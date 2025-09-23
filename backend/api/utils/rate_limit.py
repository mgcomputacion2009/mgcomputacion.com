"""
Rate limiting simple en memoria (ventana deslizante de 60s).
No persistente; adecuado para una sola instancia.
"""

import time
from collections import deque
from typing import Dict


_store: Dict[str, deque] = {}


def allow(key: str, limit: int, window_sec: int = 60) -> bool:
    """
    Retorna True si se permite la solicitud para `key` dentro del `window_sec`.
    Mantiene hasta `limit` timestamps recientes en una ventana deslizante.
    """
    now = time.time()
    bucket = _store.setdefault(key, deque())
    # Purga elementos antiguos
    while bucket and (now - bucket[0]) > window_sec:
        bucket.popleft()
    if len(bucket) >= max(0, int(limit or 0)):
        return False
    bucket.append(now)
    return True


