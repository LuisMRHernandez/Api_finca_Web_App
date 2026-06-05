from pydantic import BaseModel
from typing import Optional

class FincaCreate(BaseModel):
    nombre_finca: str
    municipio: str
    vereda: str
    descripcion: str
    variedad_cafe: Optional[str] = None     # ← NUEVO (ej. "Castillo", "Caturra", "Geisha")