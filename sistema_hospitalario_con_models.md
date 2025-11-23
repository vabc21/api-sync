# Sistema Distribuido de Sincronización de Datos Hospitalarios

## 📋 Tabla de Contenidos

1. [Estructura General](#estructura-general)
2. [Base de Datos](#base-de-datos)
3. [Models (Pydantic)](#models-pydantic)
4. [API Fuente (BD1)](#api-fuente-bd1)
5. [API Sincronización (BD2)](#api-sincronización-bd2)
6. [Guía de Instalación](#guía-de-instalación)
7. [Pruebas](#pruebas)

---

## Estructura General

```
hospital-system/
├── db-scripts/
│   ├── init_bd1.sql
│   ├── init_bd2.sql
│   └── seed_data.sql
├── api-source/
│   ├── .env
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── models/
│   │   ├── __init__.py
│   │   ├── departamento.py
│   │   ├── medico.py
│   │   └── consulta.py
│   ├── controllers/
│   ├── routes/
│   └── utils/
└── api-sync/
    ├── .env
    ├── main.py
    ├── requirements.txt
    ├── Dockerfile
    ├── models/
    │   ├── __init__.py
    │   ├── departamento.py
    │   ├── medico.py
    │   └── consulta.py
    ├── controllers/
    ├── routes/
    └── utils/
```

---

## Base de Datos

### init_bd1.sql - Crear BD1 (con IDENTITY)

```sql
-- ===== CREAR BD1 =====
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'HospitalDB_Source')
BEGIN
    CREATE DATABASE HospitalDB_Source;
END
GO

USE HospitalDB_Source;
GO

-- ===== DEPARTAMENTOS =====
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Departamentos')
BEGIN
    CREATE TABLE Departamentos (
        id INT PRIMARY KEY IDENTITY(1,1),
        nombre VARCHAR(100) NOT NULL,
        ubicacion VARCHAR(100),
        fecha_creacion DATETIME NOT NULL DEFAULT GETDATE()
    );
    
    CREATE UNIQUE INDEX IX_Departamentos_Nombre ON Departamentos(nombre);
    CREATE INDEX IX_Departamentos_Fecha ON Departamentos(fecha_creacion);
    
    PRINT 'Tabla Departamentos creada';
END
GO

-- ===== MEDICOS =====
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Medicos')
BEGIN
    CREATE TABLE Medicos (
        id INT PRIMARY KEY IDENTITY(1,1),
        departamento_id INT NOT NULL,
        nombre VARCHAR(100) NOT NULL,
        apellido VARCHAR(100) NOT NULL,
        especialidad VARCHAR(100),
        fecha_registro DATETIME NOT NULL DEFAULT GETDATE(),
        
        CONSTRAINT FK_Medicos_Departamentos 
            FOREIGN KEY (departamento_id) 
            REFERENCES Departamentos(id) 
            ON DELETE CASCADE
    );
    
    CREATE INDEX IX_Medicos_DepartamentoId ON Medicos(departamento_id);
    CREATE INDEX IX_Medicos_Fecha ON Medicos(fecha_registro);
    
    PRINT 'Tabla Medicos creada';
END
GO

-- ===== CONSULTAS =====
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Consultas')
BEGIN
    CREATE TABLE Consultas (
        id INT PRIMARY KEY IDENTITY(1,1),
        medico_id INT NOT NULL,
        nombre_paciente VARCHAR(200) NOT NULL,
        diagnostico TEXT,
        fecha_consulta DATETIME NOT NULL DEFAULT GETDATE(),
        
        CONSTRAINT FK_Consultas_Medicos 
            FOREIGN KEY (medico_id) 
            REFERENCES Medicos(id) 
            ON DELETE CASCADE
    );
    
    CREATE INDEX IX_Consultas_MedicoId ON Consultas(medico_id);
    CREATE INDEX IX_Consultas_Fecha ON Consultas(fecha_consulta);
    
    PRINT 'Tabla Consultas creada';
END
GO
```

### init_bd2.sql - Crear BD2 (sin IDENTITY)

```sql
-- ===== CREAR BD2 =====
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'HospitalDB_Replica')
BEGIN
    CREATE DATABASE HospitalDB_Replica;
END
GO

USE HospitalDB_Replica;
GO

-- ===== DEPARTAMENTOS (SIN IDENTITY) =====
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Departamentos')
BEGIN
    CREATE TABLE Departamentos (
        id INT PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        ubicacion VARCHAR(100),
        fecha_creacion DATETIME NOT NULL
    );
    
    CREATE UNIQUE INDEX IX_Departamentos_Nombre ON Departamentos(nombre);
    CREATE INDEX IX_Departamentos_Fecha ON Departamentos(fecha_creacion);
    
    PRINT 'Tabla Departamentos creada (SIN IDENTITY)';
END
GO

-- ===== MEDICOS (SIN IDENTITY) =====
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Medicos')
BEGIN
    CREATE TABLE Medicos (
        id INT PRIMARY KEY,
        departamento_id INT NOT NULL,
        nombre VARCHAR(100) NOT NULL,
        apellido VARCHAR(100) NOT NULL,
        especialidad VARCHAR(100),
        fecha_registro DATETIME NOT NULL,
        
        CONSTRAINT FK_Medicos_Departamentos 
            FOREIGN KEY (departamento_id) 
            REFERENCES Departamentos(id) 
            ON DELETE CASCADE
    );
    
    CREATE INDEX IX_Medicos_DepartamentoId ON Medicos(departamento_id);
    CREATE INDEX IX_Medicos_Fecha ON Medicos(fecha_registro);
    
    PRINT 'Tabla Medicos creada (SIN IDENTITY)';
END
GO

-- ===== CONSULTAS (SIN IDENTITY) =====
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Consultas')
BEGIN
    CREATE TABLE Consultas (
        id INT PRIMARY KEY,
        medico_id INT NOT NULL,
        nombre_paciente VARCHAR(200) NOT NULL,
        diagnostico TEXT,
        fecha_consulta DATETIME NOT NULL,
        
        CONSTRAINT FK_Consultas_Medicos 
            FOREIGN KEY (medico_id) 
            REFERENCES Medicos(id) 
            ON DELETE CASCADE
    );
    
    CREATE INDEX IX_Consultas_MedicoId ON Consultas(medico_id);
    CREATE INDEX IX_Consultas_Fecha ON Consultas(fecha_consulta);
    
    PRINT 'Tabla Consultas creada (SIN IDENTITY)';
END
GO
```

### seed_data.sql - Cargar datos de prueba

```sql
USE HospitalDB_Source;
GO

-- ===== DEPARTAMENTOS =====
INSERT INTO Departamentos (nombre, ubicacion, fecha_creacion) VALUES
('Cardiología', 'Piso 3', '2024-01-15'),
('Pediatría', 'Piso 2', '2024-01-20'),
('Urgencias', 'Piso 1', '2024-01-25'),
('Radiología', 'Sótano 1', '2024-02-01'),
('Neurología', 'Piso 4', '2024-02-10'),
('Oncología', 'Piso 5', '2024-02-15'),
('Traumatología', 'Piso 2', '2024-03-01'),
('Ginecología', 'Piso 3', '2024-03-10'),
('Oftalmología', 'Piso 1', '2024-03-20'),
('Dermatología', 'Piso 4', '2024-04-01');

-- ===== MÉDICOS (1000) =====
DECLARE @i INT = 1;
WHILE @i <= 1000
BEGIN
    INSERT INTO Medicos (departamento_id, nombre, apellido, especialidad, fecha_registro)
    SELECT 
        ((@i-1)/100)+1,
        'Médico_' + CAST(@i AS VARCHAR(10)),
        'Apellido_' + CAST(@i AS VARCHAR(10)),
        'Especialidad_' + CAST(((@i-1)/100)+1 AS VARCHAR(10)),
        DATEADD(DAY, (@i % 180), '2024-01-20');
    SET @i = @i + 1;
END

-- ===== CONSULTAS (500) =====
DECLARE @j INT = 1;
WHILE @j <= 500
BEGIN
    INSERT INTO Consultas (medico_id, nombre_paciente, diagnostico, fecha_consulta)
    VALUES 
    (
        ((@j % 1000) + 1),
        'Paciente_' + CAST(@j AS VARCHAR(10)),
        'Diagnóstico_' + CAST((@j % 10) AS VARCHAR(10)),
        DATEADD(DAY, (@j % 200), '2024-06-01')
    );
    SET @j = @j + 1;
END

PRINT 'Carga de datos completada';
SELECT 'Departamentos' AS Tabla, COUNT(*) AS Total FROM Departamentos
UNION ALL
SELECT 'Médicos', COUNT(*) FROM Medicos
UNION ALL
SELECT 'Consultas', COUNT(*) FROM Consultas;
GO
```

---

## Models (Pydantic)

### models/__init__.py

```python
from .departamento import DepartamentoBase, DepartamentoCreate, DepartamentoResponse
from .medico import MedicoBase, MedicoCreate, MedicoResponse
from .consulta import ConsultaBase, ConsultaCreate, ConsultaResponse

__all__ = [
    "DepartamentoBase",
    "DepartamentoCreate",
    "DepartamentoResponse",
    "MedicoBase",
    "MedicoCreate",
    "MedicoResponse",
    "ConsultaBase",
    "ConsultaCreate",
    "ConsultaResponse"
]
```

### models/departamento.py

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re

class DepartamentoBase(BaseModel):
    """Modelo base para Departamento con validaciones"""
    nombre: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nombre del departamento",
        pattern=r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s\-]{1,100}$",
        examples=["Cardiología", "Pediatría", "Urgencias"]
    )
    
    ubicacion: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Ubicación física del departamento",
        examples=["Piso 3", "Sótano 1", "Ala Este"]
    )
    
    @field_validator('nombre')
    @classmethod
    def validar_nombre(cls, v):
        """Validar que el nombre solo contenga letras, espacios y guiones"""
        if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s\-]{1,100}$", v):
            raise ValueError('El nombre debe contener solo letras, espacios y guiones')
        return v.strip()
    
    @field_validator('ubicacion')
    @classmethod
    def validar_ubicacion(cls, v):
        """Validar ubicación"""
        if v:
            if not re.match(r"^[A-Za-z0-9ÁÉÍÓÚáéíóúÑñÜü\s\-\.]{1,100}$", v):
                raise ValueError('Ubicación inválida')
            return v.strip()
        return v


class DepartamentoCreate(DepartamentoBase):
    """Modelo para crear un departamento"""
    pass


class DepartamentoResponse(DepartamentoBase):
    """Modelo para respuesta de departamento"""
    id: int = Field(
        description="ID del departamento (autoincremental)",
        examples=[1, 2, 3]
    )
    fecha_creacion: datetime = Field(
        description="Fecha de creación del departamento",
        examples=["2024-01-15T10:30:00"]
    )
    
    class Config:
        from_attributes = True
```

### models/medico.py

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re

class MedicoBase(BaseModel):
    """Modelo base para Médico con validaciones"""
    departamento_id: int = Field(
        ...,
        gt=0,
        description="ID del departamento",
        examples=[1, 2, 3]
    )
    
    nombre: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nombre del médico",
        pattern=r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s]{1,100}$",
        examples=["Juan", "María", "Carlos"]
    )
    
    apellido: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Apellido del médico",
        pattern=r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s]{1,100}$",
        examples=["García", "López", "Martínez"]
    )
    
    especialidad: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Especialidad médica",
        examples=["Cardiología", "Pediatría", "Neurología"]
    )
    
    @field_validator('nombre')
    @classmethod
    def validar_nombre(cls, v):
        """Validar que el nombre solo contenga letras y espacios"""
        if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s]{1,100}$", v):
            raise ValueError('El nombre debe contener solo letras y espacios')
        return v.strip()
    
    @field_validator('apellido')
    @classmethod
    def validar_apellido(cls, v):
        """Validar que el apellido solo contenga letras y espacios"""
        if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s]{1,100}$", v):
            raise ValueError('El apellido debe contener solo letras y espacios')
        return v.strip()
    
    @field_validator('especialidad')
    @classmethod
    def validar_especialidad(cls, v):
        """Validar especialidad"""
        if v:
            if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s]{1,100}$", v):
                raise ValueError('Especialidad inválida')
            return v.strip()
        return v


class MedicoCreate(MedicoBase):
    """Modelo para crear un médico"""
    pass


class MedicoResponse(MedicoBase):
    """Modelo para respuesta de médico"""
    id: int = Field(
        description="ID del médico (autoincremental)",
        examples=[1, 2, 3]
    )
    fecha_registro: datetime = Field(
        description="Fecha de registro del médico",
        examples=["2024-01-20T14:00:00"]
    )
    
    class Config:
        from_attributes = True
```

### models/consulta.py

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re

class ConsultaBase(BaseModel):
    """Modelo base para Consulta con validaciones"""
    medico_id: int = Field(
        ...,
        gt=0,
        description="ID del médico",
        examples=[1, 2, 3]
    )
    
    nombre_paciente: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Nombre del paciente",
        pattern=r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s]{1,200}$",
        examples=["Pedro González", "Ana María Ruiz"]
    )
    
    diagnostico: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Diagnóstico de la consulta",
        examples=["Hipertensión", "Diabetes Tipo 2"]
    )
    
    @field_validator('nombre_paciente')
    @classmethod
    def validar_nombre_paciente(cls, v):
        """Validar nombre del paciente"""
        if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s]{1,200}$", v):
            raise ValueError('El nombre del paciente debe contener solo letras y espacios')
        return v.strip()
    
    @field_validator('diagnostico')
    @classmethod
    def validar_diagnostico(cls, v):
        """Validar diagnóstico"""
        if v:
            if len(v.strip()) == 0:
                return None
            if not re.match(r"^[A-Za-z0-9ÁÉÍÓÚáéíóúÑñÜü\s\-\.]{1,500}$", v):
                raise ValueError('Diagnóstico inválido')
            return v.strip()
        return v


