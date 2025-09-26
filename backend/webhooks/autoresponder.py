"""
Webhook de AutoResponder para WhatsApp
"""

import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, Header, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field

from ..db.tenant_repo import tenant_repo
from ..api.utils.security import verify_hmac
from ..api.utils.rate_limit import allow as rl_allow
from ..db.events_repo import events_repo
from ..api.orquestador.dispatcher import dispatcher

logger = logging.getLogger(__name__)

# Router para webhooks
router = APIRouter(prefix="/v1/wa", tags=["webhooks"])


def ensure_session(compania_id: int, device_alias: str, session_key: str) -> str:
    """
    Crea/obtiene un identificador de sesión estable para el cliente.
    Implementación simple basada en hash; reemplazar por DAO persistente si se requiere.
    """
    import hashlib
    base = f"{compania_id}|{device_alias or ''}|{session_key or ''}"
    sid = hashlib.sha256(base.encode("utf-8")).hexdigest()[:32]
    return sid

class AutoResponderPayload(BaseModel):
    """Payload del webhook de AutoResponder"""
    rule_id: Optional[str] = Field(None, description="ID de la regla que activó el webhook")
    message: Optional[str] = Field(None, description="Mensaje recibido")
    phone: Optional[str] = Field(None, description="Número de teléfono del cliente")
    sender: Optional[str] = Field(None, description="Remitente del mensaje")
    chat_id: Optional[str] = Field(None, description="ID del chat")
    account: Optional[str] = Field(None, description="Cuenta de WhatsApp Business")
    extras: Optional[Dict[str, Any]] = Field(None, description="Datos adicionales")

