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
            raise ValueError(
                'El nombre debe contener solo letras, espacios y guiones')
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
