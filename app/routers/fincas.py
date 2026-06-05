from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    HTTPException
)

from sqlalchemy.orm import Session
import os
import shutil

from app.database.connection import get_db
from app.database.models import Finca, Usuario
from app.schemas.finca_schema import FincaCreate
from app.routers.auth import get_current_user

router = APIRouter(
    prefix="/fincas",
    tags=["Fincas"]
)

# ==========================
# CREAR FINCA
# ==========================
@router.post("/")
def crear_finca(
    finca: FincaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    nueva_finca = Finca(
        usuario_id=current_user.id,
        nombre_finca=finca.nombre_finca,
        municipio=finca.municipio,
        vereda=finca.vereda,
        descripcion=finca.descripcion,
        variedad_cafe=finca.variedad_cafe   # ← NUEVO
    )
    db.add(nueva_finca)
    db.commit()
    db.refresh(nueva_finca)

    return {
        "message": "Finca creada correctamente",
        "finca_id": nueva_finca.id
    }

# ==========================
# LISTAR MIS FINCAS
# ==========================
@router.get("/")
def obtener_mis_fincas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    fincas = db.query(Finca).filter(
        Finca.usuario_id == current_user.id
    ).all()

    return [
        {
            "id": f.id,
            "nombre_finca": f.nombre_finca,
            "municipio": f.municipio,
            "vereda": f.vereda,
            "descripcion": f.descripcion,
            "variedad_cafe": f.variedad_cafe,   # ← NUEVO
            "imagen_url": f.imagen_url
        }
        for f in fincas
    ]

# ==========================
# OBTENER MI FINCA
# ==========================
@router.get("/mi-finca")
def obtener_mi_finca(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    finca = db.query(Finca).filter(
        Finca.usuario_id == current_user.id
    ).first()

    if not finca:
        raise HTTPException(
            status_code=404,
            detail="No tienes finca registrada"
        )

    return {
        "id": finca.id,
        "nombre_finca": finca.nombre_finca,
        "municipio": finca.municipio,
        "vereda": finca.vereda,
        "descripcion": finca.descripcion,
        "variedad_cafe": finca.variedad_cafe,   # ← NUEVO
        "imagen_url": finca.imagen_url
    }

# ==========================
# SUBIR FOTO FINCA
# ==========================
@router.post("/upload-foto/{finca_id}")
def subir_foto_finca(
    finca_id: int,
    foto: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    finca = db.query(Finca).filter(Finca.id == finca_id).first()

    if not finca:
        raise HTTPException(status_code=404, detail="Finca no encontrada")
    if finca.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado")

    os.makedirs("uploads/fincas", exist_ok=True)

    extension = foto.filename.split(".")[-1]
    nombre_archivo = f"finca_{finca_id}.{extension}"
    ruta = os.path.join("uploads", "fincas", nombre_archivo)

    with open(ruta, "wb") as buffer:
        shutil.copyfileobj(foto.file, buffer)

    finca.imagen_url = ruta
    db.commit()

    return {
        "message": "Foto subida correctamente",
        "ruta": ruta
    }

# ==========================
# PÚBLICO — TODAS LAS FINCAS
# ==========================
@router.get("/public")
def obtener_fincas_publicas(
    db: Session = Depends(get_db)
):
    fincas = db.query(Finca).all()

    return [
        {
            "id": f.id,
            "nombre": f.nombre_finca,
            "ubicacion": f"{f.vereda}, {f.municipio}",
            "descripcion": f.descripcion,
            "variedad_cafe": f.variedad_cafe,   # ← NUEVO
            "foto": f.imagen_url
        }
        for f in fincas
    ]