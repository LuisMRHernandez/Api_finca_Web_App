from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

from app.database.connection import get_db
from app.database.models import Secado, Finca
from app.schemas.secado_schema import SecadoCreate, SecadoResponse, SecadoGraficaResponse
from app.routers.auth import get_current_user   # ajusta si difiere

logger = logging.getLogger("secado")

router = APIRouter(prefix="/secado", tags=["Secado"])


# ── POST /secado/ ─────────────────────────────────────────────
# Guardar nuevo registro — se puede llenar varias veces
@router.post("/", response_model=SecadoResponse)
def guardar_secado(
    datos: SecadoCreate,
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_current_user)
):
    # Verificar que la finca pertenece al usuario
    finca = db.query(Finca).filter(
        Finca.id == datos.finca_id,
        Finca.usuario_id == usuario_actual.id
    ).first()
    if not finca:
        raise HTTPException(status_code=404, detail="Finca no encontrada")

    nuevo = Secado(
        finca_id           = datos.finca_id,
        lote_id             = datos.lote_id,   # ← NUEVO: ahora sí se guarda el lote
        humedad            = datos.humedad,
        factor_rendimiento = datos.factor_rendimiento,
        observacion        = datos.observacion,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return SecadoResponse(
        id                 = nuevo.id,
        finca_id           = nuevo.finca_id,
        lote_id            = nuevo.lote_id,    # ← NUEVO
        humedad            = nuevo.humedad,
        factor_rendimiento = nuevo.factor_rendimiento,
        observacion        = nuevo.observacion,
        fecha              = nuevo.created_at.strftime("%Y-%m-%d %H:%M"),
    )


# ── GET /secado/historial ─────────────────────────────────────
# Historial completo de la finca del usuario autenticado
@router.get("/historial", response_model=List[SecadoResponse])
def obtener_historial(
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_current_user)
):
    finca = db.query(Finca).filter(
        Finca.usuario_id == usuario_actual.id
    ).first()
    if not finca:
        raise HTTPException(status_code=404, detail="Finca no encontrada")

    registros = db.query(Secado).filter(
        Secado.finca_id == finca.id
    ).order_by(Secado.created_at.desc()).all()

    return [
        SecadoResponse(
            id                 = r.id,
            finca_id           = r.finca_id,
            lote_id            = r.lote_id,    # ← NUEVO
            humedad            = r.humedad,
            factor_rendimiento = r.factor_rendimiento,
            observacion        = r.observacion,
            fecha              = r.created_at.strftime("%Y-%m-%d %H:%M"),
        )
        for r in registros
    ]


# ── GET /secado/grafica/{finca_id} ────────────────────────────
# Datos para graficar — mismo formato que /fermentacion/grafica
@router.get("/grafica/{finca_id}", response_model=List[SecadoGraficaResponse])
def obtener_grafica(
    finca_id: int,
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_current_user)
):
    # Verificar que la finca pertenece al usuario
    finca = db.query(Finca).filter(
        Finca.id == finca_id,
        Finca.usuario_id == usuario_actual.id
    ).first()
    if not finca:
        raise HTTPException(status_code=404, detail="Finca no encontrada")

    registros = db.query(Secado).filter(
        Secado.finca_id == finca_id
    ).order_by(Secado.created_at.asc()).all()

    return [
        SecadoGraficaResponse(
            fecha              = r.created_at.strftime("%Y-%m-%d %H:%M"),
            humedad            = r.humedad,
            factor_rendimiento = r.factor_rendimiento,
        )
        for r in registros
    ]


@router.get("/public/grafica/{finca_id}")
def obtener_grafica_publica(
    finca_id: int,
    db: Session = Depends(get_db)
):
    datos = (
        db.query(Secado)
        .filter(Secado.finca_id == finca_id)
        .order_by(Secado.created_at.asc())
        .all()
    )
    resultado = []
    for r in datos:
        try:
            resultado.append({
                "humedad": r.humedad,
                "factor_rendimiento": r.factor_rendimiento,
                "fecha": r.created_at.strftime("%d/%m") if r.created_at else "—"
            })
        except Exception as e:
            logger.error(f"Registro de secado id={r.id} omitido por error: {e}")
            continue
    return resultado


# ── GET /secado/public/grafica-lote/{lote_id} ───────────────────
# Igual que /public/grafica/{finca_id} pero filtrado por lote específico
@router.get("/public/grafica-lote/{lote_id}")
def obtener_grafica_publica_por_lote(
    lote_id: int,
    db: Session = Depends(get_db)
):
    datos = (
        db.query(Secado)
        .filter(Secado.lote_id == lote_id)
        .order_by(Secado.created_at.asc())
        .all()
    )
    resultado = []
    for r in datos:
        try:
            resultado.append({
                "humedad": r.humedad,
                "factor_rendimiento": r.factor_rendimiento,
                "fecha": r.created_at.strftime("%d/%m") if r.created_at else "—"
            })
        except Exception as e:
            logger.error(f"Registro de secado id={r.id} omitido por error: {e}")
            continue
    return resultado