class ConsultaCreate(ConsultaBase):
    """Modelo para crear una consulta"""
    pass


class ConsultaResponse(ConsultaBase):
    """Modelo para respuesta de consulta"""
    id: int = Field(
        description="ID de la consulta (autoincremental)",
        examples=[1, 2, 3]
    )
    fecha_consulta: datetime = Field(
        description="Fecha de la consulta",
        examples=["2024-06-15T10:00:00"]
    )
    
    class Config:
        from_attributes = True
```

---

## API Fuente (BD1)

### .env

```
SQL_DRIVER={ODBC Driver 17 for SQL Server}
SQL_SERVER=tcp:tu-servidor.database.windows.net,1433
SQL_DATABASE=HospitalDB_Source
SQL_USERNAME=usuario
SQL_PASSWORD=TuContraseña123!
API_PORT=8000
API_HOST=0.0.0.0
LOG_LEVEL=INFO
```

### main.py

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from routes import departamentos_router, medicos_router, consultas_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Iniciando API Fuente - Hospital Management System")
    logger.info("📊 Base de Datos: HospitalDB_Source (BD1)")
    logger.info("📚 Documentación: http://localhost:8000/docs")
    yield
    logger.info("🛑 Apagando API Fuente")

app = FastAPI(
    title="Hospital API - Source (BD1)",
    description="API Fuente para sincronización de datos hospitalarios",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(departamentos_router.router, prefix="/api", tags=["Departamentos"])
app.include_router(medicos_router.router, prefix="/api", tags=["Médicos"])
app.include_router(consultas_router.router, prefix="/api", tags=["Consultas"])

@app.get("/")
async def read_root():
    return {
        "mensaje": "API Fuente - Hospital Management System",
        "versión": "1.0.0",
        "estado": "operativo ✓",
        "rol": "Servidor Principal (BD1)",
        "documentación": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "estado": "ok ✓",
        "servicio": "API Fuente",
        "base_datos": "HospitalDB_Source (BD1)"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

### utils/db_connection.py

```python
from dotenv import load_dotenv
import os
import pyodbc
import logging
import json
from typing import Optional

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

