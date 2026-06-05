from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import CalidadCafe, Finca
from app.schemas.calidad_schema import CalidadCafeCreate
from app.routers.auth import get_current_user

router = APIRouter(
    prefix="/calidad",
    tags=["Calidad de Café"]
)

# =============================================
# PRIVADO — GUARDAR REGISTRO DE CALIDAD
# =============================================
@router.post("/")
def guardar_calidad(
    data: CalidadCafeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    finca = db.query(Finca).filter(Finca.id == data.finca_id).first()
    if not finca:
        raise HTTPException(status_code=404, detail="Finca no encontrada")
    if finca.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado")

    nuevo = CalidadCafe(
        finca_id=data.finca_id,
        puntaje_sensorial=data.puntaje_sensorial,
        perfil_tueste=data.perfil_tueste,
        notas_cata=data.notas_cata,
        observacion=data.observacion
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return {
        "message": "Registro de calidad guardado correctamente",
        "registro_id": nuevo.id
    }

# =============================================
# PRIVADO — HISTORIAL DE CALIDAD (mi finca)
# =============================================
@router.get("/historial")
def historial_calidad(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    finca = db.query(Finca).filter(
        Finca.usuario_id == current_user.id
    ).first()
    if not finca:
        raise HTTPException(status_code=404, detail="No tienes finca registrada")

    registros = db.query(CalidadCafe).filter(
        CalidadCafe.finca_id == finca.id
    ).order_by(CalidadCafe.created_at.asc()).all()

    return [
        {
            "id": r.id,
            "fecha": r.created_at,
            "puntaje_sensorial": r.puntaje_sensorial,
            "perfil_tueste": r.perfil_tueste,
            "notas_cata": r.notas_cata,
            "observacion": r.observacion
        }
        for r in registros
    ]

# =============================================
# PRIVADO — DATOS PARA GRÁFICA (por finca_id)
# =============================================
@router.get("/grafica/{finca_id}")
def grafica_calidad(
    finca_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    finca = db.query(Finca).filter(Finca.id == finca_id).first()
    if not finca:
        raise HTTPException(status_code=404, detail="Finca no encontrada")
    if finca.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado")

    registros = db.query(CalidadCafe).filter(
        CalidadCafe.finca_id == finca_id
    ).order_by(CalidadCafe.created_at.asc()).all()

    return [
        {
            "fecha": r.created_at.strftime("%Y-%m-%d %H:%M"),
            "puntaje_sensorial": r.puntaje_sensorial,
            "perfil_tueste": r.perfil_tueste,
            "notas_cata": r.notas_cata
        }
        for r in registros
    ]

# =============================================
# PÚBLICO — ÚLTIMOS REGISTROS DE UNA FINCA
# =============================================
@router.get("/public/{finca_id}")
def calidad_publica(
    finca_id: int,
    db: Session = Depends(get_db)
):
    registros = (
        db.query(CalidadCafe)
        .filter(CalidadCafe.finca_id == finca_id)
        .order_by(CalidadCafe.created_at.desc())
        .limit(10)
        .all()
    )

    if not registros:
        raise HTTPException(
            status_code=404,
            detail="No hay registros de calidad para esta finca"
        )

    return [
        {
            "fecha": r.created_at.strftime("%d/%m/%Y"),
            "puntaje_sensorial": r.puntaje_sensorial,
            "perfil_tueste": r.perfil_tueste,
            "notas_cata": r.notas_cata
        }
        for r in registros
    ]

# =============================================
# PÚBLICO — DATOS PARA GRÁFICA (página web)
# =============================================
@router.get("/public/grafica/{finca_id}")
def grafica_calidad_publica(
    finca_id: int,
    db: Session = Depends(get_db)
):
    registros = (
        db.query(CalidadCafe)
        .filter(CalidadCafe.finca_id == finca_id)
        .order_by(CalidadCafe.created_at.asc())
        .all()
    )

    return [
        {
            "fecha": r.created_at.strftime("%d/%m"),
            "puntaje_sensorial": r.puntaje_sensorial,
            "perfil_tueste": r.perfil_tueste,
            "notas_cata": r.notas_cata
        }
        for r in registros
    ]