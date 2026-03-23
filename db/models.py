"""
SQLAlchemy ORM models for PMS Generator database.
Tables: materials, allowable_stress, pipe_dimensions, flange_ratings,
        fitting_materials, flange_materials, gasket_materials, bolting_materials,
        valve_materials, spec_code_map, saved_specs
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, Float, String, Text, DateTime, ForeignKey, func
)
from sqlalchemy.orm import relationship
from db.database import Base


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    grade = Column(String, unique=True, index=True)
    material_type = Column(String, index=True)  # CS, SS, CS-LT, Alloy
    spec = Column(String)
    smts = Column(Integer)
    smys = Column(Integer)
    description = Column(String)

    stress_values = relationship("AllowableStress", back_populates="material", cascade="all, delete-orphan")


class AllowableStress(Base):
    __tablename__ = "allowable_stress"

    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"))
    temperature_c = Column(Float)
    stress_psi = Column(Float)

    material = relationship("Material", back_populates="stress_values")


class PipeDimension(Base):
    __tablename__ = "pipe_dimensions"

    id = Column(Integer, primary_key=True, index=True)
    nps = Column(String, index=True)
    od_inches = Column(Float)
    schedule = Column(String)
    wall_thickness = Column(Float)
    standard = Column(String)  # B36.10 or B36.19


class FlangeRating(Base):
    __tablename__ = "flange_ratings"

    id = Column(Integer, primary_key=True, index=True)
    material_group = Column(String, index=True)  # CS or SS
    temperature_f = Column(Float)
    pressure_class = Column(Integer)
    max_pressure_psig = Column(Float)


class FittingMaterial(Base):
    __tablename__ = "fitting_materials"

    id = Column(Integer, primary_key=True, index=True)
    pipe_material_grade = Column(String, index=True)
    component = Column(String)
    fitting_material = Column(String)


class FlangeMaterial(Base):
    __tablename__ = "flange_materials"

    id = Column(Integer, primary_key=True, index=True)
    pipe_material_grade = Column(String, unique=True, index=True)
    flange_spec = Column(String)
    flange_types = Column(String)


class GasketMaterial(Base):
    __tablename__ = "gasket_materials"

    id = Column(Integer, primary_key=True, index=True)
    material_type = Column(String, unique=True, index=True)
    gasket_type = Column(String)
    material = Column(String)
    spec = Column(String)
    inner_ring = Column(String)
    filler = Column(String)


class BoltingMaterial(Base):
    __tablename__ = "bolting_materials"

    id = Column(Integer, primary_key=True, index=True)
    material_type = Column(String, unique=True, index=True)
    stud_spec = Column(String)
    nut_spec = Column(String)
    temp_range = Column(String)


class ValveMaterial(Base):
    __tablename__ = "valve_materials"

    id = Column(Integer, primary_key=True, index=True)
    material_type = Column(String, index=True)
    valve_type = Column(String)
    body_material = Column(String)
    trim = Column(String)
    seat = Column(String)


class SpecCodeMap(Base):
    __tablename__ = "spec_code_map"

    id = Column(Integer, primary_key=True, index=True)
    material_type = Column(String, index=True)
    corrosion_allowance_mm = Column(Float)
    spec_code = Column(String)


class PressureRatingCode(Base):
    __tablename__ = "pressure_rating_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False, index=True)
    pressure_rating = Column(String, nullable=False)
    pressure_psig = Column(Integer, nullable=True)


class SavedSpec(Base):
    __tablename__ = "saved_specs"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String)
    doc_number = Column(String)
    revision = Column(String, default="0")
    spec_code = Column(String, index=True)
    material_grade = Column(String)
    material_type = Column(String)
    pipe_size = Column(String)
    design_pressure = Column(Float)       # legacy (psig)
    design_temp = Column(Float)           # legacy (°F)
    # ── Engineering fields ──────────────────────────────────
    design_pressure_barg = Column(Float, nullable=True)
    design_temp_c = Column(Float, nullable=True)
    corrosion_allowance = Column(Float, nullable=True)
    flange_class = Column(String, nullable=True)
    service = Column(String, nullable=True)
    is_nace = Column(Integer, default=0)     # 0/1 boolean
    is_low_temp = Column(Integer, default=0) # 0/1 boolean
    # ────────────────────────────────────────────────────────
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    pms_data_json = Column(Text)
    excel_filename = Column(String, nullable=True)
