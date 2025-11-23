import logging
from typing import Dict, Any
from datetime import datetime
from utils.sync_utils import SyncUtils
from utils.db_connection import execute_query_json
import json

logger = logging.getLogger(__name__)


class SyncController:

    @staticmethod
    async def sync(table: str, fecha_mayor: str) -> Dict[str, Any]:
        try:
            logger.info(f"🔄 Iniciando sincronización de '{table}'")

            tablas_validas = ['departamentos', 'medicos', 'consultas']
            if table not in tablas_validas:
                return {
                    "exito": False,
                    "codigo": 400,
                    "mensaje": f"Tabla inválida. Usar: {', '.join(tablas_validas)}"
                }

            try:
                datetime.strptime(fecha_mayor, '%Y-%m-%d')
            except ValueError:
                return {
                    "exito": False,
                    "codigo": 400,
                    "mensaje": "Formato de fecha inválido. Usar YYYY-MM-DD"
                }

            logger.info("📥 Descargando datos...")
            registros_recibidos = await SyncUtils.fetch_from_source(table, fecha_mayor)

            if registros_recibidos is None:
                return {
                    "exito": False,
                    "codigo": 500,
                    "mensaje": "Error al conectar con API Fuente"
                }

            recibidos = len(registros_recibidos)
            insertados = 0
            omitidos = 0
            errores = 0

            logger.info(f"⚙️  Procesando {recibidos} registros...")

            for i, registro in enumerate(registros_recibidos, 1):
                try:
                    id_original = registro.get('id')

                    existe = await SyncUtils.check_id_exists(table, id_original)

                    if existe:
                        omitidos += 1
                        continue

                    if table == 'departamentos':
                        success = await SyncController._insert_departamento(registro)
                    elif table == 'medicos':
                        success = await SyncController._insert_medico(registro)
                    elif table == 'consultas':
                        success = await SyncController._insert_consulta(registro)
                    else:
                        success = False

                    if success:
                        insertados += 1
                    else:
                        errores += 1

                except Exception as e:
                    logger.error(f"Error: {str(e)}")
                    errores += 1

            logger.info("✓ Sincronización completada")

            return {
                "exito": True,
                "codigo": 200,
                "mensaje": f"Sincronización de {table} completada",
                "datos": {
                    "tabla": table,
                    "recibidos": recibidos,
                    "insertados": insertados,
                    "omitidos": omitidos,
                    "errores": errores
                }
            }

        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return {
                "exito": False,
                "codigo": 500,
                "mensaje": f"Error: {str(e)}"
            }

    @staticmethod
    async def _insert_departamento(registro: Dict) -> bool:
        try:
            query = """
                INSERT INTO Departamentos (id, nombre, ubicacion, fecha_creacion)
                VALUES (?, ?, ?, ?)
            """
            params = (
                registro.get('id'),
                registro.get('nombre'),
                registro.get('ubicacion'),
                registro.get('fecha_creacion')
            )
            await execute_query_json(query, params, needs_commit=True)
            return True
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return False

    @staticmethod
    async def _insert_medico(registro: Dict) -> bool:
        try:
            query = """
                INSERT INTO Medicos (id, departamento_id, nombre, apellido, especialidad, fecha_registro)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            params = (
                registro.get('id'),
                registro.get('departamento_id'),
                registro.get('nombre'),
                registro.get('apellido'),
                registro.get('especialidad'),
                registro.get('fecha_registro')
            )
            await execute_query_json(query, params, needs_commit=True)
            return True
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return False

    @staticmethod
    async def _insert_consulta(registro: Dict) -> bool:
        try:
            query = """
                INSERT INTO Consultas (id, medico_id, nombre_paciente, diagnostico, fecha_consulta)
                VALUES (?, ?, ?, ?, ?)
            """
            params = (
                registro.get('id'),
                registro.get('medico_id'),
                registro.get('nombre_paciente'),
                registro.get('diagnostico'),
                registro.get('fecha_consulta')
            )
            await execute_query_json(query, params, needs_commit=True)
            return True
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return False
