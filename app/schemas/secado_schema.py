from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime


class SecadoCreate(BaseModel):
    finca_id:           int
    humedad:            float   # % — rango normal café: 10 – 12.5 %
    factor_rendimiento: float   # rango normal: 0 – 100
    observacion:        Optional[str] = None

    @validator('humedad')
    def validar_humedad(cls, v):
        if v < 0 or v > 100:
            raise ValueError('La humedad debe estar entre 0 y 100 %')
        return v

    @validator('factor_rendimiento')
    def validar_rendimiento(cls, v):
        if v < 0 or v > 100:
            raise ValueError('El factor de rendimiento debe estar entre 0 y 100')
        return v


class SecadoResponse(BaseModel):
    id:                 int
    finca_id:           int
    humedad:            float
    factor_rendimiento: float
    observacion:        Optional[str] = None
    fecha:              str   # formateado como string para la app y la web

    class Config:
        from_attributes = True


class SecadoGraficaResponse(BaseModel):
    fecha:              str
    humedad:            float
    factor_rendimiento: float