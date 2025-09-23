"""
FastAPI main application for MGComputacion API
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
import json
from datetime import datetime

# Importar módulos del orquestador LLM (simulados)
from .orquestador import router_intencion, dispatcher, redactor
from .events_schema import log_event, make_event
from .tenant_loader import load_company_by_number, load_company_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="MGComputacion API",
    description="API para sistema de mensajería inteligente",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("Health check requested")
    return {"ok": True, "timestamp": datetime.now().isoformat()}

# Webhook endpoint
@app.post("/v1/chat/webhook")
async def chat_webhook(request: Request):
    """Webhook para recibir mensajes de chat"""
    try:
        body = await request.json()
        logger.info(f"Webhook received: {json.dumps(body, indent=2)}")
        
        # Extraer datos del payload
        mensaje = body.get("texto", "")
        canal = body.get("canal", "wa")
        historial = body.get("historial", [])
        session_id = body.get("session_id", f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        numero_wa = body.get("numero_wa", "+56912345678")
        
        # Cargar compañía por número de WhatsApp
        compania_id = load_company_by_number(numero_wa)
        company_config = load_company_config(compania_id)
        
        # 1. Clasificar intención
        logger.info("Clasificando intención...")
        intent_json = router_intencion.classify(
            canal=canal, 
            mensaje=mensaje, 
            historial=historial
        )
        log_event(make_event(
            tipo="intent_detected",
            session_id=session_id,
            compania_id=compania_id,
            payload={
                "intencion": intent_json["intencion"],
                "entidades": intent_json["entidades"],
                "confianza": intent_json.get("confianza", 0.0)
            }
        ))
        
        # 2. Planificar respuesta
        logger.info("Planificando respuesta...")
        decision = dispatcher.plan(
            intent_json["intencion"], 
            intent_json["entidades"]
        )
        log_event(make_event(
            tipo="module_called",
            session_id=session_id,
            compania_id=compania_id,
            payload={
                "modulo": decision["modulo"],
                "accion": decision["accion"],
                "parametros": decision["parametros"]
            }
        ))
        
        # 3. Simular datos del módulo (mock fijo)
        datos_modulo = {
            "status": "ok",
            "items": [
                {"sku": "GN125", "precio": 2990},
                {"sku": "GN250", "precio": 4500}
            ]
        }
        log_event(make_event(
            tipo="module_result",
            session_id=session_id,
            compania_id=compania_id,
            payload={
                "modulo": decision["modulo"],
                "resultado": datos_modulo,
                "exito": True
            }
        ))
        
        # 4. Generar respuesta
        logger.info("Generando respuesta...")
        texto = redactor.reply(
            intent_json["intencion"], 
            datos_modulo, 
            politicas=company_config, 
            canal=canal
        )
        
        # 5. Log de respuesta generada
        log_event(make_event(
            tipo="response_generated",
            session_id=session_id,
            compania_id=compania_id,
            payload={
                "respuesta": texto,
                "canal": canal,
                "longitud": len(texto)
            }
        ))
        
        # Responder con resultado
        return {
            "respuesta": texto,
            "debug": {
                "intent_json": intent_json,
                "decision": decision
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return {"error": "Invalid request", "status": "error"}

# Función log_event removida - ahora se usa desde events_schema.py

# Import routers
from .routers import datos, chat
from backend.webhooks.autoresponder import router as autoresponder_router

# Include routers
app.include_router(datos.router, prefix="/v1/datos", tags=["datos"])
app.include_router(chat.router, prefix="/v1/chat", tags=["chat"])
app.include_router(autoresponder_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
