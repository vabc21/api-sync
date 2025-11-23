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