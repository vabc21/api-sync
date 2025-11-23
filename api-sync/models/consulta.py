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