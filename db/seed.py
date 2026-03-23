"""
Database seeding script for PMS Generator.
Populates database tables from reference_data.py dictionaries.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import engine, SessionLocal, Base
from db.models import (
    Material, AllowableStress, PipeDimension, FlangeRating,
    FittingMaterial, FlangeMaterial, GasketMaterial, BoltingMaterial,
    ValveMaterial, SpecCodeMap, PressureRatingCode,
)
from data.reference_data import (
    ALLOWABLE_STRESS, PIPE_DIMENSIONS_B36_10, PIPE_DIMENSIONS_B36_19,
    FLANGE_RATINGS_CS, FLANGE_RATINGS_SS, SPEC_CODE_MAP,
    FITTING_MATERIALS, FLANGE_MATERIALS, GASKET_MATERIALS,
    BOLTING_MATERIALS, VALVE_MATERIALS, PRESSURE_RATING_CODES,
)
from src.msr_module import MATERIAL_OPTIONS


MATERIAL_DESCRIPTIONS = {
    grade: desc for _, (grade, desc) in MATERIAL_OPTIONS.items()
}


def seed_materials(db):
    for grade, props in ALLOWABLE_STRESS.items():
        mat = Material(
            grade=grade,
            material_type=props["type"],
            spec=props["spec"],
            smts=props["smts"],
            smys=props["smys"],
            description=MATERIAL_DESCRIPTIONS.get(grade, grade),
        )
        db.add(mat)
        db.flush()

        for key, value in props.items():
            if isinstance(key, (int, float)):
                db.add(AllowableStress(
                    material_id=mat.id,
                    temperature_c=float(key),
                    stress_psi=float(value),
                ))


def seed_pipe_dimensions(db):
    for nps, (od, schedules) in PIPE_DIMENSIONS_B36_10.items():
        for sch, wt in schedules.items():
            db.add(PipeDimension(
                nps=nps, od_inches=od, schedule=sch,
                wall_thickness=wt, standard="B36.10",
            ))

    for nps, (od, schedules) in PIPE_DIMENSIONS_B36_19.items():
        for sch, wt in schedules.items():
            db.add(PipeDimension(
                nps=nps, od_inches=od, schedule=sch,
                wall_thickness=wt, standard="B36.19",
            ))


def seed_flange_ratings(db):
    for temp_f, classes in FLANGE_RATINGS_CS.items():
        for cls, pressure in classes.items():
            db.add(FlangeRating(
                material_group="CS", temperature_f=float(temp_f),
                pressure_class=cls, max_pressure_psig=float(pressure),
            ))

    for temp_f, classes in FLANGE_RATINGS_SS.items():
        for cls, pressure in classes.items():
            db.add(FlangeRating(
                material_group="SS", temperature_f=float(temp_f),
                pressure_class=cls, max_pressure_psig=float(pressure),
            ))


def seed_fitting_materials(db):
    for pipe_grade, fittings in FITTING_MATERIALS.items():
        for component, material in fittings.items():
            db.add(FittingMaterial(
                pipe_material_grade=pipe_grade,
                component=component,
                fitting_material=material,
            ))


def seed_flange_materials(db):
    for pipe_grade, data in FLANGE_MATERIALS.items():
        db.add(FlangeMaterial(
            pipe_material_grade=pipe_grade,
            flange_spec=data["flange"],
            flange_types=data["type"],
        ))


def seed_gasket_materials(db):
    for mat_type, data in GASKET_MATERIALS.items():
        db.add(GasketMaterial(
            material_type=mat_type,
            gasket_type=data["type"],
            material=data["material"],
            spec=data["spec"],
            inner_ring=data["inner"],
            filler=data["filler"],
        ))


def seed_bolting_materials(db):
    for mat_type, data in BOLTING_MATERIALS.items():
        db.add(BoltingMaterial(
            material_type=mat_type,
            stud_spec=data["stud"],
            nut_spec=data["nut"],
            temp_range=data["temp_range"],
        ))


def seed_valve_materials(db):
    for mat_type, valves in VALVE_MATERIALS.items():
        for valve_type, data in valves.items():
            db.add(ValveMaterial(
                material_type=mat_type,
                valve_type=valve_type,
                body_material=data["body"],
                trim=data["trim"],
                seat=data["seat"],
            ))


def seed_spec_codes(db):
    for (mat_type, ca_mm), code in SPEC_CODE_MAP.items():
        db.add(SpecCodeMap(
            material_type=mat_type,
            corrosion_allowance_mm=ca_mm,
            spec_code=code,
        ))


def seed_pressure_rating_codes(db):
    for code, data in PRESSURE_RATING_CODES.items():
        db.add(PressureRatingCode(
            code=code,
            pressure_rating=data["rating"],
            pressure_psig=data["pressure_psig"],
        ))


def is_seeded(db):
    """Check if database already has data."""
    return db.query(Material).first() is not None


def seed_all():
    """Create tables and seed all reference data."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if is_seeded(db):
            return False

        seed_materials(db)
        seed_pipe_dimensions(db)
        seed_flange_ratings(db)
        seed_fitting_materials(db)
        seed_flange_materials(db)
        seed_gasket_materials(db)
        seed_bolting_materials(db)
        seed_valve_materials(db)
        seed_spec_codes(db)
        seed_pressure_rating_codes(db)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        # Log but never crash the app — seeding failure is non-fatal
        print(f"[seed_all] Warning: seeding failed ({e}). App will still start.")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    result = seed_all()
    if result:
        print("Database seeded successfully.")
    else:
        print("Database already contains data. Skipping seed.")
