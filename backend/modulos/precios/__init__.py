"""
Módulo de precios - Funciones para consulta de precios
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

def mock_buscar(marca: Optional[str] = None, modelo: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Mock de búsqueda de precios
    
    Args:
        marca: Marca del producto (opcional)
        modelo: Modelo del producto (opcional)
        
    Returns:
        Lista de productos con precios
    """
    logger.info(f"Mock buscar precios - marca: {marca}, modelo: {modelo}")
    
    # Datos mock fijos
    productos = [
        {
            "sku": "GN125",
            "nombre": "Guitarra Acústica GN125",
            "marca": "GuitarNova",
            "modelo": "GN125",
            "precio": 2990,
            "disponible": True,
            "categoria": "guitarras"
        },
        {
            "sku": "GN250",
            "nombre": "Guitarra Eléctrica GN250",
            "marca": "GuitarNova", 
            "modelo": "GN250",
            "precio": 4500,
            "disponible": True,
            "categoria": "guitarras"
        }
    ]
    
    # Filtrar por marca si se especifica
    if marca:
        productos = [p for p in productos if p["marca"].lower() == marca.lower()]
    
    # Filtrar por modelo si se especifica
    if modelo:
        productos = [p for p in productos if p["modelo"].lower() == modelo.lower()]
    
    logger.info(f"Mock retornando {len(productos)} productos")
    return productos

def consultar_precios(tipo: str = "general", producto: str = "general") -> Dict[str, Any]:
    """
    Consulta de precios principal
    
    Args:
        tipo: Tipo de consulta
        producto: Producto específico
        
    Returns:
        Resultado de la consulta
    """
    logger.info(f"Consultando precios - tipo: {tipo}, producto: {producto}")
    
    # Usar mock para búsqueda
    items = mock_buscar()
    
    return {
        "status": "ok",
        "items": items,
        "total": len(items),
        "filtros": {
            "tipo": tipo,
            "producto": producto
        }
    }
