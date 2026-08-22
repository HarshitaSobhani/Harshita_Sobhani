from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db

router = APIRouter(prefix="/api/gis", tags=["gis"])


@router.get("/cameras.geojson")
def cameras_geojson(db: Session = Depends(get_db)):
    """GIS map layer: registry cameras as a GeoJSON FeatureCollection (Model 1)."""
    cameras = db.query(models.Camera).all()
    features = []
    for c in cameras:
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [c.longitude, c.latitude]},
            "properties": {
                "id": c.id,
                "code": c.code,
                "name": c.name,
                "department_id": c.department_id,
                "camera_type": c.camera_type,
                "status": c.status,
                "vms_platform": c.vms_platform,
            },
        })
    return {"type": "FeatureCollection", "features": features}
