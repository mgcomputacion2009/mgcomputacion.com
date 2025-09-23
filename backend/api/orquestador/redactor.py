"""
Redactor - Genera respuestas basadas en intenciones y datos
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class Redactor:
    """Generador de respuestas"""
    
    def reply(self, intencion: str, datos_modulo: Dict[str, Any], 
              politicas: Dict[str, str], canal: str) -> str:
        """
        Genera respuesta basada en intención y datos del módulo
        
        Args:
            intencion: Intención detectada
            datos_modulo: Datos devueltos por el módulo
            politicas: Políticas de respuesta (ej: CTA)
            canal: Canal de comunicación
            
        Returns:
            Texto de respuesta generado
        """
        logger.info(f"Generando respuesta para intención: {intencion}")
        
        # TODO: Implementar generación real con LLM
        # Por ahora, respuestas template basadas en intención
        
        if intencion == "consulta_precios":
            if datos_modulo.get("status") == "ok" and datos_modulo.get("items"):
                items = datos_modulo["items"]
                respuesta = "📋 Precios encontrados:\n\n"
                for item in items:
                    # Formato limpio: SKU, modelo (si hay), precio
                    sku = item.get('sku', 'N/A')
                    modelo = item.get('modelo', '')
                    precio = item.get('precio', 0)
                    
                    if modelo:
                        respuesta += f"• {sku} {modelo}: ${precio:,}\n"
                    else:
                        respuesta += f"• {sku}: ${precio:,}\n"
            else:
                respuesta = "❌ No pude encontrar precios. ¿Podrías ser más específico?"
                
        elif intencion == "crear_pedido":
            if datos_modulo.get("status") == "ok":
                respuesta = "✅ Pedido procesado!\n\n"
                respuesta += "📝 Detalles:\n"
                if datos_modulo.get("items"):
                    for item in datos_modulo["items"]:
                        sku = item.get('sku', 'N/A')
                        precio = item.get('precio', 0)
                        respuesta += f"• {sku}: ${precio:,}\n"
            else:
                respuesta = "❌ Error procesando pedido. Inténtalo de nuevo."
                
        elif intencion == "saludo":
            respuesta = "👋 ¡Hola! Soy tu asistente.\n\n"
            respuesta += "¿En qué puedo ayudarte?\n"
            respuesta += "• Consultar precios\n"
            respuesta += "• Crear pedido\n"
            respuesta += "• Información general"
            
        elif intencion == "consulta_general":
            respuesta = "🤔 ¿En qué puedo ayudarte?\n\n"
            respuesta += "Puedo ayudarte con:\n"
            respuesta += "• Consultas de precios\n"
            respuesta += "• Crear pedidos\n"
            respuesta += "• Información general"
            
        else:
            respuesta = "🤔 No estoy seguro de cómo ayudarte.\n\n"
            respuesta += "Puedo ayudarte con:\n"
            respuesta += "• Consultas de precios\n"
            respuesta += "• Crear pedidos\n"
            respuesta += "• Información general"
        
        # Limitar longitud para consulta_general
        if intencion == "consulta_general" and len(respuesta) > 300:
            respuesta = respuesta[:297] + "..."
        
        # Añadir CTA si está activa en config
        cta = politicas.get('cta', '')
        if cta == "responde 1 para seguir":
            respuesta += f"\n\n{cta}"
        elif cta and cta != "responde 1 para seguir":
            respuesta += f"\n\n{cta}"
        
        logger.info(f"Respuesta generada: {respuesta[:100]}...")
        return respuesta

# Instancia global
redactor = Redactor()
