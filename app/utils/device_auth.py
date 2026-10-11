from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from jose import jwt, JWTError

from app.database.connection import get_db
from app.database.models import Dispositivo, Finca
from app.utils.security import SECRET_KEY, ALGORITHM

# No lanza error automaticamente si no viene el header Authorization:
# asi podemos decidir nosotros si usamos token de dispositivo o JWT.
_security_opcional = HTTPBearer(auto_error=False)


class ContextoAuth:
    """
    Resultado de autenticar una peticion que puede venir de dos origenes:
      - "sensor": un ESP32 que manda su token fijo (header X-Device-Token)
      - "app":    la app movil con el JWT del usuario logueado
    El finca_id SIEMPRE se calcula aqui en el servidor (a partir del token
    o del usuario), nunca se confia en un finca_id que venga en el body.
    """

    def __init__(
        self,
        finca_id: int,
        origen: str,
        dispositivo_id: Optional[int] = None,
        dispositivo_nombre: Optional[str] = None,
        usuario_id: Optional[int] = None,
    ):
        self.finca_id = finca_id
        self.origen = origen
        self.dispositivo_id = dispositivo_id
        self.dispositivo_nombre = dispositivo_nombre
        self.usuario_id = usuario_id


def get_auth_context(
    db: Session = Depends(get_db),
    x_device_token: Optional[str] = Header(default=None, alias="X-Device-Token"),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_security_opcional),
) -> ContextoAuth:
    # 1) Token fijo de dispositivo (ESP32 enviando directo por WiFi)
    if x_device_token:
        dispositivo = (
            db.query(Dispositivo)
            .filter(Dispositivo.token == x_device_token, Dispositivo.activo == True)
            .first()
        )
        if not dispositivo:
            raise HTTPException(
                status_code=401, detail="Token de dispositivo invalido o revocado"
            )

        dispositivo.ultima_conexion = datetime.utcnow()
        db.commit()

        return ContextoAuth(
            finca_id=dispositivo.finca_id,
            origen="sensor",
            dispositivo_id=dispositivo.id,
            dispositivo_nombre=dispositivo.nombre,
        )

    # 2) JWT de usuario (app movil, p.ej. sincronizando lo que llego por
    #    Bluetooth mientras no habia internet)
    if credentials:
        try:
            payload = jwt.decode(
                credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]
            )
            user_id = payload.get("user_id")
            if not user_id:
                raise HTTPException(status_code=401, detail="Token invalido")
        except JWTError:
            raise HTTPException(status_code=401, detail="Token invalido")

        finca = db.query(Finca).filter(Finca.usuario_id == user_id).first()
        if not finca:
            raise HTTPException(status_code=404, detail="No tienes finca registrada")

        return ContextoAuth(finca_id=finca.id, origen="app", usuario_id=user_id)

    raise HTTPException(
        status_code=401,
        detail="Se requiere token de dispositivo (X-Device-Token) o token de usuario",
    )