@router.post("/autoresponder")
async def autoresponder_webhook(
    body: AutoResponderPayload,
    request: Request,
    x_ar_device: str = Header(None, alias="X-AR-Device"),
    x_ar_token: str = Header(None, alias="X-AR-Token"),
    x_ar_signature: str = Header(None, alias="X-AR-Signature"),
):
    """
    Webhook de AutoResponder para WhatsApp
    
    Headers requeridos:
    - X-AR-Device: Alias del dispositivo
    - X-AR-Token: Token del dispositivo
    
    Body: AutoResponderPayload con datos del mensaje
    """
    try:
        # Normalización de payload (soporta envoltorios y estilos camel/snake)
        try:
            raw = await request.json()
        except Exception:
            raw = {}
        data = raw or {}
        q = data.get("query") or data

        rule_id = str(q.get("rule_id") or q.get("ruleId") or "").strip()
        message = (q.get("message") or (body.message or "")).strip()
        phone = str(q.get("phone") or q.get("senderPhone") or (body.phone or "")).strip()
        sender = (q.get("sender") or (body.sender or "")).strip()

        app_pkg = data.get("appPackageName") or q.get("appPackageName")
        msg_pkg = data.get("messengerPackageName") or q.get("messengerPackageName")

        # --- extrae remitente real (cliente) ---
        headers = {k.lower(): v for k, v in request.headers.items()} if request and request.headers else {}
        sender_raw = (
            headers.get('x-ar-sender') or
            data.get('sender') or
            (data.get('query') or {}).get('sender') or
            sender or ''
        )
        import re as _re
        sender_digits = _re.sub(r"\D", "", sender_raw or "")  # solo números
        if sender_digits.startswith('0'):
            sender_digits = sender_digits.lstrip('0')
        # rango aceptado: 7 a 15 dígitos (E.164 sin '+')
        cliente_numero = sender_digits if 7 <= len(sender_digits) <= 15 else None
        # si no viene phone en el payload, usar el número extraído del sender
        if not phone and cliente_numero:
            phone = cliente_numero
        cliente_nombre = (sender_raw or "").strip() or None

        if not message:
            return JSONResponse(status_code=400, content={"ok": False, "error": "invalid_input"})

        logger.info(f"[AR] recv device={x_ar_device} msg_len={len(message or '')} phone={phone}")

        # Rate limit por IP
        import os
        client_ip = request.client.host if request and request.client else "unknown"
        max_ip = int(os.getenv("RL_MAX_PER_IP", "60"))
        if not rl_allow(f"ip:{client_ip}", max_ip, 60):
            logger.warning(f"[AR] rate_limit ip={client_ip}")
            return JSONResponse(status_code=429, content={"ok": False, "error": "rate_limited"})
        
        # 1) Buscar compañía por dispositivo y token
        cid = None
        if x_ar_device and x_ar_token:
            cid = tenant_repo.get_compania_id_by_device(x_ar_device, x_ar_token)
        
        # 2) Si no se encuentra y hay phone, buscar por cliente
        if not cid and phone:
            logger.info(f"Buscando compañía por cliente: {phone}")
            cid = tenant_repo.get_compania_id_by_cliente(phone)
        
        # 3) Log de resolución y validación
        if cid:
            logger.info(f"[AR] tenant cid={cid} device={x_ar_device}")
        else:
            logger.warning(f"[AR] tenant_unauthorized device={x_ar_device} phone={phone}")
            return JSONResponse(
                status_code=401,
                content={"ok": False, "error": "tenant_unauthorized"}
            )

        # Verificación opcional de firma HMAC
        VERIFY = os.getenv("VERIFY_SIGNATURE", "false").lower() in ("1", "true", "yes")
        if VERIFY and cid:
            try:
                secret = tenant_repo.get_secret(cid)
                sig = x_ar_signature
                if not secret or not sig:
                    logger.warning("[AR] bad_signature: faltante secreto o firma")
                    return JSONResponse(status_code=401, content={"ok": False, "error": "bad_signature"})
                body_raw = await request.body()
                if not verify_hmac(body_raw, sig, secret):
                    logger.warning("[AR] firma inválida")
                    return JSONResponse(status_code=401, content={"ok": False, "error": "bad_signature"})
                logger.info("[AR] firma válida")
            except Exception as e:
                logger.error(f"[AR] error verificando firma: {e}")
                return JSONResponse(status_code=401, content={"ok": False, "error": "bad_signature"})

        # Rate limit básico en memoria (TTL 60s)
        try:
            max_tenant = int(os.getenv("RL_MAX_PER_TENANT", "120"))
            if cid and not rl_allow(f"tenant:{cid}", max_tenant, 60):
                logger.warning(f"[AR] rate_limit tenant cid={cid}")
                return JSONResponse(status_code=429, content={"ok": False, "error": "rate_limited"})
        except Exception as e:
            logger.error(f"[AR] error en rate_limit: {e}")
        
        # 4) Construir meta con datos del webhook (incluir config de compañía)
        company_config = tenant_repo.get_company_config(cid)
        meta = {
            "numero": phone,
            "canal": "wa",
            "compania_id": cid,
            "ar_device": x_ar_device,
            "rule_id": rule_id or body.rule_id,
            "sender": sender or body.sender,
            "account": body.account,
            "chat_id": body.chat_id,
            "company_config": company_config,
            "appPackageName": app_pkg,
            "messengerPackageName": msg_pkg,
        }
        # cliente normalizado y sesión
        meta['cliente'] = {"numero": cliente_numero, "nombre": cliente_nombre}
        session_key = cliente_numero or (cliente_nombre or 'desconocido')
        session_id = ensure_session(cid, x_ar_device or '', session_key)
        meta['session_id'] = session_id

        # Registrar evento de entrada (resumen)
        try:
            summary = {
                "msg_len": len(message or ""),
                "phone": phone,
                "device": x_ar_device,
            }
            events_repo.log_event(cid, session_id, "webhook_in", summary)
        except Exception:
            logger.warning("[AR] no se pudo registrar evento webhook_in")
        
        # 5) Llamar al dispatcher
        logger.info(f"Procesando mensaje con dispatcher - Phone: {body.phone}")
        resultado = dispatcher.procesar_mensaje(
            numero=phone,
            texto=message,
            canal="wa",
            meta=meta
        )
        
        # 6) Responder con resultado (formato oficial: objeto con 'replies' de objetos)
        if resultado and resultado.get("ok"):
            reply = resultado.get("reply", "")
            logger.info(f"[AR] reply cid={cid} chars={len(reply or '')}")
            # Registrar evento de salida
            try:
                events_repo.log_event(cid, session_id, "response_generated", {"len": len(reply or "")})
            except Exception:
                logger.warning("[AR] no se pudo registrar evento response_generated")
            # Responder como objeto con arreglo 'replies' y objetos {message, queued}
            return JSONResponse(content={
                "replies": [
                    {
                        "message": reply,
                        "queued": True
                    }
                ]
            })
        else:
            error_msg = resultado.get("error", "unknown_error") if resultado else "dispatcher_error"
            logger.error(f"Error en dispatcher: {error_msg}")
            # Responder con objeto y arreglo vacío para compatibilidad
            return JSONResponse(content={
                "replies": [],
                "queued": False
            }, status_code=400)
            
    except Exception as e:
        logger.error(f"Error inesperado en webhook AutoResponder: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": str(e)}
        )

