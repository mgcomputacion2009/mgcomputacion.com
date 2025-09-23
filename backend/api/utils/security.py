"""
Utilidades de seguridad (HMAC, firmas, etc.)
"""

import hmac
import hashlib
from typing import Optional


def verify_hmac(body_bytes: bytes, signature: Optional[str], secret: Optional[str]) -> bool:
    """
    Verifica firma HMAC-SHA256 en hex.

    Args:
        body_bytes: Cuerpo bruto del request (bytes)
        signature: Firma recibida (hex string)
        secret: Secreto compartido

    Returns:
        True si la firma es válida, False en caso contrario
    """
    if not signature or not secret:
        return False
    try:
        digest = hmac.new(secret.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()
        return hmac.compare_digest(digest, signature.strip())
    except Exception:
        return False


