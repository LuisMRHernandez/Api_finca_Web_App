from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import secrets

from app.database.connection import get_db
from app.database.models import Dispositivos as Dispositivo, Finca
from app.schemas.dispositivo_schema import (
    DispositivoCreate,
    DispositivoResponse,
    DispositivoTokenResponse,
)
from app.routers.auth import get_current_user

router = APIRouter(prefix="/dispositivos", tags=["Dispositivos"])

TIPOS_VALIDOS = {"suelo", "beneficio"}


def _mi_finca(db: Session, usuario_actual) -> Finca:
    finca = db.query(Finca).filter(Finca.usuario_id == usuario_actual.id).first()
    if not finca:
        raise HTTPException(status_code=404, detail="No tienes finca registrada")
    return finca


# =====================
# CREAR DISPOSITIVO (genera el token fijo — se muestra UNA sola vez)
# =====================
@router.post("/", response_model=DispositivoTokenResponse)
def crear_dispositivo(
    datos: DispositivoCreate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    if datos.tipo not in TIPOS_VALIDOS:
        raise HTTPException(
            status_code=400, detail="tipo debe ser 'suelo' o 'beneficio'"
        )

    finca = _mi_finca(db, usuario_actual)

    nuevo = Dispositivo(
        finca_id=finca.id,
        nombre=datos.nombre,
        tipo=datos.tipo,
        token=secrets.token_hex(20),  # 40 caracteres, fijo para el dispositivo
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


# =====================
# MIS DISPOSITIVOS
# =====================
@router.get("/mis-dispositivos", response_model=List[DispositivoResponse])
def listar_dispositivos(
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    finca = _mi_finca(db, usuario_actual)
    return (
        db.query(Dispositivo)
        .filter(Dispositivo.finca_id == finca.id)
        .order_by(Dispositivo.created_at.desc())
        .all()
    )


# =====================
# REVOCAR / ACTIVAR
# =====================
@router.patch("/{dispositivo_id}/revocar", response_model=DispositivoResponse)
def revocar_dispositivo(
    dispositivo_id: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    finca = _mi_finca(db, usuario_actual)
    dispositivo = (
        db.query(Dispositivo)
        .filter(Dispositivo.id == dispositivo_id, Dispositivo.finca_id == finca.id)
        .first()
    )
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")

    dispositivo.activo = False
    db.commit()
    db.refresh(dispositivo)
    return dispositivo


@router.patch("/{dispositivo_id}/activar", response_model=DispositivoResponse)
def activar_dispositivo(
    dispositivo_id: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    finca = _mi_finca(db, usuario_actual)
    dispositivo = (
        db.query(Dispositivo)
        .filter(Dispositivo.id == dispositivo_id, Dispositivo.finca_id == finca.id)
        .first()
    )
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")

    dispositivo.activo = True
    db.commit()
    db.refresh(dispositivo)
    return dispositivo