@router.get("/autoresponder/health")
async def autoresponder_health():
    """
    Health check del webhook de AutoResponder
    """
    return {
        "ok": True,
        "service": "autoresponder_webhook",
        "status": "healthy"
    }

@router.get("/outbox/status")
async def outbox_status():
    """
    Endpoint para verificar el estado del outbox (requerido por AutoResponder)
    """
    return {
        "ok": True,
        "status": "active",
        "message": "Outbox service is running"
    }

@router.get("/_debug/resolve")
async def debug_resolve_tenant(
    device: Optional[str] = None,
    token: Optional[str] = None,
    phone: Optional[str] = None
):
    """
    DEBUG ONLY: disable in prod
    Endpoint de debug para probar resolución de tenant
    
    Query params:
    - device: Alias del dispositivo
    - token: Token del dispositivo
    - phone: Número de teléfono del cliente
    """
    logger.info(f"[DEBUG] Resolviendo tenant - device={device} token={'***' if token else None} phone={phone}")
    
    cid = None
    
    # 1) Intentar resolución por dispositivo
    if device and token:
        logger.info(f"[DEBUG] Intentando resolución por dispositivo: {device}")
        cid = tenant_repo.get_compania_id_by_device(device, token)
        if cid:
            logger.info(f"[DEBUG] Tenant resuelto por dispositivo: cid={cid}")
        else:
            logger.info(f"[DEBUG] Dispositivo no encontrado: {device}")
    
    # 2) Si no se encontró, intentar por teléfono
    if not cid and phone:
        logger.info(f"[DEBUG] Intentando resolución por teléfono: {phone}")
        cid = tenant_repo.get_compania_id_by_cliente(phone)
        if cid:
            logger.info(f"[DEBUG] Tenant resuelto por teléfono: cid={cid}")
        else:
            logger.info(f"[DEBUG] Teléfono no encontrado: {phone}")
    
    result = {
        "cid": cid,
        "device": device,
        "phone": phone,
        "ok": cid is not None,
        "method": "device" if device and token and cid else "phone" if phone and cid else "none"
    }
    
    logger.info(f"[DEBUG] Resultado: {result}")
    return result

# DEBUG ONLY: restringir por auth en producción
@router.get("/../ops/eventos")
async def debug_list_eventos(compania_id: Optional[int] = None, limit: int = 50):
    """
    DEBUG ONLY: listar eventos recientes por compañía.
    """
    try:
        data = events_repo.list_events(compania_id, limit)
        return {"ok": True, "items": data}
    except Exception as e:
        logger.error(f"[OPS] error listando eventos: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": "list_error"})
