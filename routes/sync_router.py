from fastapi import APIRouter, Query
from controllers.sync_controller import SyncController
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/sync")
async def sincronizar(
    table: str = Query(...,
                       description="Tabla: departamentos, medicos, consultas"),
    fecha_mayor: str = Query(..., description="Fecha YYYY-MM-DD")
):
    """
    POST /api/sync?table=medicos&fecha_mayor=2025-01-01

    Sincroniza una tabla desde API Fuente
    """
    logger.info(f"🔄 POST /api/sync - table={table}, fecha_mayor={fecha_mayor}")
    return await SyncController.sync(table, fecha_mayor)
