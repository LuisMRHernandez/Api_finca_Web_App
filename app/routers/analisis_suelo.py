from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from app.database.connection import SessionLocal
from app.database.models import AnalisisSuelo, Finca
from app.schemas.analisis_suelo_schema import AnalisisSueloCreate
from app.utils.oauth2 import get_current_user

logger = logging.getLogger("analisis_suelo")

router = APIRouter(
    prefix="/analisis-suelo",
    tags=["Análisis de Suelo"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =====================
# GUARDAR ANALISIS (lo usa el ESP32 directo por WiFi, y la app cuando
# sincroniza lo que llego por Bluetooth)
# =====================
@router.post("/")
def guardar_analisis_suelo(
    data: AnalisisSueloCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    finca = db.query(Finca).filter(Finca.id == data.finca_id).first()
    if not finca:
        raise HTTPException(status_code=404, detail="Finca no encontrada")
    if finca.usuario_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="No autorizado")

    nuevo_registro = AnalisisSuelo(
        finca_id=data.finca_id,
        lote_id=data.lote_id,
        cultivo=data.cultivo,
        etapa=data.etapa,
        num_puntos=data.num_puntos,
        humedad=data.humedad,
        temperatura=data.temperatura,
        ph=data.ph,
        ec=data.ec,
        n_mg_kg=data.n_mg_kg,
        p_mg_kg=data.p_mg_kg,
        k_mg_kg=data.k_mg_kg,
        estado_humedad=data.estado_humedad,
        estado_temperatura=data.estado_temperatura,
        estado_ph=data.estado_ph,
        estado_ec=data.estado_ec,
        recomendacion=data.recomendacion,
        origen=data.origen,
        via_envio=data.via_envio,
        dispositivo_id=data.dispositivo_id,
        fecha_medicion=data.fecha_medicion,
    )
    db.add(nuevo_registro)
    db.commit()
    db.refresh(nuevo_registro)
    return {
        "message": "Análisis de suelo guardado correctamente",
        "registro_id": nuevo_registro.id,
        "finca_id": nuevo_registro.finca_id
    }

# =====================
# HISTORIAL (usuario autenticado, su finca — la primera que tenga)
# =====================
@router.get("/historial")
def obtener_historial_suelo(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    finca = db.query(Finca).filter(
        Finca.usuario_id == current_user["user_id"]
    ).first()
    if not finca:
        raise HTTPException(status_code=404, detail="No tienes finca registrada")

    datos = db.query(AnalisisSuelo).filter(
        AnalisisSuelo.finca_id == finca.id
    ).order_by(AnalisisSuelo.created_at.desc()).all()

    return datos

# =====================
# HISTORIAL POR FINCA (autenticado)
# =====================
@router.get("/{finca_id}")
def obtener_historial_por_finca(
    finca_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    finca = db.query(Finca).filter(Finca.id == finca_id).first()
    if not finca:
        raise HTTPException(status_code=404, detail="Finca no encontrada")
    if finca.usuario_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="No autorizado")

    return db.query(AnalisisSuelo).filter(
        AnalisisSuelo.finca_id == finca_id
    ).order_by(AnalisisSuelo.created_at.desc()).all()

# =====================
# GRAFICA NPK (autenticado) — evolucion de N, P, K y pH en el tiempo
# =====================
@router.get("/grafica/{finca_id}")
def obtener_datos_grafica_suelo(
    finca_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    finca = db.query(Finca).filter(Finca.id == finca_id).first()
    if not finca:
        raise HTTPException(status_code=404, detail="Finca no encontrada")
    if finca.usuario_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="No autorizado")

    registros = db.query(AnalisisSuelo).filter(
        AnalisisSuelo.finca_id == finca_id
    ).order_by(AnalisisSuelo.created_at.asc()).all()

    return [
        {
            "fecha": (item.fecha_medicion or item.created_at).strftime("%Y-%m-%d %H:%M"),
            "cultivo": item.cultivo,
            "etapa": item.etapa,
            "ph": item.ph,
            "ec": item.ec,
            "n_mg_kg": item.n_mg_kg,
            "p_mg_kg": item.p_mg_kg,
            "k_mg_kg": item.k_mg_kg,
        }
        for item in registros
    ]
