from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os, shutil

from app.database.connection import get_db
from app.database.models import Finca
from app.schemas.finca_schema import (
    FincaCreate, FincaPublicResponse, FincaResponse
)

# ── get_current_user ─────────────────────────────────────────
# En la mayoría de proyectos FastAPI está en auth.py
# Si te da error cambia esta línea por la ubicación correcta:
#   from app.utils.dependencies import get_current_user
#   from app.routers.auth import get_current_user
from app.routers.auth import get_current_user

router = APIRouter(prefix="/fincas", tags=["Fincas"])

UPLOAD_DIR = "uploads/fincas"


# ── GET /fincas/public ────────────────────────────────────────
# Sin token — usado por la página web para mostrar tarjetas
@router.get("/public", response_model=List[FincaPublicResponse])
def listar_fincas_publicas(db: Session = Depends(get_db)):
    fincas = db.query(Finca).all()
    resultado = []
    for f in fincas:
        resultado.append({
            "id":                f.id,
            "nombre":            f.nombre_finca,
            "altura":            f.altura_finca or "—",
            "ubicacion":         f"{f.municipio}, {f.vereda}"
                                 if f.municipio and f.vereda
                                 else (f.municipio or f.vereda or "—"),
            "descripcion":       f.descripcion,
            "variedad_cafe":     f.variedad_cafe,
            "foto":              f.imagen_url,
            # Datos del propietario via relación usuario (definida en models.py)
            "nombre_productor":  f.usuario.nombre  if f.usuario else None,
            "celular_productor": f.usuario.celular if f.usuario else None,
        })
    return resultado


# ── GET /fincas/mi-finca ──────────────────────────────────────
# Con token — usado por la app móvil
@router.get("/mi-finca", response_model=FincaResponse)
def obtener_mi_finca(
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_current_user)
):
    finca = db.query(Finca).filter(
        Finca.usuario_id == usuario_actual.id
    ).first()
    if not finca:
        raise HTTPException(status_code=404, detail="Finca no encontrada")
    return finca


# ── POST /fincas ──────────────────────────────────────────────
@router.post("/", response_model=FincaResponse)
def crear_finca(
    datos: FincaCreate,
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_current_user)
):
    existente = db.query(Finca).filter(
        Finca.usuario_id == usuario_actual.id
    ).first()
    if existente:
        raise HTTPException(
            status_code=400,
            detail="Ya tienes una finca registrada"
        )
    nueva = Finca(
        usuario_id    = usuario_actual.id,
        nombre_finca  = datos.nombre_finca,
        altura_finca  = datos.altura_finca,
        municipio     = datos.municipio,
        vereda        = datos.vereda,
        descripcion   = datos.descripcion,
        variedad_cafe = datos.variedad_cafe,
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


# ── POST /fincas/upload-foto/{finca_id} ───────────────────────
@router.post("/upload-foto/{finca_id}")
def subir_foto(
    finca_id: int,
    foto: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_current_user)
):
    finca = db.query(Finca).filter(
        Finca.id == finca_id,
        Finca.usuario_id == usuario_actual.id
    ).first()
    if not finca:
        raise HTTPException(status_code=404, detail="Finca no encontrada")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ruta = f"{UPLOAD_DIR}/finca_{finca_id}.jpg"
    with open(ruta, "wb") as buffer:
        shutil.copyfileobj(foto.file, buffer)

    finca.imagen_url = ruta
    db.commit()
    return {"message": "Foto subida correctamente", "url": ruta}