from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

from routes import sync_router, lectura_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

API_SOURCE_URL = os.getenv("API_SOURCE_URL", "http://localhost:8000")

app = FastAPI(
    title="Hospital API - Sync (BD2)",
    description="API de Sincronización para replicación de datos",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sync_router.router, prefix="/api", tags=["Sincronización"])
app.include_router(lectura_router.router, prefix="/api", tags=["Lectura"])

@app.get("/")
async def read_root():
    return {
        "mensaje": "API Sincronización",
        "versión": "1.0.0",
        "rol": "Cliente/Réplica (BD2)",
        "api_fuente": API_SOURCE_URL
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)