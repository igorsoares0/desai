"""
Modelos Pydantic para validação de dados
"""
from pydantic import BaseModel, Field
from typing import Optional

class GenerateRequest(BaseModel):
    """Modelo para requisição de geração"""
    style: str = Field(..., description="Estilo do design")
    room_type: str = Field(..., description="Tipo de cômodo")
    strength: Optional[float] = Field(0.7, ge=0.0, le=1.0, description="Força da transformação")
    model: Optional[str] = Field("flux-dev", description="Modelo a usar")

class GenerateResponse(BaseModel):
    """Modelo para resposta de geração"""
    success: bool
    output_url: Optional[str] = None
    style: Optional[str] = None
    room_type: Optional[str] = None
    model_used: Optional[str] = None
    processing_time: Optional[float] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    """Modelo para health check"""
    status: str
    version: str
    replicate_configured: bool
