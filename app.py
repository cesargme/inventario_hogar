from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from auth.basic import verify_credentials
from config.manifest import manifest_data
from config.settings import APP_NAME, APP_VERSION
from database.db import init_db, get_session
from database.models import User
from routes import inventory, process
from sqlmodel import Session, select
from utils.time import humanize_time


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

# Templates Jinja2
templates = Jinja2Templates(directory="templates")

# Registrar routers
app.include_router(inventory.router)
app.include_router(process.router)


@app.get("/", response_class=HTMLResponse)
async def root(
    request: Request,
    user: User = Depends(verify_credentials),
):
    """Main app view"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/app/process", response_class=HTMLResponse)
async def app_process_view(
    request: Request,
    user: User = Depends(verify_credentials),
):
    """Vista de procesamiento de texto"""
    return templates.TemplateResponse(
        "components/process_view.html", {"request": request}
    )


@app.get("/app/inventory", response_class=HTMLResponse)
async def app_inventory_view(
    request: Request,
    section_id: int | None = None,
    user: User = Depends(verify_credentials),
    session: Session = Depends(get_session),
):
    """Vista de inventario con filtro opcional por sección"""
    from database.models import Item, Section

    # Obtener secciones
    sections_stmt = select(Section).order_by(Section.name)
    sections = session.exec(sections_stmt).all()

    # Obtener items
    items_stmt = select(Item).order_by(Item.updated_at.desc())
    if section_id:
        items_stmt = items_stmt.where(Item.section_id == section_id)

    items = session.exec(items_stmt).all()

    # Preparar data para template
    items_data = [
        {
            "id": item.id,
            "name": item.name,
            "emoji": item.emoji,
            "quantity": item.quantity,
            "unit": item.unit,
            "section_emoji": item.section.emoji,
            "section_name": item.section.name,
            "updated_at_human": humanize_time(item.updated_at),
            "is_below_threshold": item.is_below_threshold,
        }
        for item in items
    ]

    sections_data = [
        {
            "id": section.id,
            "name": section.name,
            "emoji": section.emoji,
        }
        for section in sections
    ]

    return templates.TemplateResponse(
        "components/inventory_view.html",
        {"request": request, "items": items_data, "sections": sections_data},
    )


@app.get("/manifest.json", response_class=JSONResponse)
async def get_manifest():
    """Servir PWA manifest"""
    return manifest_data


@app.get("/health")
async def health_check(session: Session = Depends(get_session)):
    """Health check para Railway"""
    import os
    from database.models import Section, Item, User

    # Contar registros
    sections_count = len(session.exec(select(Section)).all())
    items_count = len(session.exec(select(Item)).all())
    users_count = len(session.exec(select(User)).all())

    return {
        "status": "ok",
        "database": {
            "path": os.getenv("DB_PATH", "./inventario.db"),
            "sections": sections_count,
            "items": items_count,
            "users": users_count,
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8030, reload=True)
