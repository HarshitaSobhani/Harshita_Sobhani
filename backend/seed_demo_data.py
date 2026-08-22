"""
Seeds a representative demo dataset: departments, ~50 sample cameras spread
across Gujarat districts, and a representative watchlist, matching the
hackathon's evaluation test scenario (Model 1 registry + Model 2 analytics).

Usage: python seed_demo_data.py
"""
import random
from app.database import Base, engine, SessionLocal
from app import models

Base.metadata.create_all(bind=engine)

DEPARTMENTS = ["Home Department", "Transport Department (RTO)", "Municipal Corporation", "Food & Civil Supplies"]

# Approximate coordinates for named districts/cities from the problem statement.
DISTRICT_COORDS = {
    "Valsad": (20.5992, 72.9342),
    "Dahod": (22.8331, 74.2593),
    "Somnath": (20.8880, 70.4013),
    "Jamnagar": (22.4707, 70.0577),
    "Dwarka": (22.2394, 68.9678),
    "Ahmedabad": (23.0225, 72.5714),
    "Gandhinagar": (23.2156, 72.6369),
    "Surat": (21.1702, 72.8311),
    "Vadodara": (22.3072, 73.1812),
    "Rajkot": (22.3039, 70.8022),
}


def jitter(value, spread=0.05):
    return value + random.uniform(-spread, spread)


def seed():
    db = SessionLocal()
    try:
        dept_map = {}
        for name in DEPARTMENTS:
            dept = db.query(models.Department).filter_by(name=name).first()
            if not dept:
                dept = models.Department(name=name)
                db.add(dept)
                db.commit()
                db.refresh(dept)
            dept_map[name] = dept.id

        camera_types = ["ip", "analog"]
        vms_platforms = ["Milestone", "Hikvision iVMS", "Genetec", "Local NVR"]
        protocols = ["rtsp", "onvif", "vendor_sdk"]
        storage_types = ["cloud", "local"]

        districts = list(DISTRICT_COORDS.items())
        count = 0
        for i in range(50):
            district, (lat, lon) = districts[i % len(districts)]
            dept_name = DEPARTMENTS[i % len(DEPARTMENTS)]
            code = f"CAM-{district[:3].upper()}-{i+1:03d}"
            if db.query(models.Camera).filter_by(code=code).first():
                continue
            camera = models.Camera(
                code=code,
                name=f"{district} {'Junction' if i % 2 == 0 else 'Checkpoint'} Camera {i+1}",
                department_id=dept_map[dept_name],
                camera_type=camera_types[i % len(camera_types)],
                latitude=jitter(lat),
                longitude=jitter(lon),
                location_desc=f"{district} district, public domain",
                vms_platform=vms_platforms[i % len(vms_platforms)],
                stream_protocol=protocols[i % len(protocols)],
                stream_url=None,
                storage_type=storage_types[i % len(storage_types)],
                retention_days=7 if i % 2 == 0 else 15,
                status=["online", "online", "online", "offline", "maintenance"][i % 5],
            )
            db.add(camera)
            count += 1
        db.commit()
        print(f"Seeded {count} cameras across {len(DEPARTMENTS)} departments.")

        watchlist_samples = [
            ("stolen_vehicle", "GJ01AB1234", "Stolen vehicle reported at Ahmedabad PS", "VAHAN"),
            ("wanted_person", "WANTED-0098", "Wanted in dacoity case, eGujCop FIR 221/2026", "eGujCop"),
            ("missing_person", "MISSING-0451", "Missing minor, reported Surat", "eGujCop"),
            ("blacklisted_vehicle", "GJ05CD5678", "Flagged for repeated traffic violations", "SARTHI"),
        ]
        for category, ref, desc, source in watchlist_samples:
            if not db.query(models.WatchlistEntry).filter_by(reference_no=ref).first():
                db.add(models.WatchlistEntry(category=category, reference_no=ref, description=desc, source_db=source))
        db.commit()
        print("Seeded representative watchlist entries.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
