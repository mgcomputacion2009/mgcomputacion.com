"""
Módulo de financiamiento - Funciones para opciones de pago
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

def mock_calcular_cuotas(monto: float, plazo_meses: int = 12) -> List[Dict[str, Any]]:
    """
    Mock de cálculo de cuotas de financiamiento
    
    Args:
        monto: Monto a financiar
        plazo_meses: Plazo en meses (opcional, default 12)
        
    Returns:
        Lista de opciones de financiamiento
    """
    logger.info(f"Mock calcular cuotas - monto: {monto}, plazo: {plazo_meses} meses")
    
    # Opciones mock fijas
    opciones = [
        {
            "plazo_meses": 6,
            "cuota_mensual": round(monto / 6, 2),
            "interes_total": round(monto * 0.05, 2),
            "total_pagar": round(monto * 1.05, 2),
            "tasa_interes": 5.0,
            "disponible": True
        },
        {
            "plazo_meses": 12,
            "cuota_mensual": round(monto / 12, 2),
            "interes_total": round(monto * 0.10, 2),
            "total_pagar": round(monto * 1.10, 2),
            "tasa_interes": 10.0,
            "disponible": True
        }
    ]
    
    # Filtrar por plazo si se especifica
    if plazo_meses:
        opciones = [o for o in opciones if o["plazo_meses"] == plazo_meses]
    
    logger.info(f"Mock retornando {len(opciones)} opciones de financiamiento")
    return opciones

def consultar_financiamiento(monto: float, tipo: str = "general") -> Dict[str, Any]:
    """
    Consulta de opciones de financiamiento
    
    Args:
        monto: Monto a financiar
        tipo: Tipo de financiamiento
        
    Returns:
        Resultado de la consulta
    """
    logger.info(f"Consultando financiamiento - monto: {monto}, tipo: {tipo}")
    
    # Usar mock para cálculo
    opciones = mock_calcular_cuotas(monto)
    
    return {
        "status": "ok",
        "opciones": opciones,
        "total_opciones": len(opciones),
        "monto_solicitado": monto,
        "tipo": tipo
    }
