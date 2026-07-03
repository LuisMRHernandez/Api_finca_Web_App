from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.connection import Base

# ==========================
# TABLA USUARIOS
# ==========================
class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    celular = Column(String, nullable=True)          # ← NUEVO
    created_at = Column(DateTime, default=datetime.utcnow)
    fincas = relationship("Finca", back_populates="usuario")

# ==========================
# TABLA FINCAS
# ==========================
class Finca(Base):
    __tablename__ = "fincas"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    nombre_finca = Column(String, nullable=False)
    altura_finca = Column(String)
    municipio = Column(String)
    vereda = Column(String)
    descripcion = Column(Text)
    variedad_cafe = Column(String, nullable=True)    # ← NUEVO
    imagen_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="fincas")
    fermentaciones = relationship("Fermentacion", back_populates="finca")
    imagenes = relationship("ImagenFinca", back_populates="finca")
    calidades = relationship("CalidadCafe", back_populates="finca")  # ← NUEVO

# ==========================
# TABLA FERMENTACION
# ==========================
class Fermentacion(Base):
    __tablename__ = "fermentacion"
    id = Column(Integer, primary_key=True, index=True)
    finca_id = Column(Integer, ForeignKey("fincas.id"))
    brix = Column(Float)
    ph = Column(Float)
    temperatura = Column(Float)
    observacion = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    finca = relationship("Finca", back_populates="fermentaciones")

# ==========================
# TABLA CALIDAD CAFÉ          ← NUEVO
# ==========================
class CalidadCafe(Base):
    __tablename__ = "calidad_cafe"
    id = Column(Integer, primary_key=True, index=True)
    finca_id = Column(Integer, ForeignKey("fincas.id"), nullable=False)

    # Puntuación global de calidad sensorial (escala 0-100, estándar SCA)
    puntaje_sensorial = Column(Float, nullable=False)

    # Perfil de tueste: claro / medio / medio-oscuro / oscuro
    perfil_tueste = Column(String, nullable=False)

    # Notas de cata: descripción libre (ej. "chocolate, caramelo, cítrico")
    notas_cata = Column(Text, nullable=True)

    # proceso: descripción libre (ej. "descripcion proceso de beneficio")
    proceso = Column(Text, nullable=True)

    # Observaciones adicionales del evaluador
    observacion = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    finca = relationship("Finca", back_populates="calidades")

# ==========================
# TABLA IMAGENES
# ==========================
class ImagenFinca(Base):
    __tablename__ = "imagenes_finca"
    id = Column(Integer, primary_key=True, index=True)
    finca_id = Column(Integer, ForeignKey("fincas.id"))
    ruta_imagen = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    finca = relationship("Finca", back_populates="imagenes")