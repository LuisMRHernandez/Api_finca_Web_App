from pydantic import BaseModel, Field
from typing import Optional

class CalidadCafeCreate(BaseModel):
    finca_id: int
    puntaje_sensorial: float = Field(
        ...,
        ge=0,
        le=100,
        description="Puntaje de calidad sensorial (0-100, escala SCA)"
    )
    perfil_tueste: str = Field(
        ...,
        description="Perfil de tueste: claro, medio, medio-oscuro u oscuro"
    )
    notas_cata: Optional[str] = Field(
        None,
        description="Notas de cata libres, ej: chocolate, caramelo, cítrico"
    )
    proceso: str = Field(
        None,
        description="descripcion de su proceso en el beneficio"
    )
    observacion: Optional[str] = None