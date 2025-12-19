from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from config.manifest import manifest_data
from config.settings import APP_NAME, APP_VERSION
from database.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa la base de datos al arrancar la app"""
    init_db()
    yield


# Crear app FastAPI
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    lifespan=lifespan,
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """Root endpoint - temporal"""
    return {"message": "Inventario Alimentos API", "version": APP_VERSION}


@app.get("/manifest.json", response_class=JSONResponse)
async def get_manifest():
    """Servir PWA manifest"""
    return manifest_data


@app.get("/health")
async def health_check():
    """Health check para Railway"""
    return {"status": "ok"}
