from pydantic import BaseModel
from typing import Optional


# ── Crear finca (POST /fincas/) ───────────────────────────────
class FincaCreate(BaseModel):
    nombre_finca:  str
    altura_finca:  str
    municipio:     str
    vereda:        str
    descripcion:   str
    variedad_cafe: Optional[str] = None


# ── Respuesta privada (GET /fincas/mi-finca) ──────────────────
# Nombres exactos de las columnas en la tabla fincas
class FincaResponse(BaseModel):
    id:            int
    nombre_finca:  str
    altura_finca:  Optional[str] = None
    municipio:     Optional[str] = None
    vereda:        Optional[str] = None
    descripcion:   Optional[str] = None
    variedad_cafe: Optional[str] = None
    imagen_url:    Optional[str] = None

    class Config:
        from_attributes = True


# ── Respuesta pública (GET /fincas/public) ────────────────────
# Campos renombrados + datos del propietario para la web
class FincaPublicResponse(BaseModel):
    id:                int
    nombre:            str
    altura:            Optional[str] = None
    ubicacion:         Optional[str] = None
    descripcion:       Optional[str] = None
    variedad_cafe:     Optional[str] = None
    foto:              Optional[str] = None
    nombre_productor:  Optional[str] = None
    celular_productor: Optional[str] = None

    class Config:
        from_attributes = True