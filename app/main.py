from fastapi import FastAPI
from app.database.connection import engine
from app.database.models import Base
from app.routers import auth, fincas, fermentacion, calidad, secado
from app.routers import lotes                          # ← NUEVO
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Fincas Cafeteras", version="1.0")

app.add_middleware(CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"])

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth.router)
app.include_router(fincas.router)
app.include_router(fermentacion.router)
app.include_router(calidad.router)
app.include_router(secado.router)
app.include_router(lotes.router)                       # ← NUEVO

@app.get("/")
def home():
    return {"message": "API funcionando correctamente"}