driver = os.getenv("SQL_DRIVER", "{ODBC Driver 17 for SQL Server}")
server = os.getenv("SQL_SERVER", "localhost")
database = os.getenv("SQL_DATABASE", "HospitalDB_Source")
username = os.getenv("SQL_USERNAME", "sa")
password = os.getenv("SQL_PASSWORD", "password")

connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"

async def get_db_connection():
    try:
        logger.info(f"🔌 Intentando conectar a: {database}")
        conn = pyodbc.connect(connection_string, timeout=10)
        logger.info("✓ Conexión exitosa")
        return conn
    except pyodbc.Error as e:
        logger.error(f"❌ Error de conexión: {str(e)}")
        raise Exception(f"Error de conexión: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Error inesperado: {str(e)}")
        raise

async def execute_query_json(
    sql_template: str,
    params: Optional[tuple] = None,
    needs_commit: bool = False
) -> str:
    conn = None
    cursor = None
    
    try:
        conn = await get_db_connection()
        cursor = conn.cursor()
        
        param_info = "(sin parámetros)" if not params else f"(con {len(params)} parámetros)"
        logger.info(f"📋 Ejecutando consulta {param_info}")
        
        if params:
            cursor.execute(sql_template, params)
        else:
            cursor.execute(sql_template)
        
        results = []
        if cursor.description:
            columns = [column[0] for column in cursor.description]
            logger.info(f"✓ Columnas: {columns}")
            
            for row in cursor.fetchall():
                processed_row = [
                    str(item) if isinstance(item, (bytes, bytearray)) else item 
                    for item in row
                ]
                results.append(dict(zip(columns, processed_row)))
            
            logger.info(f"✓ Filas recuperadas: {len(results)}")
        else:
            logger.info(f"✓ Filas afectadas: {cursor.rowcount}")
        
        if needs_commit:
            logger.info("💾 Realizando commit")
            conn.commit()
            logger.info("✓ Commit exitoso")
        
        return json.dumps(results, default=str)
    
    except pyodbc.Error as e:
        logger.error(f"❌ Error SQL: {str(e)}")
        if conn and needs_commit:
            try:
                conn.rollback()
            except:
                pass
        raise Exception(f"Error en consulta SQL: {str(e)}") from e
    
    except Exception as e:
        logger.error(f"❌ Error inesperado: {str(e)}")
        raise
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            logger.info("🔌 Conexión cerrada")
```

### controllers/departamentos_controller.py

```python
from utils.db_connection import execute_query_json
from models import DepartamentoCreate, DepartamentoResponse
import logging
import json
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class DepartamentosController:
    
    @staticmethod
    async def get_all(fecha_mayor: Optional[str] = None) -> Dict[str, Any]:
        try:
            logger.info("📋 GET: Obteniendo todos los departamentos")
            
            if fecha_mayor:
                logger.info(f"   Aplicando filtro: fecha_creacion > {fecha_mayor}")
                query = """
                    SELECT id, nombre, ubicacion, fecha_creacion
                    FROM Departamentos
                    WHERE fecha_creacion > ?
                    ORDER BY fecha_creacion DESC
                """
                resultado_json = await execute_query_json(query, (fecha_mayor,))
            else:
                query = """
                    SELECT id, nombre, ubicacion, fecha_creacion
                    FROM Departamentos
                    ORDER BY id
                """
                resultado_json = await execute_query_json(query)
            
            resultados = json.loads(resultado_json)
            logger.info(f"✓ Encontrados {len(resultados)} departamentos")
            
            return {
                "éxito": True,
                "código": 200,
                "mensaje": f"Se encontraron {len(resultados)} departamentos",
                "datos": resultados
            }
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return {
                "éxito": False,
                "código": 500,
                "mensaje": f"Error: {str(e)}"
            }
    
    @staticmethod
    async def get_by_id(id: int) -> Dict[str, Any]:
        try:
            logger.info(f"📋 GET: Obteniendo departamento {id}")
            
            query = """
                SELECT id, nombre, ubicacion, fecha_creacion
                FROM Departamentos
                WHERE id = ?
            """
            resultado_json = await execute_query_json(query, (id,))
            resultados = json.loads(resultado_json)
            
            if not resultados:
                return {
                    "éxito": False,
                    "código": 404,
                    "mensaje": f"Departamento {id} no encontrado"
                }
            
            return {
                "éxito": True,
                "código": 200,
                "mensaje": "Departamento encontrado",
                "datos": resultados[0]
            }
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return {
                "éxito": False,
                "código": 500,
                "mensaje": f"Error: {str(e)}"
            }
    
    @staticmethod
    async def create(departamento: DepartamentoCreate) -> Dict[str, Any]:
        try:
            logger.info(f"➕ POST: Creando departamento: {departamento.nombre}")
            
            query = """
                INSERT INTO Departamentos (nombre, ubicacion, fecha_creacion)
                VALUES (?, ?, GETDATE())
            """
            await execute_query_json(
                query, 
                (departamento.nombre, departamento.ubicacion), 
                needs_commit=True
            )
            
            query_last = "SELECT @@IDENTITY AS id"
            resultado_json = await execute_query_json(query_last)
            resultado = json.loads(resultado_json)
            new_id = int(resultado[0]['id']) if resultado else None
            
            logger.info(f"✓ Departamento creado con ID: {new_id}")
            
            return {
                "éxito": True,
                "código": 201,
                "mensaje": "Departamento creado exitosamente",
                "datos": {
                    "id": new_id,
                    "nombre": departamento.nombre,
                    "ubicacion": departamento.ubicacion
                }
            }
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return {
                "éxito": False,
                "código": 500,
                "mensaje": f"Error: {str(e)}"
            }
    
    @staticmethod
    async def update(id: int, departamento: DepartamentoCreate) -> Dict[str, Any]:
        try:
            logger.info(f"✏️  PUT: Actualizando departamento {id}")
            
            updates = []
            params = []
            
            if departamento.nombre:
                updates.append("nombre = ?")
                params.append(departamento.nombre)
            if departamento.ubicacion is not None:
                updates.append("ubicacion = ?")
                params.append(departamento.ubicacion)
            
            if not updates:
                return {
                    "éxito": False,
                    "código": 400,
                    "mensaje": "No hay campos para actualizar"
                }
            
            params.append(id)
            query = f"UPDATE Departamentos SET {', '.join(updates)} WHERE id = ?"
            
            await execute_query_json(query, tuple(params), needs_commit=True)
            
            return {
                "éxito": True,
                "código": 200,
                "mensaje": "Departamento actualizado exitosamente"
            }
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return {
                "éxito": False,
                "código": 500,
                "mensaje": f"Error: {str(e)}"
            }
    
    @staticmethod
    async def delete(id: int) -> Dict[str, Any]:
        try:
            logger.info(f"🗑️  DELETE: Eliminando departamento {id}")
            
            query = "DELETE FROM Departamentos WHERE id = ?"
            await execute_query_json(query, (id,), needs_commit=True)
            
            return {
                "éxito": True,
                "código": 200,
                "mensaje": "Departamento eliminado exitosamente"
            }
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return {
                "éxito": False,
                "código": 500,
                "mensaje": f"Error: {str(e)}"
            }
