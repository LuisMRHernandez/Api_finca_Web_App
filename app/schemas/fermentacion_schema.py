from pydantic import BaseModel
from typing import Optional


class FermentacionCreate(BaseModel):
    finca_id: int
    brix: float
    ph: float
    temperatura: float
    observacion: Optional[str] = None