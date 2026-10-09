from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AnalisisSueloCreate(BaseModel):
    finca_id: int
    lote_id: Optional[int] = None

    cultivo: str
    etapa: str
    num_puntos: int = 1

    humedad: Optional[float] = None
    temperatura: Optional[float] = None
    ph: Optional[float] = None
    ec: Optional[float] = None
    n_mg_kg: Optional[float] = None
    p_mg_kg: Optional[float] = None
    k_mg_kg: Optional[float] = None

    estado_humedad: Optional[str] = None
    estado_temperatura: Optional[str] = None
    estado_ph: Optional[str] = None
    estado_ec: Optional[str] = None

    recomendacion: Optional[str] = None

    origen: str = "sensor"          # sensor | manual
    via_envio: Optional[str] = None  # wifi | bluetooth
    dispositivo_id: Optional[str] = None

    # Momento real en que se tomo la medicion en campo (lo manda el ESP32
    # o, si llego por Bluetooth y se sincronizo despues, lo manda la app
    # con la hora en que el telefono la recibio del sensor).
    fecha_medicion: Optional[datetime] = None


class AnalisisSueloResponse(BaseModel):
    id: int
    finca_id: int
    lote_id: Optional[int] = None

    cultivo: str
    etapa: str
    num_puntos: int

    humedad: Optional[float] = None
    temperatura: Optional[float] = None
    ph: Optional[float] = None
    ec: Optional[float] = None
    n_mg_kg: Optional[float] = None
    p_mg_kg: Optional[float] = None
    k_mg_kg: Optional[float] = None

    estado_humedad: Optional[str] = None
    estado_temperatura: Optional[str] = None
    estado_ph: Optional[str] = None
    estado_ec: Optional[str] = None

    recomendacion: Optional[str] = None

    origen: str
    via_envio: Optional[str] = None
    dispositivo_id: Optional[str] = None

    fecha_medicion: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
