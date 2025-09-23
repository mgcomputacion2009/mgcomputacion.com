"""
Schema y helpers para eventos del sistema
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def log_event(evt: dict) -> None:
    """
    Guarda evento en archivo de log y hace print seguro
    
    Args:
        evt: Diccionario con datos del evento
    """
    try:
        # Agregar timestamp si no existe
        if "timestamp" not in evt:
            evt["timestamp"] = datetime.now().isoformat()
        
        # Convertir a JSON
        event_json = json.dumps(evt, ensure_ascii=False, indent=2)
        
        # Guardar en archivo de log
        with open("/tmp/events.log", "a", encoding="utf-8") as f:
            f.write(event_json + "\n" + "-" * 80 + "\n")
        
        # Print seguro (solo campos no sensibles)
        safe_event = {
            "tipo": evt.get("tipo", "unknown"),
            "session_id": evt.get("session_id", "N/A"),
            "compania_id": evt.get("compania_id", "N/A"),
            "timestamp": evt.get("timestamp", "N/A")
        }
        
        logger.info(f"EVENT LOGGED: {json.dumps(safe_event, ensure_ascii=False)}")
        
    except Exception as e:
        logger.error(f"Error logging event: {str(e)}")
        # Fallback: solo print del error
        print(f"ERROR LOGGING EVENT: {str(e)}")

def make_event(tipo: str, session_id: str, compania_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Crea evento con estructura estándar
    
    Args:
        tipo: Tipo de evento
        session_id: ID de la sesión
        compania_id: ID de la compañía
        payload: Datos adicionales del evento
        
    Returns:
        Diccionario con estructura de evento
    """
    return {
        "tipo": tipo,
        "session_id": session_id,
        "compania_id": compania_id,
        "timestamp": datetime.now().isoformat(),
        "payload": payload
    }

def log_intent_detected(session_id: str, compania_id: str, intencion: str, entidades: Dict[str, Any], confianza: float) -> None:
    """
    Helper específico para eventos de intención detectada
    
    Args:
        session_id: ID de la sesión
        compania_id: ID de la compañía
        intencion: Intención detectada
        entidades: Entidades extraídas
        confianza: Nivel de confianza
    """
    event = make_event(
        tipo="intent_detected",
        session_id=session_id,
        compania_id=compania_id,
        payload={
            "intencion": intencion,
            "entidades": entidades,
            "confianza": confianza
        }
    )
    log_event(event)

def log_module_called(session_id: str, compania_id: str, modulo: str, accion: str, parametros: Dict[str, Any]) -> None:
    """
    Helper específico para eventos de módulo llamado
    
    Args:
        session_id: ID de la sesión
        compania_id: ID de la compañía
        modulo: Módulo llamado
        accion: Acción ejecutada
        parametros: Parámetros enviados
    """
    event = make_event(
        tipo="module_called",
        session_id=session_id,
        compania_id=compania_id,
        payload={
            "modulo": modulo,
            "accion": accion,
            "parametros": parametros
        }
    )
    log_event(event)

def log_module_result(session_id: str, compania_id: str, modulo: str, resultado: Dict[str, Any], exito: bool) -> None:
    """
    Helper específico para eventos de resultado de módulo
    
    Args:
        session_id: ID de la sesión
        compania_id: ID de la compañía
        modulo: Módulo que retornó resultado
        resultado: Resultado del módulo
        exito: Si la operación fue exitosa
    """
    event = make_event(
        tipo="module_result",
        session_id=session_id,
        compania_id=compania_id,
        payload={
            "modulo": modulo,
            "resultado": resultado,
            "exito": exito
        }
    )
    log_event(event)

def log_response_generated(session_id: str, compania_id: str, respuesta: str, canal: str) -> None:
    """
    Helper específico para eventos de respuesta generada
    
    Args:
        session_id: ID de la sesión
        compania_id: ID de la compañía
        respuesta: Texto de respuesta generado
        canal: Canal de comunicación
    """
    event = make_event(
        tipo="response_generated",
        session_id=session_id,
        compania_id=compania_id,
        payload={
            "respuesta": respuesta,
            "canal": canal,
            "longitud": len(respuesta)
        }
    )
    log_event(event)
