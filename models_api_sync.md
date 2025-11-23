# Models para API Sincronización (BD2)

## 📁 Estructura de Carpeta

```
api-sync/
├── models/
│   ├── __init__.py
│   ├── departamento.py
│   ├── medico.py
│   └── consulta.py
├── controllers/
├── routes/
├── utils/
├── main.py
└── requirements.txt
```

---

## models/__init__.py

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

---

## models/departamento.py

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
        description="ID del departamento",
        examples=[1, 2, 3]
    )
    fecha_creacion: datetime = Field(
        description="Fecha de creación del departamento",
        examples=["2024-01-15T10:30:00"]
    )
    
    class Config:
        from_attributes = True
```

---

## models/medico.py

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
        description="ID del médico",
        examples=[1, 2, 3]
    )
    fecha_registro: datetime = Field(
        description="Fecha de registro del médico",
        examples=["2024-01-20T14:00:00"]
    )
    
    class Config:
        from_attributes = True
```

---

## models/consulta.py

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
        description="ID de la consulta",
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

## controllers/lectura_controller.py (CON MODELS)

```python
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
                "éxito": True,
                "código": 200,
                "mensaje": f"{len(resultados)} departamentos encontrados",
                "datos": [dept.dict() for dept in departamentos_validados]
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
            
            # Validar con Pydantic
            medicos_validados = [
                MedicoResponse(**med) for med in resultados
            ]
            
            return {
                "éxito": True,
                "código": 200,
                "mensaje": f"{len(resultados)} médicos encontrados",
                "datos": [med.dict() for med in medicos_validados]
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
            
            # Validar con Pydantic
            consultas_validadas = [
                ConsultaResponse(**cons) for cons in resultados
            ]
            
            return {
                "éxito": True,
                "código": 200,
                "mensaje": f"{len(resultados)} consultas encontradas",
                "datos": [cons.dict() for cons in consultas_validadas]
            }
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return {
                "éxito": False,
                "código": 500,
                "mensaje": f"Error: {str(e)}"
            }
```

---

## routes/lectura_router.py (CON RESPONSE MODELS)

```python
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
```

---

## ✅ PASOS PARA AGREGAR MODELS A API-SYNC

### 1. Crear carpeta models

```bash
cd api-sync
mkdir models
```

### 2. Crear archivos

```bash
# Windows
echo. > models/__init__.py
echo. > models/departamento.py
echo. > models/medico.py
echo. > models/consulta.py

# Mac/Linux
touch models/__init__.py models/departamento.py models/medico.py models/consulta.py
```

### 3. Copiar contenido

- Copiar `models/__init__.py` de arriba
- Copiar `models/departamento.py` de arriba
- Copiar `models/medico.py` de arriba
- Copiar `models/consulta.py` de arriba

### 4. Actualizar controllers

Usar el contenido de `controllers/lectura_controller.py` de arriba

### 5. Actualizar routes

Usar el contenido de `routes/lectura_router.py` de arriba

### 6. Limpiar caché

```bash
rmdir /s /q api-sync\__pycache__
rmdir /s /q api-sync\models\__pycache__
rmdir /s /q api-sync\controllers\__pycache__
rmdir /s /q api-sync\routes\__pycache__
```

### 7. Reiniciar

```bash
cd api-sync
python main.py
```

---

## 📋 Estructura Final Completa

```
api-sync/
├── models/
│   ├── __init__.py              ✅ NUEVO
│   ├── departamento.py          ✅ NUEVO
│   ├── medico.py                ✅ NUEVO
│   └── consulta.py              ✅ NUEVO
├── controllers/
│   ├── __init__.py
│   ├── sync_controller.py
│   └── lectura_controller.py    ✅ ACTUALIZADO
├── routes/
│   ├── __init__.py
│   ├── sync_router.py
│   └── lectura_router.py        ✅ ACTUALIZADO
├── utils/
│   ├── __init__.py
│   ├── db_connection.py
│   └── sync_utils.py
├── .env
├── main.py
└── requirements.txt
```

---

## ✅ CHECKLIST

- [ ] Carpeta `api-sync/models/` creada
- [ ] `models/__init__.py` con imports correctos
- [ ] `models/departamento.py` con validaciones
- [ ] `models/medico.py` con validaciones
- [ ] `models/consulta.py` con validaciones
- [ ] `controllers/lectura_controller.py` actualizado con models
- [ ] `routes/lectura_router.py` actualizado con response_model
- [ ] Cache limpiado (`__pycache__` eliminado)
- [ ] API Sync reiniciada