```

### controllers/medicos_controller.py

```python
from utils.db_connection import execute_query_json
from models import MedicoCreate, MedicoResponse
import logging
import json
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class MedicosController:
    
    @staticmethod
    async def get_all(fecha_mayor: Optional[str] = None) -> Dict[str, Any]:
        try:
            logger.info("📋 GET: Obteniendo todos los médicos")
            
            if fecha_mayor:
                logger.info(f"   Filtrando por fecha_registro > {fecha_mayor}")
                query = """
                    SELECT id, departamento_id, nombre, apellido, especialidad, fecha_registro
                    FROM Medicos
                    WHERE fecha_registro > ?
                    ORDER BY fecha_registro DESC
                """
                resultado_json = await execute_query_json(query, (fecha_mayor,))
            else:
                query = """
                    SELECT id, departamento_id, nombre, apellido, especialidad, fecha_registro
                    FROM Medicos
                    ORDER BY id
                """
                resultado_json = await execute_query_json(query)
            
            resultados = json.loads(resultado_json)
            return {
                "éxito": True,
                "código": 200,
                "mensaje": f"Se encontraron {len(resultados)} médicos",
                "datos": resultados
            }
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return {
                "éxito": False,
                "código": 500,
                "mensaje": f"Error: {str(e)}"
            }
    
    @staticmethod
    async def get_by_id(id: int) -> Dict[str, Any]:
        try:
            logger.info(f"📋 GET: Obteniendo médico {id}")
            
            query = """
                SELECT id, departamento_id, nombre, apellido, especialidad, fecha_registro
                FROM Medicos
                WHERE id = ?
            """
            resultado_json = await execute_query_json(query, (id,))
            resultados = json.loads(resultado_json)
            
            if not resultados:
                return {
                    "éxito": False,
                    "código": 404,
                    "mensaje": f"Médico {id} no encontrado"
                }
            
            return {
                "éxito": True,
                "código": 200,
                "mensaje": "Médico encontrado",
                "datos": resultados[0]
            }
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return {
                "éxito": False,
                "código": 500,
                "mensaje": f"Error: {str(e)}"
            }
    
    @staticmethod
    async def create(medico: MedicoCreate) -> Dict[str, Any]:
        try:
            logger.info(f"➕ POST: Creando médico: {medico.nombre} {medico.apellido}")
            
            query = """
                INSERT INTO Medicos (departamento_id, nombre, apellido, especialidad, fecha_registro)
                VALUES (?, ?, ?, ?, GETDATE())
            """
            await execute_query_json(
                query, 
                (medico.departamento_id, medico.nombre, medico.apellido, medico.especialidad), 
                needs_commit=True
            )
            
            query_last = "SELECT @@IDENTITY AS id"
            resultado_json = await execute_query_json(query_last)
            resultado = json.loads(resultado_json)
            new_id = int(resultado[0]['id']) if resultado else None
            
            return {
                "éxito": True,
                "código": 201,
                "mensaje": "Médico creado exitosamente",
                "datos": {"id": new_id}
            }
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return {
                "éxito": False,
                "código": 500,
                "mensaje": f"Error: {str(e)}"
            }
    
    @staticmethod
    async def update(id: int, medico: MedicoCreate) -> Dict[str, Any]:
        try:
            logger.info(f"✏️  PUT: Actualizando médico {id}")
            
            updates = []
            params = []
            
            if medico.departamento_id:
                updates.append("departamento_id = ?")
                params.append(medico.departamento_id)
            if medico.nombre:
                updates.append("nombre = ?")
                params.append(medico.nombre)
            if medico.apellido:
                updates.append("apellido = ?")
                params.append(medico.apellido)
            if medico.especialidad is not None:
                updates.append("especialidad = ?")
                params.append(medico.especialidad)
            
            if not updates:
                return {
                    "éxito": False,
                    "código": 400,
                    "mensaje": "No hay campos para actualizar"
                }
            
            params.append(id)
            query = f"UPDATE Medicos SET {', '.join(updates)} WHERE id = ?"
            
            await execute_query_json(query, tuple(params), needs_commit=True)
            
            return {
                "éxito": True,
                "código": 200,
                "mensaje": "Médico actualizado exitosamente"
            }
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return {
                "éxito": False,
                "código": 500,
                "mensaje": f"Error: {str(e)}"
            }
    
    @staticmethod
    async def delete(id: int) -> Dict[str, Any]:
        try:
            logger.info(f"🗑️  DELETE: Eliminando médico {id}")
            
            query = "DELETE FROM Medicos WHERE id = ?"
            await execute_query_json(query, (id,), needs_commit=True)
            
            return {
                "éxito": True,
                "código": 200,
                "mensaje": "Médico eliminado exitosamente"
            }
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return {
                "éxito": False,
                "código": 500,
                "mensaje": f"Error: {str(e)}"
            }
