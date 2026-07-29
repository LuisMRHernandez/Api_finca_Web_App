from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LoteCreate(BaseModel):
    finca_id:     int
    nombre:       str
    variedad:     Optional[str] = None
    fecha_inicio: Optional[datetime] = None


class LoteResponse(BaseModel):
    id:           int
    finca_id:     int
    nombre:       str
    variedad:     Optional[str] = None
    fecha_inicio: Optional[str] = None
    activo:       bool
    created_at:   Optional[str] = None

    class Config:
        from_attributes = True


class LoteCerrarResponse(BaseModel):
    id:     int
    nombre: str
    activo: bool

    class Config:
        from_attributes = True