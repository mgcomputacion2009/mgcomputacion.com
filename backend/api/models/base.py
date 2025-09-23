"""
Base models for API
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    timestamp: str = datetime.now().isoformat()

class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: dict
    timestamp: str = datetime.now().isoformat()

class PaginationRequest(BaseModel):
    """Pagination request model"""
    limite: int = 20
    offset: int = 0

class PaginationResponse(BaseModel):
    """Pagination response model"""
    limite: int
    offset: int
    total: int
    paginas: int