```

### controllers/consultas_controller.py

```python
from utils.db_connection import execute_query_json
from models import ConsultaCreate, ConsultaResponse
import logging
import json
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ConsultasController:
    
    @staticmethod
    async def get_all(fecha_mayor: Optional[str] = None) -> Dict[str, Any]:
        try:
            logger.info("📋 GET: Obteniendo todas las consultas")
            
            if fecha_mayor:
                query = """
                    SELECT id, medico_id, nombre_paciente, diagnostico, fecha_consulta
                    FROM Consultas
                    WHERE fecha_consulta > ?
                    ORDER BY fecha_consulta DESC
                """
                resultado_json = await execute_query_json(query, (fecha_mayor,))
            else:
                query = """
                    SELECT id, medico_id, nombre_paciente, diagnostico, fecha_consulta
                    FROM Consultas
                    ORDER BY id
                """
                resultado_json = await execute_query_json(query)
            
            resultados = json.loads(resultado_json)
            return {
                "éxito": True,
                "código": 200,
                "mensaje": f"Se encontraron {len(resultados)} consultas",
                "datos": resultados
            }
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return {
                "éxito": False,
                "código": 500,
                "mensaje": f"Error: {str(e)}"
            }
    
    @staticmethod
    async def get_by_id(id: int) -> Dict[str, Any]:
        try:
            logger.info(f"📋 GET: Obteniendo consulta {id}")
            
            query = """
                SELECT id, medico_id, nombre_paciente, diagnostico, fecha_consulta
                FROM Consultas
                WHERE id = ?
            """
            resultado_json = await execute_query_json(query, (id,))
            resultados = json.loads(resultado_json)
            
            if not resultados:
                return {
                    "éxito": False,
                    "código": 404,
                    "mensaje": f"Consulta {id} no encontrada"
                }
            
            return {
                "éxito": True,
                "código": 200,
                "mensaje": "Consulta encontrada",
                "datos": resultados[0]
            }
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return {
                "éxito": False,
                "código": 500,
                "mensaje": f"Error: {str(e)}"
            }
    
    @staticmethod
    async def create(consulta: ConsultaCreate) -> Dict[str, Any]:
        try:
            logger.info(f"➕ POST: Creando consulta para: {consulta.nombre_paciente}")
            
            query = """
                INSERT INTO Consultas (medico_id, nombre_paciente, diagnostico, fecha_consulta)
                VALUES (?, ?, ?, GETDATE())
            """
            await execute_query_json(
                query, 
                (consulta.medico_id, consulta.nombre_paciente, consulta.diagnostico), 
                needs_commit=True
            )
            
            query_last = "SELECT @@IDENTITY AS id"
            resultado_json = await execute_query_json(query_last)
            resultado = json.loads(resultado_json)
            new_id = int(resultado[0]['id']) if resultado else None
            
            return {
                "éxito": True,
                "código": 201,
                "mensaje": "Consulta creada exitosamente",
                "datos": {"id": new_id}
            }
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return {
                "éxito": False,
                "código": 500,
                "mensaje": f"Error: {str(e)}"
            }
    
    @staticmethod
    async def update(id: int, consulta: ConsultaCreate) -> Dict[str, Any]:
        try:
            logger.info(f"✏️  PUT: Actualizando consulta {id}")
            
            updates = []
            params = []
            
            if consulta.medico_id:
                updates.append("medico_id = ?")
                params.append(consulta.medico_id)
            if consulta.nombre_paciente:
                updates.append("nombre_paciente = ?")
                params.append(consulta.nombre_paciente)
            if consulta.diagnostico is not None:
                updates.append("diagnostico = ?")
                params.append(consulta.diagnostico)
            
            if not updates:
                return {
                    "éxito": False,
                    "código": 400,
                    "mensaje": "No hay campos para actualizar"
                }
            
            params.append(id)
            query = f"UPDATE Consultas SET {', '.join(updates)} WHERE id = ?"
            
            await execute_query_json(query, tuple(params), needs_commit=True)
            
            return {
                "éxito": True,
                "código": 200,
                "mensaje": "Consulta actualizada exitosamente"
            }
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return {
                "éxito": False,
                "código": 500,
                "mensaje": f"Error: {str(e)}"
            }
    
    @staticmethod
    async def delete(id: int) -> Dict[str, Any]:
        try:
            logger.info(f"🗑️  DELETE: Eliminando consulta {id}")
            
            query = "DELETE FROM Consultas WHERE id = ?"
            await execute_query_json(query, (id,), needs_commit=True)
            
            return {
                "éxito": True,
                "código": 200,
                "mensaje": "Consulta eliminada exitosamente"
            }
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return {
                "éxito": False,
                "código": 500,
                "mensaje": f"Error: {str(e)}"
            }
