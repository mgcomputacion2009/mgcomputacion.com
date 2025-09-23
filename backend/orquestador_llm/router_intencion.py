"""
Router de Intenciones - Clasificador de intenciones para WhatsApp
"""

import os
import re
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Configuración de logging
logger = logging.getLogger(__name__)

# Configuración desde variables de entorno
INTENT_MODEL_PRIMARY = os.getenv("INTENT_MODEL_PRIMARY", "o3-mini")
INTENT_MODEL_FALLBACK = os.getenv("INTENT_MODEL_FALLBACK", "gpt-4o")
INTENT_CONF_THRESHOLD = float(os.getenv("INTENT_CONF_THRESHOLD", "0.65"))
INTENT_MAX_TOKENS = int(os.getenv("INTENT_MAX_TOKENS", "200"))
USE_LLM = os.getenv("USE_LLM", "1") == "1"

# Lista de marcas conocidas
MARCAS_CONOCIDAS = [
    "suzuki", "yamaha", "bajaj", "honda", "kawasaki", "ktm", "ducati",
    "aprilia", "triumph", "bmw", "harley", "indian", "royal enfield"
]

def pre_extractor(mensaje: str) -> Dict[str, Any]:
    """
    Pre-extractor liviano para detectar entidades básicas sin LLM
    
    Args:
        mensaje: Mensaje del usuario
        
    Returns:
        Diccionario con entidades detectadas
    """
    mensaje_lower = mensaje.lower()
    extractores = {}
    
    # Detectar teléfono (+ dígitos 10-15)
    telefono_match = re.search(r'\+?[\d\s\-\(\)]{10,15}', mensaje)
    if telefono_match:
        extractores["telefono"] = telefono_match.group().strip()
    
    # Detectar monto (número con usd|$|bs|ves)
    monto_match = re.search(r'(\d+(?:\.\d{2})?)\s*(usd|\$|bs|ves)', mensaje_lower)
    if monto_match:
        extractores["monto"] = float(monto_match.group(1))
    
    # Detectar marca (lista conocida)
    for marca in MARCAS_CONOCIDAS:
        if marca in mensaje_lower:
            extractores["marca"] = marca
            break
    
    # Detectar modelo alfanumérico corto (GN125, EN125, etc.)
    modelo_match = re.search(r'([a-z]{2}\d{3})', mensaje_lower)
    if modelo_match:
        extractores["modelo"] = modelo_match.group(1)
    
    # Detectar nombre (palabras que empiezan con mayúscula)
    nombre_match = re.search(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+', mensaje)
    if nombre_match:
        extractores["nombre"] = nombre_match.group().strip()
    
    return extractores

    hints = _pre_extract(mensaje)
if hints.get("financia_hint"):
    # Prioridad: si el LLM duda, que tienda a FINANCIAMIENTO
    llm_bias = {"prefer_intent": "financiamiento"}
else:
    llm_bias = {}


def _llm_classify(mensaje: str, historial: List[Dict], extractores_previos: Dict[str, Any], 
                 modelo: str = INTENT_MODEL_PRIMARY) -> Dict[str, Any]:
    """
    Clasifica intención usando LLM
    
    Args:
        mensaje: Mensaje del usuario
        historial: Historial de conversación
        extractores_previos: Entidades pre-extraídas
        modelo: Modelo a usar
        
    Returns:
        Resultado de la clasificación
    """
    try:
        # Importar OpenAI solo si se necesita
        from openai import OpenAI
        
        client = OpenAI()
        
        # Construir historial resumido (últimos 3 turnos)
        historial_resumido = []
        for turno in historial[-3:]:
            historial_resumido.append({
                "intencion": turno.get("intencion", ""),
                "entidades": turno.get("entidades", {}),
                "timestamp": turno.get("timestamp", "")
            })
        
        # Construir prompt
        prompt = f"""
Eres un clasificador de intenciones para WhatsApp. Devuelve SOLO JSON válido según el esquema.

REGLAS DE PRIORIDAD:
1. datos_pago > pedido > precio > financiamiento > humano > saludo > desconocida
2. Si aparece "cuotas", "crédito", "plan", "ZAN" → financiamiento
3. Si solo es saludo breve → saludo
4. Si faltan datos clave (ej. modelo) → siguiente_accion = "preguntar_aclaracion"

MENSAJE: "{mensaje}"
HISTORIAL: {json.dumps(historial_resumido, ensure_ascii=False)}
EXTRACTORES_PREVIOS: {json.dumps(extractores_previos, ensure_ascii=False)}

ESQUEMA DE RESPUESTA:
{{
  "intencion": "precio|financiamiento|pedido|datos_pago|humano|saludo|desconocida",
  "entidades": {{
    "marca": null,
    "modelo": null,
    "telefono": null,
    "monto": null,
    "nombre": null
  }},
  "confianza": 0.0,
  "siguiente_accion": "modulo_precios|modulo_financiamiento|modulo_pedidos|modulo_sesiones|preguntar_aclaracion",
  "razonamiento_breve": ""
}}

Responde SOLO con el JSON válido, sin texto adicional.
"""
        
        # Llamada a la API
        response = client.chat.completions.create(
            model=modelo,
            messages=[
                {"role": "system", "content": "Eres un clasificador de intenciones para WhatsApp. Devuelve SOLO JSON válido."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=INTENT_MAX_TOKENS,
            temperature=0.1
        )
        
        # Extraer respuesta
        respuesta_texto = response.choices[0].message.content.strip()
        
        # Intentar parsear JSON
        try:
            resultado = json.loads(respuesta_texto)
            
            # Validar esquema básico
            if not isinstance(resultado, dict):
                raise ValueError("Respuesta no es un objeto JSON")
            
            # Asegurar campos requeridos
            resultado.setdefault("intencion", "desconocida")
            resultado.setdefault("entidades", {})
            resultado.setdefault("confianza", 0.5)
            resultado.setdefault("siguiente_accion", "preguntar_aclaracion")
            resultado.setdefault("razonamiento_breve", "")
            
            # Agregar metadatos
            resultado["_meta"] = {
                "modelo_usado": modelo,
                "timestamp": datetime.now().isoformat()
            }
            
            return resultado
            
        except json.JSONDecodeError:
            # Intentar arreglar JSON una vez
            try:
                # Buscar JSON en la respuesta
                json_match = re.search(r'\{.*\}', respuesta_texto, re.DOTALL)
                if json_match:
                    resultado = json.loads(json_match.group())
                    resultado["_meta"] = {"modelo_usado": modelo, "timestamp": datetime.now().isoformat()}
                    return resultado
            except:
                pass
            
            # Si falla, usar fallback
            return _mock_classify(mensaje, extractores_previos)
            
    except Exception as e:
        logger.error(f"Error en LLM classify: {str(e)}")
        return _mock_classify(mensaje, extractores_previos)

def _mock_classify(mensaje: str, extractores_previos: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clasificación mock usando reglas heurísticas
    
    Args:
        mensaje: Mensaje del usuario
        extractores_previos: Entidades pre-extraídas
        
    Returns:
        Resultado de la clasificación mock
    """
    mensaje_lower = mensaje.lower()
    
    # Detectar intención por palabras clave
    if any(word in mensaje_lower for word in ["cuotas", "crédito", "plan", "zan"]):
        intencion = "financiamiento"
        siguiente_accion = "modulo_financiamiento"
        confianza = 0.7
        razonamiento = "Detectado financiamiento por palabras clave"
    elif any(word in mensaje_lower for word in ["precio", "costo", "cuanto", "vale"]):
        intencion = "precio"
        siguiente_accion = "modulo_precios"
        confianza = 0.7
        razonamiento = "Detectado precio por palabras clave"
    elif any(word in mensaje_lower for word in ["comprar", "pedido", "orden", "quiero"]):
        intencion = "pedido"
        siguiente_accion = "modulo_pedidos"
        confianza = 0.7
        razonamiento = "Detectado pedido por palabras clave"
    elif any(word in mensaje_lower for word in ["pago", "deposito", "cuenta", "tarjeta"]):
        intencion = "datos_pago"
        siguiente_accion = "modulo_sesiones"
        confianza = 0.7
        razonamiento = "Detectado datos de pago por palabras clave"
    elif any(word in mensaje_lower for word in ["hola", "buenos", "saludo", "ayuda"]):
        intencion = "saludo"
        siguiente_accion = "preguntar_aclaracion"
        confianza = 0.4
        razonamiento = "Detectado saludo por palabras clave"
    else:
        intencion = "desconocida"
        siguiente_accion = "preguntar_aclaracion"
        confianza = 0.3
        razonamiento = "No se pudo clasificar, usando desconocida"
    
    # Construir entidades
    entidades = {
        "marca": extractores_previos.get("marca"),
        "modelo": extractores_previos.get("modelo"),
        "telefono": extractores_previos.get("telefono"),
        "monto": extractores_previos.get("monto"),
        "nombre": extractores_previos.get("nombre")
    }
    
    return {
        "intencion": intencion,
        "entidades": entidades,
        "confianza": confianza,
        "siguiente_accion": siguiente_accion,
        "razonamiento_breve": razonamiento,
        "_meta": {
            "modelo_usado": "mock",
            "timestamp": datetime.now().isoformat()
        }
    }

def classify(canal: str, mensaje: str, historial: Optional[List] = None, 
            extractores_previos: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Clasifica la intención de un mensaje
    
    Args:
        canal: Canal de comunicación (ej: "wa")
        mensaje: Mensaje del usuario
        historial: Historial de conversación (opcional)
        extractores_previos: Entidades pre-extraídas (opcional)
        
    Returns:
        Diccionario con la clasificación según el esquema
        
    Examples:
        >>> classify("wa", "precio de la suzuki gn125")
        {'intencion': 'precio', 'entidades': {'marca': 'suzuki', 'modelo': 'gn125'}, 'confianza': 0.7, 'siguiente_accion': 'modulo_precios', 'razonamiento_breve': '...'}
        
        >>> classify("wa", "quiero plan zan para moto 250")
        {'intencion': 'financiamiento', 'entidades': {'marca': None, 'modelo': '250'}, 'confianza': 0.8, 'siguiente_accion': 'modulo_financiamiento', 'razonamiento_breve': '...'}
        
        >>> classify("wa", "a qué cuenta deposito?")
        {'intencion': 'datos_pago', 'entidades': {}, 'confianza': 0.6, 'siguiente_accion': 'modulo_sesiones', 'razonamiento_breve': '...'}
        
        >>> classify("wa", "hola")
        {'intencion': 'saludo', 'entidades': {}, 'confianza': 0.4, 'siguiente_accion': 'preguntar_aclaracion', 'razonamiento_breve': '...'}
    """
    try:
        # Normalizar parámetros
        historial = historial or []
        extractores_previos = extractores_previos or {}
        
        # Pre-extraer entidades
        extractores = pre_extractor(mensaje)
        extractores_previos.update(extractores)
        
        # Si no usar LLM, usar mock
        if not USE_LLM:
            return _mock_classify(mensaje, extractores_previos)
        
        # Intentar clasificación con LLM
        resultado = _llm_classify(mensaje, historial, extractores_previos, INTENT_MODEL_PRIMARY)
        
        # Si confianza es baja, intentar con modelo fallback
        if resultado.get("confianza", 0) < INTENT_CONF_THRESHOLD:
            logger.info(f"Confianza baja ({resultado.get('confianza', 0)}), intentando con modelo fallback")
            resultado_fallback = _llm_classify(mensaje, historial, extractores_previos, INTENT_MODEL_FALLBACK)
            
            if resultado_fallback.get("confianza", 0) > resultado.get("confianza", 0):
                resultado = resultado_fallback
        
        # Mapear intención a siguiente_accion
        intencion = resultado.get("intencion", "desconocida")
        if intencion == "precio":
            resultado["siguiente_accion"] = "modulo_precios"
        elif intencion == "financiamiento":
            resultado["siguiente_accion"] = "modulo_financiamiento"
        elif intencion == "pedido":
            resultado["siguiente_accion"] = "modulo_pedidos"
        elif intencion in ["datos_pago", "humano"]:
            resultado["siguiente_accion"] = "modulo_sesiones"
        else:
            resultado["siguiente_accion"] = "preguntar_aclaracion"
        
        # Si confianza es baja, cambiar siguiente_accion
        if resultado.get("confianza", 0) < INTENT_CONF_THRESHOLD:
            resultado["siguiente_accion"] = "preguntar_aclaracion"
            resultado["razonamiento_breve"] = "Confianza baja, requiere aclaración"
        
        return resultado
        
    except Exception as e:
        logger.error(f"Error en classify: {str(e)}")
        return _mock_classify(mensaje, extractores_previos or {})

def debug_prompt(mensaje: str, historial: List[Dict] = None, extractores_previos: Dict = None) -> str:
    """
    Función de debug que devuelve el prompt construido para auditoría
    
    Args:
        mensaje: Mensaje del usuario
        historial: Historial de conversación
        extractores_previos: Entidades pre-extraídas
        
    Returns:
        Prompt construido para el LLM
    """
    historial = historial or []
    extractores_previos = extractores_previos or {}
    
    historial_resumido = []
    for turno in historial[-3:]:
        historial_resumido.append({
            "intencion": turno.get("intencion", ""),
            "entidades": turno.get("entidades", {}),
            "timestamp": turno.get("timestamp", "")
        })
    
    return f"""
Eres un clasificador de intenciones para WhatsApp. Devuelve SOLO JSON válido según el esquema.

REGLAS DE PRIORIDAD:
1. datos_pago > pedido > precio > financiamiento > humano > saludo > desconocida
2. Si aparece "cuotas", "crédito", "plan", "ZAN" → financiamiento
3. Si solo es saludo breve → saludo
4. Si faltan datos clave (ej. modelo) → siguiente_accion = "preguntar_aclaracion"

MENSAJE: "{mensaje}"
HISTORIAL: {json.dumps(historial_resumido, ensure_ascii=False)}
EXTRACTORES_PREVIOS: {json.dumps(extractores_previos, ensure_ascii=False)}

ESQUEMA DE RESPUESTA:
{{
  "intencion": "precio|financiamiento|pedido|datos_pago|humano|saludo|desconocida",
  "entidades": {{
    "marca": null,
    "modelo": null,
    "telefono": null,
    "monto": null,
    "nombre": null
  }},
  "confianza": 0.0,
  "siguiente_accion": "modulo_precios|modulo_financiamiento|modulo_pedidos|modulo_sesiones|preguntar_aclaracion",
  "razonamiento_breve": ""
}}

Responde SOLO con el JSON válido, sin texto adicional.
"""

# Tests mínimos
if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
    
    # Tests adicionales
    print("\n=== Tests Adicionales ===")
    
    # Test 1: Precio
    result1 = classify("wa", "precio de la suzuki gn125")
    print(f"Test 1 - Precio: {result1['intencion']} -> {result1['siguiente_accion']} (confianza: {result1['confianza']})")
    
    # Test 2: Financiamiento
    result2 = classify("wa", "quiero plan zan para moto 250")
    print(f"Test 2 - Financiamiento: {result2['intencion']} -> {result2['siguiente_accion']} (confianza: {result2['confianza']})")
    
    # Test 3: Datos de pago
    result3 = classify("wa", "a qué cuenta deposito?")
    print(f"Test 3 - Datos pago: {result3['intencion']} -> {result3['siguiente_accion']} (confianza: {result3['confianza']})")
    
    # Test 4: Saludo
    result4 = classify("wa", "hola")
    print(f"Test 4 - Saludo: {result4['intencion']} -> {result4['siguiente_accion']} (confianza: {result4['confianza']})")
    
    print("\n=== Tests Completados ===")

FINANCIA_TERMS = [
    "plan", "zan", "cuota", "cuotas", "financiar", "financiamiento",
    "credito", "crédito", "mensualidad", "plazo", "abono"
]

def _pre_extract(mensaje: str) -> dict:
    m = mensaje.lower()
    hay_financia = any(t in m for t in FINANCIA_TERMS)
    # ... tu detección de marca/modelo/teléfono/monto ...
    return {
        "marca": marca or None,
        "modelo": modelo or None,
        "telefono": telefono or None,
        "monto": monto or None,
        "financia_hint": bool(hay_financia),
    }
