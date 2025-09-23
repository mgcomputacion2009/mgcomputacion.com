"""
Router de intenciones - Clasifica mensajes y detecta intenciones
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class RouterIntencion:
    """Clasificador de intenciones"""
    
    def classify(self, canal: str, mensaje: str, historial: List[Dict]) -> Dict[str, Any]:
        """
        Clasifica un mensaje y detecta la intención
        
        Args:
            canal: Canal de comunicación (wa, web, etc.)
            mensaje: Texto del mensaje
            historial: Historial de conversación
            
        Returns:
            Dict con intención, entidades y confianza
        """
        logger.info(f"Clasificando mensaje: '{mensaje}' en canal {canal}")
        
        # TODO: Implementar clasificación real con LLM
        # Por ahora, simulación basada en palabras clave
        
        mensaje_lower = mensaje.lower()
        
        # Detectar intención basada en palabras clave
        if any(word in mensaje_lower for word in ['precio', 'costo', 'cuanto', 'cotizar']):
            intencion = "consulta_precios"
            entidades = {"tipo": "precio", "producto": "general"}
            confianza = 0.85
        elif any(word in mensaje_lower for word in ['comprar', 'pedido', 'orden', 'quiero']):
            intencion = "crear_pedido"
            entidades = {"accion": "comprar", "producto": "general"}
            confianza = 0.80
        elif any(word in mensaje_lower for word in ['hola', 'buenos', 'saludo', 'ayuda']):
            intencion = "saludo"
            entidades = {"tipo": "saludo"}
            confianza = 0.90
        else:
            intencion = "consulta_general"
            entidades = {"tipo": "general"}
            confianza = 0.60
        
        return {
            "intencion": intencion,
            "entidades": entidades,
            "confianza": confianza,
            "canal": canal,
            "mensaje_original": mensaje
        }

# Instancia global
router_intencion = RouterIntencion()