```

### routes/departamentos_router.py

```python
from fastapi import APIRouter, Query
from controllers.departamentos_controller import DepartamentosController
from models import DepartamentoCreate, DepartamentoResponse
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/departamentos", response_model=dict)
async def get_departamentos(fecha_mayor: Optional[str] = Query(None)):
    """GET /api/departamentos - Obtiene todos los departamentos"""
    logger.info(f"GET /api/departamentos")
    return await DepartamentosController.get_all(fecha_mayor)

@router.get("/departamentos/{id}", response_model=dict)
async def get_departamento(id: int):
    """GET /api/departamentos/{id}"""
    logger.info(f"GET /api/departamentos/{id}")
    return await DepartamentosController.get_by_id(id)

@router.post("/departamentos", status_code=201, response_model=dict)
async def create_departamento(departamento: DepartamentoCreate):
    """POST /api/departamentos"""
    logger.info(f"POST /api/departamentos")
    return await DepartamentosController.create(departamento)

@router.put("/departamentos/{id}", response_model=dict)
async def update_departamento(id: int, departamento: DepartamentoCreate):
    """PUT /api/departamentos/{id}"""
    logger.info(f"PUT /api/departamentos/{id}")
    return await DepartamentosController.update(id, departamento)

@router.delete("/departamentos/{id}", response_model=dict)
async def delete_departamento(id: int):
    """DELETE /api/departamentos/{id}"""
    logger.info(f"DELETE /api/departamentos/{id}")
    return await DepartamentosController.delete(id)
```

### routes/medicos_router.py

```python
from fastapi import APIRouter, Query
from controllers.medicos_controller import MedicosController
from models import MedicoCreate, MedicoResponse
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/medicos", response_model=dict)
async def get_medicos(fecha_mayor: Optional[str] = Query(None)):
    """GET /api/medicos"""
    return await MedicosController.get_all(fecha_mayor)

@router.get("/medicos/{id}", response_model=dict)
async def get_medico(id: int):
    """GET /api/medicos/{id}"""
    return await MedicosController.get_by_id(id)

@router.post("/medicos", status_code=201, response_model=dict)
async def create_medico(medico: MedicoCreate):
    """POST /api/medicos"""
    return await MedicosController.create(medico)

