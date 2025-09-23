"""
Módulo de pedidos - Funciones para gestión de pedidos
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

def mock_crear_pedido(items: List[Dict[str, Any]], cliente_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Mock de creación de pedido
    
    Args:
        items: Lista de items del pedido
        cliente_id: ID del cliente (opcional)
        
    Returns:
        Pedido creado con datos mock
    """
    logger.info(f"Mock crear pedido - items: {len(items)}, cliente: {cliente_id}")
    
    # Generar código de pedido mock
    codigo_pedido = f"PED-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Calcular total
    total = sum(item.get("precio", 0) * item.get("cantidad", 1) for item in items)
    
    # Pedido mock
    pedido = {
        "codigo_pedido": codigo_pedido,
        "cliente_id": cliente_id or "CLI-MOCK-001",
        "items": items,
        "total": total,
        "estado": "pendiente",
        "fecha_creacion": datetime.now().isoformat(),
        "metodo_pago": "por_definir",
        "direccion_entrega": "por_definir"
    }
    
    logger.info(f"Mock pedido creado: {codigo_pedido} - Total: ${total}")
    return pedido

def crear_pedido(accion: str = "comprar", producto: str = "general") -> Dict[str, Any]:
    """
    Creación de pedido principal
    
    Args:
        accion: Acción del pedido
        producto: Producto específico
        
    Returns:
        Resultado de la creación
    """
    logger.info(f"Creando pedido - accion: {accion}, producto: {producto}")
    
    # Items mock basados en el producto
    if producto == "general":
        items = [
            {"sku": "GN125", "nombre": "Guitarra Acústica GN125", "precio": 2990, "cantidad": 1},
            {"sku": "GN250", "nombre": "Guitarra Eléctrica GN250", "precio": 4500, "cantidad": 1}
        ]
    else:
        items = [
            {"sku": producto, "nombre": f"Producto {producto}", "precio": 2000, "cantidad": 1}
        ]
    
    # Usar mock para crear pedido
    pedido = mock_crear_pedido(items)
    
    return {
        "status": "ok",
        "pedido": pedido,
        "accion": accion,
        "producto": producto
    }

def consultar_pedido(codigo_pedido: str) -> Dict[str, Any]:
    """
    Consulta de pedido por código
    
    Args:
        codigo_pedido: Código del pedido
        
    Returns:
        Detalles del pedido
    """
    logger.info(f"Consultando pedido: {codigo_pedido}")
    
    # Mock de pedido existente
    pedido_mock = {
        "codigo_pedido": codigo_pedido,
        "cliente_id": "CLI-MOCK-001",
        "items": [
            {"sku": "GN125", "nombre": "Guitarra Acústica GN125", "precio": 2990, "cantidad": 1}
        ],
        "total": 2990,
        "estado": "pendiente",
        "fecha_creacion": "2025-09-23T04:00:00Z",
        "metodo_pago": "por_definir",
        "direccion_entrega": "por_definir"
    }
    
    return {
        "status": "ok",
        "pedido": pedido_mock
    }
