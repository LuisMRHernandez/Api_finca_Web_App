from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean
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
    variedad_cafe = Column(String, nullable=True)   
    imagen_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="fincas")
    fermentaciones = relationship("Fermentacion", back_populates="finca")
    imagenes = relationship("ImagenFinca", back_populates="finca")
    calidades = relationship("CalidadCafe", back_populates="finca")
    secados = relationship("Secado", back_populates="finca")
    lotes = relationship("Lote", back_populates="finca")
    analisis_suelo = relationship("AnalisisSuelo", back_populates="finca")
    dispositivos = relationship("Dispositivo", back_populates="finca")

# ==========================
# TABLA LOTES — corregida
# ==========================

class Lote(Base):
    __tablename__ = "lotes"
    id = Column(Integer, primary_key=True, index=True)
    finca_id = Column(Integer, ForeignKey("fincas.id"), nullable=False)
    nombre = Column(String, nullable=False)

    # ── Campos que faltaban (los usa lotes.py / lote_schema.py) ──
    variedad = Column(String, nullable=True)
    fecha_inicio = Column(DateTime, nullable=True)
    activo = Column(Boolean, default=True, nullable=False)

    # ── Campos existentes (se conservan) ──
    fecha_recoleccion = Column(DateTime, nullable=True)
    cantidad_kg = Column(Float, nullable=True)
    estado = Column(
        String,
        default="Fermentación"
    )  # Fermentación, Secado, Finalizado
    observacion = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    finca = relationship("Finca", back_populates="lotes")

    fermentaciones = relationship(
        "Fermentacion",
        back_populates="lote",
        cascade="all, delete-orphan"
    )

    secados = relationship(
        "Secado",
        back_populates="lote",
        cascade="all, delete-orphan"
    )

    analisis_suelo = relationship(
        "AnalisisSuelo",
        back_populates="lote",
        cascade="all, delete-orphan"
    )

# ==========================
# TABLA FERMENTACION
# ==========================
class Fermentacion(Base):
    __tablename__ = "fermentacion"
    id = Column(Integer, primary_key=True, index=True)
    finca_id = Column(Integer, ForeignKey("fincas.id"))
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=True)
    brix = Column(Float)
    ph = Column(Float)
    temperatura = Column(Float)
    observacion = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    finca = relationship("Finca", back_populates="fermentaciones")
    lote = relationship("Lote", back_populates="fermentaciones")

# ==========================
# TABLA CALIDAD CAFÉ          
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

# ==========================
# TABLA SECADO
# ==========================
class Secado(Base):
    __tablename__ = "secado"
    id = Column(Integer, primary_key=True, index=True)
    finca_id = Column(Integer, ForeignKey("fincas.id"), nullable=False)
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=True)
    humedad   = Column(Float, nullable=False)   # % humedad del grano
    factor_rendimiento = Column(Float, nullable=False)   # factor de rendimiento
    observacion = Column(Text, nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)

    finca = relationship("Finca", back_populates="secados")
    lote = relationship("Lote", back_populates="secados")

# ==========================
# TABLA ANALISIS DE SUELO (medidor NPK portátil)
# ==========================
class AnalisisSuelo(Base):
    __tablename__ = "analisis_suelo"
    id = Column(Integer, primary_key=True, index=True)
    finca_id = Column(Integer, ForeignKey("fincas.id"), nullable=False)
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=True)

    cultivo = Column(String, nullable=False)          # ej. "Cafe", "Uchuva"
    etapa = Column(String, nullable=False)             # ej. "Floracion", "Vivero / semillero"
    num_puntos = Column(Integer, nullable=False, default=1)  # puntos de muestreo promediados

    humedad = Column(Float, nullable=True)             # %RH
    temperatura = Column(Float, nullable=True)         # C
    ph = Column(Float, nullable=True)
    ec = Column(Float, nullable=True)                  # uS/cm
    n_mg_kg = Column(Float, nullable=True)
    p_mg_kg = Column(Float, nullable=True)
    k_mg_kg = Column(Float, nullable=True)

    estado_humedad = Column(String, nullable=True)      # BAJO/NORMAL/ALTO/SIN REFERENCIA
    estado_temperatura = Column(String, nullable=True)
    estado_ph = Column(String, nullable=True)
    estado_ec = Column(String, nullable=True)

    recomendacion = Column(Text, nullable=True)         # texto generado por el medidor

    origen = Column(String, nullable=False, default="sensor")       # sensor | manual
    via_envio = Column(String, nullable=True)                       # wifi | bluetooth
    dispositivo_id = Column(String, nullable=True)                  # id/MAC del ESP32 que envio el dato

    fecha_medicion = Column(DateTime, nullable=True)    # momento real de la medicion en campo
    created_at = Column(DateTime, default=datetime.utcnow)          # momento en que llego a la BD

    finca = relationship("Finca", back_populates="analisis_suelo")
    lote = relationship("Lote", back_populates="analisis_suelo")

# ==========================
# TABLA DISPOSITIVOS (ESP32 registrados: medidor de suelo,
# estacion de fermentacion/secado, etc.) — autenticacion por
# token fijo, sin login de usuario/contraseña desde el dispositivo.
# ==========================
class Dispositivo(Base):
    __tablename__ = "dispositivos"
    id = Column(Integer, primary_key=True, index=True)
    finca_id = Column(Integer, ForeignKey("fincas.id"), nullable=False)

    nombre = Column(String, nullable=False)        # ej. "Medidor NPK - Lote 1"
    tipo = Column(String, nullable=False)           # suelo | beneficio
    token = Column(String, unique=True, nullable=False, index=True)
    activo = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    ultima_conexion = Column(DateTime, nullable=True)

    finca = relationship("Finca", back_populates="dispositivos")