@router.put("/medicos/{id}", response_model=dict)
async def update_medico(id: int, medico: MedicoCreate):
    """PUT /api/medicos/{id}"""
    return await MedicosController.update(id, medico)

@router.delete("/medicos/{id}", response_model=dict)
async def delete_medico(id: int):
    """DELETE /api/medicos/{id}"""
    return await MedicosController.delete(id)
```

### routes/consultas_router.py

```python
from fastapi import APIRouter, Query
from controllers.consultas_controller import ConsultasController
from models import ConsultaCreate, ConsultaResponse
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/consultas", response_model=dict)
async def get_consultas(fecha_mayor: Optional[str] = Query(None)):
    """GET /api/consultas"""
    return await ConsultasController.get_all(fecha_mayor)

@router.get("/consultas/{id}", response_model=dict)
async def get_consulta(id: int):
    """GET /api/consultas/{id}"""
    return await ConsultasController.get_by_id(id)

@router.post("/consultas", status_code=201, response_model=dict)
async def create_consulta(consulta: ConsultaCreate):
    """POST /api/consultas"""
    return await ConsultasController.create(consulta)

@router.put("/consultas/{id}", response_model=dict)
async def update_consulta(id: int, consulta: ConsultaCreate):
    """PUT /api/consultas/{id}"""
    return await ConsultasController.update(id, consulta)

@router.delete("/consultas/{id}", response_model=dict)
async def delete_consulta(id: int):
    """DELETE /api/consultas/{id}"""
    return await ConsultasController.delete(id)
```

### utils/__init__.py

```python
from .db_connection import execute_query_json, get_db_connection

__all__ = ["execute_query_json", "get_db_connection"]
```

### controllers/__init__.py

```python
from .departamentos_controller import DepartamentosController
from .medicos_controller import MedicosController
from .consultas_controller import ConsultasController

__all__ = ["DepartamentosController", "MedicosController", "ConsultasController"]
```

### routes/__init__.py

```python
from . import departamentos_router
from . import medicos_router
from . import consultas_router

__all__ = ["departamentos_router", "medicos_router", "consultas_router"]
```

### requirements.txt

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-dotenv==1.0.0
pyodbc==5.0.1
pydantic==2.4.2
python-dateutil==2.8.2
```

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    unixodbc-dev \
    && apt-get clean

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## API Sincronización (BD2)

### .env (API Sync)

```
SQL_DRIVER={ODBC Driver 17 for SQL Server}
SQL_SERVER=tcp:tu-servidor.database.windows.net,1433
SQL_DATABASE=HospitalDB_Replica
SQL_USERNAME=usuario
SQL_PASSWORD=TuContraseña123!
API_SOURCE_URL=http://localhost:8000
API_PORT=8001
API_HOST=0.0.0.0
LOG_LEVEL=INFO
```

### main.py (API Sync)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os

from routes import sync_router, lectura_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

API_SOURCE_URL = os.getenv("API_SOURCE_URL", "http://localhost:8000")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Iniciando API Sincronización")
    logger.info(f"🔗 Conectada a API Fuente: {API_SOURCE_URL}")
    yield
    logger.info("🛑 Apagando API Sincronización")

