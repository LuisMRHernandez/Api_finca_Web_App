from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

from app.database.connection import get_db
from app.database.models import AnalisisSuelo, Finca
from app.schemas.analisis_suelo_schema import AnalisisSueloCreate, AnalisisSueloResponse
from app.utils.device_auth import get_auth_context, ContextoAuth
from app.routers.auth import get_current_user

logger = logging.getLogger("analisis_suelo")

router = APIRouter(prefix="/analisis-suelo", tags=["Análisis de Suelo"])


# =====================
# GUARDAR ANALISIS
# Acepta DOS formas de autenticacion (ver app/utils/device_auth.py):
#   - Header "X-Device-Token": el medidor de suelo (ESP32) enviando
#     directo por WiFi con su token fijo.
#   - Authorization: Bearer <JWT>: la app movil, cuando sincroniza un
#     resultado que llego al telefono por Bluetooth.
# El finca_id SIEMPRE se resuelve aqui, nunca se confia en el body.
# =====================
@router.post("/", response_model=AnalisisSueloResponse)
def guardar_analisis_suelo(
    data: AnalisisSueloCreate,
    db: Session = Depends(get_db),
    auth: ContextoAuth = Depends(get_auth_context),
):
    nuevo_registro = AnalisisSuelo(
        finca_id=auth.finca_id,
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
        origen="sensor" if auth.origen == "sensor" else (data.origen or "manual"),
        via_envio="wifi" if auth.origen == "sensor" else (data.via_envio or "bluetooth"),
        dispositivo_id=auth.dispositivo_nombre or data.dispositivo_id,
        fecha_medicion=data.fecha_medicion,
    )
    db.add(nuevo_registro)
    db.commit()
    db.refresh(nuevo_registro)
    return nuevo_registro


# =====================
# HISTORIAL (app, usuario autenticado con JWT — su finca)
# =====================
@router.get("/historial", response_model=List[AnalisisSueloResponse])
def obtener_historial_suelo(
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    finca = db.query(Finca).filter(Finca.usuario_id == usuario_actual.id).first()
    if not finca:
        raise HTTPException(status_code=404, detail="No tienes finca registrada")

    return (
        db.query(AnalisisSuelo)
        .filter(AnalisisSuelo.finca_id == finca.id)
        .order_by(AnalisisSuelo.created_at.desc())
        .all()
    )


# =====================
# HISTORIAL POR FINCA (app)
# =====================
@router.get("/{finca_id}", response_model=List[AnalisisSueloResponse])
def obtener_historial_por_finca(
    finca_id: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    finca = db.query(Finca).filter(Finca.id == finca_id).first()
    if not finca:
        raise HTTPException(status_code=404, detail="Finca no encontrada")
    if finca.usuario_id != usuario_actual.id:
        raise HTTPException(status_code=403, detail="No autorizado")

    return (
        db.query(AnalisisSuelo)
        .filter(AnalisisSuelo.finca_id == finca_id)
        .order_by(AnalisisSuelo.created_at.desc())
        .all()
    )


# =====================
# GRAFICA NPK (app) — evolucion de N, P, K y pH en el tiempo
# =====================
@router.get("/grafica/{finca_id}")
def obtener_datos_grafica_suelo(
    finca_id: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    finca = db.query(Finca).filter(Finca.id == finca_id).first()
    if not finca:
        raise HTTPException(status_code=404, detail="Finca no encontrada")
    if finca.usuario_id != usuario_actual.id:
        raise HTTPException(status_code=403, detail="No autorizado")

    registros = (
        db.query(AnalisisSuelo)
        .filter(AnalisisSuelo.finca_id == finca_id)
        .order_by(AnalisisSuelo.created_at.asc())
        .all()
    )

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
