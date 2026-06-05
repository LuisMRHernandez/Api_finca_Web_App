from pydantic import BaseModel, EmailStr
from typing import Optional

# Crear usuario
class UserCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    celular: Optional[str] = None       # ← NUEVO (opcional al registrarse)

# Respuesta usuario
class UserResponse(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    celular: Optional[str] = None       # ← NUEVO

    class Config:
        from_attributes = True