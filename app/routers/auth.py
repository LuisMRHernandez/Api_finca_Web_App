from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.database.models import Usuario
from app.schemas.user_schema import UserCreate, UserResponse
from app.utils.security import hash_password, verify_password

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.utils.security import SECRET_KEY, ALGORITHM

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =====================
# REGISTRO
# =====================
@router.post("/register", response_model=UserResponse)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(Usuario).filter(
        Usuario.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="El correo ya existe")

    new_user = Usuario(
        nombre=user.nombre,
        email=user.email,
        password=hash_password(user.password),
        celular=user.celular            # ← NUEVO
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

# =====================
# LOGIN JWT
# =====================
from app.schemas.auth_schema import LoginRequest
from app.utils.security import create_access_token

@router.post("/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(Usuario).filter(
        Usuario.email == request.email
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    token = create_access_token({"user_id": user.id, "email": user.email})

    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": user.nombre
    }

# =====================
# OBTENER USUARIO JWT
# =====================
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return user