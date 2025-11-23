from fastapi import APIRouter
from controllers.lectura_controller import LecturaController
from models import DepartamentoResponse, MedicoResponse, ConsultaResponse
import logging
from typing import List

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/departamentos", response_model=dict)
async def get_departamentos():
    """GET /api/departamentos - Obtener todos los departamentos de BD2"""
    return await LecturaController.get_departamentos()

@router.get("/medicos", response_model=dict)
async def get_medicos():
    """GET /api/medicos - Obtener todos los médicos de BD2"""
    return await LecturaController.get_medicos()

@router.get("/consultas", response_model=dict)
async def get_consultas():
    """GET /api/consultas - Obtener todas las consultas de BD2"""
    return await LecturaController.get_consultas()