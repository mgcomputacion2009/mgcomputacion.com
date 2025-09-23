"""
Dispatcher - Planifica acciones basadas en intenciones
"""

import logging
from typing import Dict, Any, Optional
from ..tenant_loader import load_company_config_by_id

logger = logging.getLogger(__name__)

class Dispatcher:
    """Planificador de acciones basado en intenciones"""
    
    def plan(self, intencion: str, entidades: Dict[str, Any]) -> Dict[str, Any]:
        """
        Planifica la acción a tomar basada en la intención detectada
        
        Args:
            intencion: Intención detectada
            entidades: Entidades extraídas del mensaje
            
        Returns:
            Dict con módulo, acción y parámetros
        """
        logger.info(f"Planificando acción para intención: {intencion}")
        
        # TODO: Implementar lógica de planificación real
        # Por ahora, mapeo simple de intenciones a módulos
        
        if intencion == "consulta_precios":
            return {
                "modulo": "precios",
                "accion": "consultar",
                "parametros": {
                    "tipo": entidades.get("tipo", "general"),
                    "producto": entidades.get("producto", "general")
                },
                "prioridad": "alta"
            }
        elif intencion == "crear_pedido":
            return {
                "modulo": "pedidos",
                "accion": "crear",
                "parametros": {
                    "accion": entidades.get("accion", "comprar"),
                    "producto": entidades.get("producto", "general")
                },
                "prioridad": "alta"
            }
        elif intencion == "saludo":
            return {
                "modulo": "sistema",
                "accion": "saludar",
                "parametros": {
                    "tipo": entidades.get("tipo", "saludo")
                },
                "prioridad": "media"
            }
        else:
            return {
                "modulo": "sistema",
                "accion": "consulta_general",
                "parametros": {
                    "tipo": "general"
                },
                "prioridad": "baja"
            }
    
    def procesar_mensaje(self, numero: str, texto: str, canal: str, meta: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa un mensaje del orquestador LLM
        
        Args:
            numero: Número de teléfono del cliente
            texto: Texto del mensaje
            canal: Canal de comunicación (wa, web, etc.)
            meta: Metadatos adicionales (incluye compania_id si está disponible)
            
        Returns:
            Diccionario con resultado del procesamiento
        """
        try:
            logger.info(f"Procesando mensaje - Número: {numero}, Canal: {canal}")
            
            # Cargar configuración de compañía si está disponible
            compania_id = meta.get("compania_id")
            company_config = None
            
            if compania_id:
                logger.info(f"Cargando configuración para compañía: {compania_id}")
                company_config = load_company_config_by_id(compania_id)
                logger.info(f"Configuración cargada: {company_config.get('cta', 'N/A')}")
            else:
                logger.info("No se proporcionó compania_id, usando configuración por defecto")
                company_config = {
                    "cta": "responde 1 para seguir",
                    "prompts_version": "v1",
                    "modo_venta": "activo"
                }
            
            # Simular procesamiento
            if not texto or not numero:
                return {
                    "ok": False,
                    "error": "invalid_input"
                }
            
            # Generar respuesta simulada con configuración de compañía
            cta = company_config.get("cta", "responde 1 para seguir")
            reply = f"Respuesta simulada para: {texto[:50]}...\n\n{cta}"
            
            # Log de metadatos incluyendo compania_id
            logger.info(f"Meta recibida: {meta}")
            logger.info(f"Compañía ID: {compania_id}")
            logger.info(f"Configuración aplicada: {company_config.get('cta', 'N/A')}")
            
            return {
                "ok": True,
                "reply": reply,
                "meta": {
                    "numero": numero,
                    "canal": canal,
                    "compania_id": compania_id,
                    "company_config": company_config,
                    "ar_device": meta.get("ar_device"),
                    "rule_id": meta.get("rule_id")
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
