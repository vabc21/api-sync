import httpx
import logging
import os
from typing import List, Dict, Any, Optional
from utils import execute_query_json, get_db_connection
import json

logger = logging.getLogger(__name__)

API_SOURCE_URL = os.getenv("API_SOURCE_URL", "http://localhost:8000")

class SyncUtils:
    
    @staticmethod
    async def fetch_from_source(table: str, fecha_mayor: str) -> Optional[List[Dict[str, Any]]]:
        try:
            endpoint = f"{API_SOURCE_URL}/api/{table}"
            
            logger.info(f"🔗 Conectando a API Fuente: {endpoint}")
            logger.info(f"📅 Parámetro: fecha_mayor={fecha_mayor}")
            
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    endpoint,
                    params={"fecha_mayor": fecha_mayor}
                )
            
            if response.status_code != 200:
                logger.error(f"❌ Error HTTP {response.status_code}")
                return None
            
            data = response.json()

            if not data:
                logger.warning(f"⚠️ API retornó 0 registros")
                return []
            
            registros = data.get("datos", [])
            logger.info(f"✓ Recibidos {len(registros)} registros")
            
            return registros
        
        except httpx.TimeoutException:
            logger.error("❌ Timeout: API Fuente no responde")
            return None
        except httpx.ConnectError:
            logger.error(f"❌ No se pudo conectar a {API_SOURCE_URL}")
            return None
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return None
    
    @staticmethod
    async def check_id_exists(table: str, id: int) -> bool:
        try:
            query = f"SELECT COUNT(*) AS cnt FROM {table} WHERE id = ?"
            resultado_json = await execute_query_json(query, (id,))
            resultado = json.loads(resultado_json)
            
            if resultado:
                count = int(resultado[0].get('cnt', 0))
                return count > 0
            
            return False
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return False