from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# 1. Physical Units
class Unit(Base):
    __tablename__ = "units"
    unit_id = Column(Integer, primary_key=True, index=True)
    unit_number = Column(String, nullable=False)
    floor = Column(Integer)
    
    tenants = relationship("Tenant", back_populates="unit")

# 2. Staff/Management
class Staff(Base):
    __tablename__ = "staff"
    staff_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    role = Column(String)  # e.g., 'Manager', 'Security', 'Admin'

# 3. Tenants
class Tenant(Base):
    __tablename__ = "tenants"
    tenant_id = Column(Integer, primary_key=True, index=True)
    unit_id = Column(Integer, ForeignKey("units.unit_id"))
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    
    unit = relationship("Unit", back_populates="tenants")

# 4. Rules Catalog
class InfractionType(Base):
    __tablename__ = "infraction_types"
    type_id = Column(Integer, primary_key=True, index=True)
    category = Column(String)
    base_fine = Column(Float)
    description = Column(String) 

# 5. The Actual Infraction Event
class Infraction(Base):
    __tablename__ = "infractions"
    infraction_id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.tenant_id"))
    type_id = Column(Integer, ForeignKey("infraction_types.type_id"))
    reporter_id = Column(Integer, ForeignKey("staff.staff_id"))
    date_logged = Column(DateTime(timezone=True), server_default=func.now())
    date_time = Column(DateTime(timezone=True))
    status = Column(String, default="Pending")

    evidence = relationship("Evidence", back_populates="infraction")

# 6. Evidence (Images/Videos)
class Evidence(Base):
    __tablename__ = "evidence"
    evidence_id = Column(Integer, primary_key=True, index=True)
    infraction_id = Column(Integer, ForeignKey("infractions.infraction_id"))
    file_url = Column(String, nullable=False)
    file_type = Column(String)

    infraction = relationship("Infraction", back_populates="evidence")