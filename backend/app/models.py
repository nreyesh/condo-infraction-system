import enum
import uuid
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Enum as SQLAlchemyEnum, Boolean
from sqlalchemy.orm import relationship, declarative_mixin
from sqlalchemy.sql import func, text
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class InfractionRecordType(enum.Enum):
    INCIDENCIA = "INCIDENCIA"
    MULTA = "MULTA"

class InfractionStatus(enum.Enum):
    EN_REVISION = "EN_REVISION"
    CURSADO = "CURSADO"
    APELACION = "APELACION"
    NULA = "NULA"

class EvidenceFileType(enum.Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    DOCUMENT = "DOCUMENT"

class StaffRole(enum.Enum):
    MAYORDOMO = "Mayordomo"
    CONSERJE = "Conserje"
    ADMIN = "Admin"

@declarative_mixin
class TimestampMixin:
    """Mixin to add universal created_at and updated_at timestamps to tables."""
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

# Physical Units (Departamento)
class Unit(Base, TimestampMixin):
    __tablename__ = "units"
    unit_id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    unit_number = Column(String, nullable=False, unique=True)
    floor = Column(Integer, nullable=False)
    
    residents = relationship("Resident", back_populates="unit", cascade="all, delete-orphan")
    infractions = relationship("Infraction", back_populates="unit", foreign_keys="[Infraction.unit_id]")

# Contact Info of the person responsible living in a unit (Residente)
class Resident(Base, TimestampMixin):
    __tablename__ = "residents"
    resident_id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    unit_id = Column(UUID(as_uuid=True), ForeignKey("units.unit_id"), nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email = Column(String, nullable=True, unique=True)
    phone = Column(String, nullable=True)
    role = Column(String, default="Residente", nullable=False) #ej: 'Residente', 'Comite'
    is_active = Column(Boolean, default=True, nullable=False) # Soft delete flag
    
    unit = relationship("Unit", back_populates="residents")

# Staff/Management (Personal)
class Staff(Base, TimestampMixin):
    __tablename__ = "staff"
    staff_id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    full_name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # e.g., 'Mayordomo', 'Conserje', 'Admin'
    email = Column(String, nullable=False, unique=True)
    phone = Column(String)
    is_active = Column(Boolean, default=True, nullable=False) # Soft delete flag

    reported_infractions = relationship("Infraction", foreign_keys="[Infraction.reporter_staff_id]")
    assigned_infractions = relationship("Infraction", foreign_keys="[Infraction.assigned_staff_id]")


# Rules Catalog (Catálogo de Faltas)
class InfractionType(Base, TimestampMixin):
    __tablename__ = "infraction_types"
    type_id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String, nullable=False)
    category = Column(String)
    description = Column(Text) 


# Infraction Event (Evento de Infracción)
class Infraction(Base, TimestampMixin):
    __tablename__ = "infractions"
    infraction_id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    unit_id = Column(UUID(as_uuid=True), ForeignKey("units.unit_id"), nullable=False)
    type_id = Column(UUID(as_uuid=True), ForeignKey("infraction_types.type_id"), nullable=False)

    # Se permite que el reportante sea Staff o una Unidad (residente del comité).
    reporter_staff_id = Column(UUID(as_uuid=True), ForeignKey("staff.staff_id"), nullable=True)
    reporter_unit_id = Column(UUID(as_uuid=True), ForeignKey("units.unit_id"), nullable=True)

    # Staff asignado para investigar la incidencia/multa.
    assigned_staff_id = Column(UUID(as_uuid=True), ForeignKey("staff.staff_id"), nullable=True)
    
    # Tipo de registro (Incidencia o Multa) usando SQLAlchemyEnum
    record_type = Column(SQLAlchemyEnum(InfractionRecordType), default=InfractionRecordType.INCIDENCIA, nullable=False)
    
    # Estado de la infracción usando SQLAlchemyEnum
    status = Column(SQLAlchemyEnum(InfractionStatus), default=InfractionStatus.EN_REVISION, nullable=False)

    # Fecha del evento (created_at from mixin replaces date_logged)
    date_of_event = Column(DateTime(timezone=True), nullable=False)

    # Campos para descripción detallada, severidad y monto final.
    description = Column(Text, nullable=False) # Para detalles como la persona específica involucrada.
    severity = Column(Integer, nullable=False) # Rango de 1 a 10.
    final_amount = Column(Float, nullable=False) # Monto final de la multa.

    # Relaciones para acceder a los objetos vinculados.
    unit = relationship("Unit", back_populates="infractions", foreign_keys=[unit_id])
    infraction_type = relationship("InfractionType")
    reporter_staff = relationship("Staff", foreign_keys=[reporter_staff_id])
    reporter_unit = relationship("Unit", foreign_keys=[reporter_unit_id])
    assigned_staff = relationship("Staff", foreign_keys=[assigned_staff_id])
    
    evidence = relationship("Evidence", back_populates="infraction", cascade="all, delete-orphan")
    history = relationship("InfractionHistory", back_populates="infraction", cascade="all, delete-orphan")

# Evidence (Evidencia)
class Evidence(Base, TimestampMixin):
    __tablename__ = "evidence"
    evidence_id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    infraction_id = Column(UUID(as_uuid=True), ForeignKey("infractions.infraction_id"), nullable=False)
    file_type = Column(SQLAlchemyEnum(EvidenceFileType), nullable=False) # Using SQLAlchemyEnum
    file_url = Column(String, nullable=False) # URL al archivo en GCP Storage.

    infraction = relationship("Infraction", back_populates="evidence")

# InfractionHistory (Historial de la Infracción)
class InfractionHistory(Base, TimestampMixin):
    __tablename__ = "infraction_history"
    history_id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    infraction_id = Column(UUID(as_uuid=True), ForeignKey("infractions.infraction_id"), nullable=False)
    
    # Correlativo: order of events for this specific infraction
    sequence_number = Column(Integer, nullable=False, default=1)
    
    # Quién realizó el cambio (normalmente un miembro del Staff).
    changed_by_staff_id = Column(UUID(as_uuid=True), ForeignKey("staff.staff_id"), nullable=False)
    
    # Estado usando SQLAlchemyEnum
    status = Column(SQLAlchemyEnum(InfractionStatus), nullable=False)
    
    # Detalles adicionales sobre qué otros campos fueron modificados
    modification_details = Column(Text, nullable=True) 
    
    notes = Column(Text) # Comentarios sobre el cambio.

    infraction = relationship("Infraction", back_populates="history")
    changed_by_staff = relationship("Staff")
