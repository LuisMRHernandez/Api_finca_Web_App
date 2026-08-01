from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.connection import get_db
from app.database.models import Lote, Finca
from app.schemas.lote_schema import LoteCreate, LoteResponse, LoteCerrarResponse
from app.routers.auth import get_current_user
import logging
logger = logging.getLogger("lotes")

router = APIRouter(prefix="/lotes", tags=["Lotes"])


# ── POST /lotes/ — crear nuevo lote ──────────────────────────
@router.post("/", response_model=LoteResponse)
def crear_lote(
    datos: LoteCreate,
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_current_user)
):
    finca = db.query(Finca).filter(
        Finca.id == datos.finca_id,
        Finca.usuario_id == usuario_actual.id
    ).first()
    if not finca:
        raise HTTPException(status_code=404, detail="Finca no encontrada")

    lote = Lote(
        finca_id     = datos.finca_id,
        nombre       = datos.nombre,
        variedad     = datos.variedad,
        fecha_inicio = datos.fecha_inicio,
        activo       = True,
    )
    db.add(lote)
    db.commit()
    db.refresh(lote)

    return LoteResponse(
        id           = lote.id,
        finca_id     = lote.finca_id,
        nombre       = lote.nombre,
        variedad     = lote.variedad,
        fecha_inicio = lote.fecha_inicio.strftime("%Y-%m-%d")
                       if lote.fecha_inicio else None,
        activo       = lote.activo,
        created_at   = lote.created_at.strftime("%Y-%m-%d %H:%M"),
    )


# ── GET /lotes/mis-lotes — lotes de la finca del usuario ─────
@router.get("/mis-lotes", response_model=List[LoteResponse])
def obtener_mis_lotes(
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_current_user)
):
    finca = db.query(Finca).filter(
        Finca.usuario_id == usuario_actual.id
    ).first()
    if not finca:
        raise HTTPException(status_code=404, detail="Finca no encontrada")

    lotes = db.query(Lote).filter(
        Lote.finca_id == finca.id
    ).order_by(Lote.created_at.desc()).all()

    return [
        LoteResponse(
            id           = l.id,
            finca_id     = l.finca_id,
            nombre       = l.nombre,
            variedad     = l.variedad,
            fecha_inicio = l.fecha_inicio.strftime("%Y-%m-%d")
                           if l.fecha_inicio else None,
            activo       = l.activo,
            created_at   = l.created_at.strftime("%Y-%m-%d %H:%M"),
        )
        for l in lotes
    ]


# ── GET /lotes/activos — solo lotes activos ───────────────────
@router.get("/activos", response_model=List[LoteResponse])
def obtener_lotes_activos(
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_current_user)
):
    finca = db.query(Finca).filter(
        Finca.usuario_id == usuario_actual.id
    ).first()
    if not finca:
        raise HTTPException(status_code=404, detail="Finca no encontrada")

    lotes = db.query(Lote).filter(
        Lote.finca_id == finca.id,
        Lote.activo   == True
    ).order_by(Lote.created_at.desc()).all()

    return [
        LoteResponse(
            id           = l.id,
            finca_id     = l.finca_id,
            nombre       = l.nombre,
            variedad     = l.variedad,
            fecha_inicio = l.fecha_inicio.strftime("%Y-%m-%d")
                           if l.fecha_inicio else None,
            activo       = l.activo,
            created_at   = l.created_at.strftime("%Y-%m-%d %H:%M"),
        )
        for l in lotes
    ]


# ── PATCH /lotes/{lote_id}/cerrar — cerrar un lote ───────────
@router.patch("/{lote_id}/cerrar", response_model=LoteCerrarResponse)
def cerrar_lote(
    lote_id: int,
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_current_user)
):
    # Verificar que el lote pertenece a una finca del usuario
    lote = db.query(Lote).join(Finca).filter(
        Lote.id           == lote_id,
        Finca.usuario_id  == usuario_actual.id
    ).first()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")

    lote.activo = False
    db.commit()
    db.refresh(lote)
    return lote



# ── GET /lotes/public/{finca_id} — lotes de una finca, sin token ──
# Ubicar ANTES de cualquier ruta tipo "/{lote_id}" si algún día la agregas
@router.get("/public/{finca_id}", response_model=List[LoteResponse])
def obtener_lotes_publicos(
    finca_id: int,
    db: Session = Depends(get_db)
):
    lotes = db.query(Lote).filter(
        Lote.finca_id == finca_id
    ).order_by(Lote.created_at.desc()).all()

    resultado = []
    for l in lotes:
        try:
            resultado.append(LoteResponse(
                id           = l.id,
                finca_id     = l.finca_id,
                nombre       = l.nombre,
                variedad     = l.variedad,
                fecha_inicio = l.fecha_inicio.strftime("%Y-%m-%d") if l.fecha_inicio else None,
                activo       = l.activo,
                created_at   = l.created_at.strftime("%Y-%m-%d %H:%M") if l.created_at else None,
            ))
        except Exception as e:
            logger.error(f"Lote id={l.id} omitido por error: {e}")
            continue
    return resultado