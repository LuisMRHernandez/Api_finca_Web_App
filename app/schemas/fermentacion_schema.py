from pydantic import BaseModel
from typing import Optional


class FermentacionCreate(BaseModel):
    finca_id:    int
    lote_id:     Optional[int] = None   # ← NUEVO
    ph:          float
    brix:        float
    temperatura: float
    observacion: Optional[str] = None


class FermentacionResponse(BaseModel):
    id:          int
    finca_id:    int
    lote_id:     Optional[int] = None   # ← NUEVO
    ph:          float
    brix:        float
    temperatura: float
    observacion: Optional[str] = None
    fecha:       str

    class Config:
        from_attributes = True


class FermentacionGraficaResponse(BaseModel):
    fecha:       str
    ph:          float
    brix:        float
    temperatura: float