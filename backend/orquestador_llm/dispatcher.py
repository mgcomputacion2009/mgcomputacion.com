"""
Dispatcher - Procesador de mensajes del orquestador LLM
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class Dispatcher:
    """Procesador de mensajes del orquestador LLM"""
    
    def procesar_mensaje(self, numero: str, texto: str, canal: str, meta: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa un mensaje del orquestador LLM
        
        Args:
            numero: Número de teléfono del cliente
            texto: Texto del mensaje
            canal: Canal de comunicación (wa, web, etc.)
            meta: Metadatos adicionales
            
        Returns:
            Diccionario con resultado del procesamiento
        """
        try:
            logger.info(f"Procesando mensaje - Número: {numero}, Canal: {canal}")
            
            # TODO: Implementar procesamiento real del mensaje
            # Por ahora, simulación básica
            
            # Simular procesamiento
            if not texto or not numero:
                return {
                    "ok": False,
                    "error": "invalid_input"
                }
            
            # Generar respuesta simulada
            reply = f"Respuesta simulada para: {texto[:50]}..."
            
            # Log de metadatos
            logger.info(f"Meta recibida: {meta}")
            
            return {
                "ok": True,
                "reply": reply,
                "meta": {
                    "numero": numero,
                    "canal": canal,
                    "compania_id": meta.get("compania_id"),
                    "ar_device": meta.get("ar_device")
                }
            }
            
        except Exception as e:
            logger.error(f"Error procesando mensaje: {str(e)}")
            return {
                "ok": False,
                "error": "processing_error"
            }

# Instancia global
dispatcher = Dispatcher()