app = FastAPI(
    title="Hospital API - Sync (BD2)",
    description="API de Sincronización para replicación de datos",
    version="1.0.0",
    lifespan=lifespan
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

@app.get("/health")
async def health_check():
    return {
        "estado": "ok ✓",
        "servicio": "API Sync",
        "base_datos": "HospitalDB_Replica (BD2)"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
```

### utils/sync_utils.py

```python
import httpx
import logging
import os
from typing import List, Dict, Any, Optional
from utils.db_connection import execute_query_json
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
            
            if not data.get("éxito"):
                logger.warning(f"⚠️  Error: {data.get('mensaje')}")
                return None
            
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
```

### controllers/sync_controller.py

```python
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
                    "éxito": False,
                    "código": 400,
                    "mensaje": f"Tabla inválida. Usar: {', '.join(tablas_validas)}"
                }
            
            try:
                datetime.strptime(fecha_mayor, '%Y-%m-%d')
            except ValueError:
                return {
                    "éxito": False,
                    "código": 400,
                    "mensaje": "Formato de fecha inválido. Usar YYYY-MM-DD"
                }
            
            logger.info(f"📥 Descargando datos...")
            registros_recibidos = await SyncUtils.fetch_from_source(table, fecha_mayor)
            
            if registros_recibidos is None:
                return {
                    "éxito": False,
                    "código": 500,
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
            
            logger.info(f"✓ Sincronización completada")
            
            return {
                "éxito": True,
                "código": 200,
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
                "éxito": False,
                "código": 500,
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
```

### controllers/lectura_controller.py

```python
from utils.db_connection import execute_query_json
import logging
import json
from typing import Dict, Any

logger = logging.getLogger(__name__)

class LecturaController:
    
    @staticmethod
    async def get_departamentos() -> Dict[str, Any]:
        try:
            logger.info("📋 GET: Obteniendo departamentos de BD2")
            
            query = "SELECT * FROM Departamentos ORDER BY id"
            resultado_json = await execute_query_json(query)
            resultados = json.loads(resultado_json)
            
            return {
                "éxito": True,
                "código": 200,
                "mensaje": f"{len(resultados)} departamentos encontrados",
                "datos": resultados
            }
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return {
                "éxito": False,
                "código": 500,
                "mensaje": f"Error: {str(e)}"
            }
    
    @staticmethod
    async def get_medicos() -> Dict[str, Any]:
        try:
            logger.info("📋 GET: Obteniendo médicos de BD2")
            
            query = "SELECT * FROM Medicos ORDER BY id"
            resultado_json = await execute_query_json(query)
            resultados = json.loads(resultado_json)
            
            return {
                "éxito": True,
                "código": 200,
                "mensaje": f"{len(resultados)} médicos encontrados",
                "datos": resultados
            }
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return {
                "éxito": False,
                "código": 500,
                "mensaje": f"Error: {str(e)}"
            }
    
    @staticmethod
    async def get_consultas() -> Dict[str, Any]:
        try:
            logger.info("📋 GET: Obteniendo consultas de BD2")
            
            query = "SELECT * FROM Consultas ORDER BY id"
            resultado_json = await execute_query_json(query)
            resultados = json.loads(resultado_json)
            
            return {
                "éxito": True,
                "código": 200,
                "mensaje": f"{len(resultados)} consultas encontradas",
                "datos": resultados
            }
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return {
                "éxito": False,
                "código": 500,
                "mensaje": f"Error: {str(e)}"
            }
```

### routes/sync_router.py

```python
from fastapi import APIRouter, Query
from controllers.sync_controller import SyncController
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/sync")
async def sincronizar(
    table: str = Query(..., description="Tabla: departamentos, medicos, consultas"),
    fecha_mayor: str = Query(..., description="Fecha YYYY-MM-DD")
):
    """
    POST /api/sync?table=medicos&fecha_mayor=2025-01-01
    
    Sincroniza una tabla desde API Fuente
    """
    logger.info(f"🔄 POST /api/sync - table={table}, fecha_mayor={fecha_mayor}")
    return await SyncController.sync(table, fecha_mayor)
```

### routes/lectura_router.py

```python
from fastapi import APIRouter
from controllers.lectura_controller import LecturaController
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/departamentos")
async def get_departamentos():
    """GET /api/departamentos"""
    return await LecturaController.get_departamentos()

@router.get("/medicos")
async def get_medicos():
    """GET /api/medicos"""
    return await LecturaController.get_medicos()

@router.get("/consultas")
async def get_consultas():
    """GET /api/consultas"""
    return await LecturaController.get_consultas()
```

### utils/db_connection.py (API Sync)

(Igual que API Source, pero conecta a BD2)

### utils/__init__.py (API Sync)

```python
from .db_connection import execute_query_json, get_db_connection
from .sync_utils import SyncUtils

__all__ = ["execute_query_json", "get_db_connection", "SyncUtils"]
```

### controllers/__init__.py (API Sync)

```python
from .sync_controller import SyncController
from .lectura_controller import LecturaController

__all__ = ["SyncController", "LecturaController"]
```

### routes/__init__.py (API Sync)

```python
from . import sync_router
from . import lectura_router

__all__ = ["sync_router", "lectura_router"]
```

### requirements.txt (API Sync)

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-dotenv==1.0.0
pyodbc==5.0.1
httpx==0.25.1
pydantic==2.4.2
python-dateutil==2.8.2
```

---

## Guía de Instalación

### Paso 1: Preparar Base de Datos

```bash
# En Azure SQL Management Studio
# Ejecutar en orden:
1. init_bd1.sql (crear BD1 con IDENTITY)
2. init_bd2.sql (crear BD2 sin IDENTITY)
3. seed_data.sql (cargar 1510 registros)
```

### Paso 2: Crear Estructura de Carpetas

```bash
mkdir hospital-system
cd hospital-system

# API Source
mkdir api-source
cd api-source
mkdir controllers routes utils models
cd ..

# API Sync
mkdir api-sync
cd api-sync
mkdir controllers routes utils models
cd ..

# Scripts BD
mkdir db-scripts
```

### Paso 3: Copiar Archivos

Copiar cada archivo de arriba en su ubicación correcta.

### Paso 4: Configurar Variables de Entorno

**api-source/.env:**
```
SQL_SERVER=tcp:TU-SERVIDOR.database.windows.net,1433
SQL_DATABASE=HospitalDB_Source
SQL_USERNAME=tu-usuario
SQL_PASSWORD=tu-contraseña
```

**api-sync/.env:**
```
SQL_SERVER=tcp:TU-SERVIDOR.database.windows.net,1433
SQL_DATABASE=HospitalDB_Replica
SQL_USERNAME=tu-usuario
SQL_PASSWORD=tu-contraseña
API_SOURCE_URL=http://localhost:8000
```

### Paso 5: Instalar Dependencias

```bash
cd api-source
pip install -r requirements.txt

cd ../api-sync
pip install -r requirements.txt
```

---

## Pruebas

### Terminal 1: Ejecutar API Fuente

```bash
cd api-source
python main.py
```

### Terminal 2: Ejecutar API Sync

```bash
cd api-sync
python main.py
```

### Terminal 3: Pruebas

```bash
# Sincronizar Médicos
curl -X POST "http://localhost:8001/api/sync?table=medicos&fecha_mayor=2024-01-01"

# Verificar
curl http://localhost:8001/api/medicos

# Sincronizar Consultas
curl -X POST "http://localhost:8001/api/sync?table=consultas&fecha_mayor=2024-06-01"
```

---

## Endpoints Disponibles

### API Fuente (Puerto 8000)

- `GET /api/departamentos` - Obtener todos
- `GET /api/departamentos?fecha_mayor=YYYY-MM-DD` - Filtrar por fecha
- `POST /api/departamentos` - Crear
- `PUT /api/departamentos/{id}` - Actualizar
- `DELETE /api/departamentos/{id}` - Eliminar

Igual para `/api/medicos` y `/api/consultas`

### API Sync (Puerto 8001)

- `POST /api/sync?table=departamentos&fecha_mayor=YYYY-MM-DD` - Sincronizar
- `GET /api/departamentos` - Verificar datos
- `GET /api/medicos` - Verificar datos
- `GET /api/consultas` - Verificar datos

---

## Características

✅ Pydantic Models con validaciones
✅ Async/await con FastAPI
✅ pyodbc + SQL puro
✅ CRUD completo
✅ Filtrado por fecha
✅ Sincronización incremental
✅ Idempotencia
✅ Logging detallado
✅ Docker ready
✅ Variables de entorno
✅ Documentación Swagger automática