from fastapi import FastAPI

from app.database.connection import engine
from app.database.models import Base

from app.routers import auth
from app.routers import fincas
from app.routers import fermentacion
from app.routers import calidad               # ← NUEVO

from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Crear tablas (incluye la nueva tabla calidad_cafe)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Fincas Cafeteras",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)

app.include_router(auth.router)
app.include_router(fincas.router)
app.include_router(fermentacion.router)
app.include_router(calidad.router)            # ← NUEVO

@app.get("/")
def home():
    return {"message": "API funcionando correctamente"}