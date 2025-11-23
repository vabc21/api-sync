from utils.db_connection import execute_query_json
from models import DepartamentoResponse, MedicoResponse, ConsultaResponse
import logging
import json
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class LecturaController:

    @staticmethod
    async def get_departamentos() -> Dict[str, Any]:
        try:
            logger.info("📋 GET: Obteniendo departamentos de BD2")

            query = "SELECT * FROM Departamentos ORDER BY id"
            resultado_json = await execute_query_json(query)
            resultados = json.loads(resultado_json)

            # Validar con Pydantic
            departamentos_validados = [
                DepartamentoResponse(**dept) for dept in resultados
            ]

            return {
                "exito": True,
                "codigo": 200,
                "mensaje": f"{len(resultados)} departamentos encontrados",
                "datos": [dept.dict() for dept in departamentos_validados]
            }
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return {
                "exito": False,
                "codigo": 500,
                "mensaje": f"Error: {str(e)}"
            }

    @staticmethod
    async def get_medicos() -> Dict[str, Any]:
        try:
            logger.info("📋 GET: Obteniendo médicos de BD2")

            query = "SELECT * FROM Medicos ORDER BY id"
            resultado_json = await execute_query_json(query)
            resultados = json.loads(resultado_json)

            # Validar con Pydantic
            medicos_validados = [
                MedicoResponse(**med) for med in resultados
            ]

            return {
                "exito": True,
                "codigo": 200,
                "mensaje": f"{len(resultados)} médicos encontrados",
                "datos": [med.dict() for med in medicos_validados]
            }
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return {
                "exito": False,
                "codigo": 500,
                "mensaje": f"Error: {str(e)}"
            }

    @staticmethod
    async def get_consultas() -> Dict[str, Any]:
        try:
            logger.info("📋 GET: Obteniendo consultas de BD2")

            query = "SELECT * FROM Consultas ORDER BY id"
            resultado_json = await execute_query_json(query)
            resultados = json.loads(resultado_json)

            consultas_validadas = [
                ConsultaResponse(**cons) for cons in resultados
            ]

            return {
                "exito": True,
                "codigo": 200,
                "mensaje": f"{len(resultados)} consultas encontradas",
                "datos": [cons.dict() for cons in consultas_validadas]
            }
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return {
                "exito": False,
                "codigo": 500,
                "mensaje": f"Error: {str(e)}"
            }
