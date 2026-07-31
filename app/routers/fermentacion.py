from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.database.models import Fermentacion, Finca
from app.schemas.fermentacion_schema import FermentacionCreate
from app.utils.oauth2 import get_current_user

router = APIRouter(
    prefix="/fermentacion",
    tags=["Fermentación"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =====================
# GUARDAR DATOS
# =====================
@router.post("/")
def guardar_fermentacion(
    data: FermentacionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    finca = db.query(Finca).filter(Finca.id == data.finca_id).first()
    if not finca:
        raise HTTPException(status_code=404, detail="Finca no encontrada")
    if finca.usuario_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="No autorizado")

    nuevo_registro = Fermentacion(
        finca_id=data.finca_id,
        brix=data.brix,
        ph=data.ph,
        temperatura=data.temperatura,
        observacion=data.observacion
    )
    db.add(nuevo_registro)
    db.commit()
    db.refresh(nuevo_registro)
    return {
        "message": "Datos guardados correctamente",
        "registro_id": nuevo_registro.id
    }

# =====================
# HISTORIAL (usuario autenticado, su finca)
# =====================
@router.get("/historial")
def obtener_historial_fermentacion(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    finca = db.query(Finca).filter(
        Finca.usuario_id == current_user["user_id"]
    ).first()
    if not finca:
        raise HTTPException(status_code=404, detail="No tienes finca registrada")

    datos = db.query(Fermentacion).filter(
        Fermentacion.finca_id == finca.id
    ).order_by(Fermentacion.created_at.asc()).all()

    return [
        {
            "id": dato.id,
            "fecha": dato.created_at,
            "brix": dato.brix,
            "ph": dato.ph,
            "temperatura": dato.temperatura,
            "observacion": dato.observacion
        }
        for dato in datos
    ]

# =====================
# DATOS PARA GRÁFICAS (autenticado)
# =====================
@router.get("/grafica/{finca_id}")
def obtener_datos_grafica(
    finca_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    finca = db.query(Finca).filter(Finca.id == finca_id).first()
    if not finca:
        raise HTTPException(status_code=404, detail="Finca no encontrada")
    if finca.usuario_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="No autorizado")

    registros = db.query(Fermentacion).filter(
        Fermentacion.finca_id == finca_id
    ).order_by(Fermentacion.id.asc()).all()

    return [
        {
            "fecha": item.created_at.strftime("%Y-%m-%d %H:%M"),
            "brix": item.brix,
            "ph": item.ph,
            "temperatura": item.temperatura
        }
        for item in registros
    ]

# =====================
# ENDPOINTS PÚBLICOS (sin JWT) — ANTES de /{finca_id}
# =====================
import logging
logger = logging.getLogger("fermentacion")

@router.get("/public/grafica/{finca_id}")
def obtener_grafica_publica(
    finca_id: int,
    db: Session = Depends(get_db)
):
    datos = (
        db.query(Fermentacion)
        .filter(Fermentacion.finca_id == finca_id)
        .order_by(Fermentacion.created_at.asc())
        .all()
    )
    resultado = []
    for d in datos:
        try:
            resultado.append({
                "ph": d.ph,
                "brix": d.brix,
                "temperatura": d.temperatura,
                # si created_at viniera nulo, no se cae: se omite la fecha
                "fecha": d.created_at.strftime("%d/%m") if d.created_at else "—"
            })
        except Exception as e:
            logger.error(f"Registro de fermentación id={d.id} omitido por error: {e}")
            continue
    return resultado

# =====================
# HISTORIAL POR FINCA (autenticado) — AL FINAL
# =====================
@router.get("/{finca_id}")
def obtener_historial(
    finca_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    finca = db.query(Finca).filter(Finca.id == finca_id).first()
    if not finca:
        raise HTTPException(status_code=404, detail="Finca no encontrada")
    if finca.usuario_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="No autorizado")

    return db.query(Fermentacion).filter(
        Fermentacion.finca_id == finca_id
    ).order_by(Fermentacion.id.asc()).all()