from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DispositivoCreate(BaseModel):
    nombre: str
    tipo: str  # "suelo" | "beneficio"


class DispositivoResponse(BaseModel):
    id: int
    finca_id: int
    nombre: str
    tipo: str
    activo: bool
    created_at: datetime
    ultima_conexion: Optional[datetime] = None

    class Config:
        from_attributes = True


class DispositivoTokenResponse(DispositivoResponse):
    # El token solo viaja en la respuesta de creacion. Despues de eso
    # no se vuelve a mostrar completo (el servidor no lo "recuerda" para
    # mostrarlo, solo para compararlo).
    token: str
