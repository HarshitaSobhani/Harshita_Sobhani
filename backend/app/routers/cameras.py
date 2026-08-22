from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/cameras", tags=["cameras"])


@router.get("/", response_model=List[schemas.CameraOut])
def list_cameras(department_id: int | None = None, status: str | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Camera)
    if department_id is not None:
        query = query.filter(models.Camera.department_id == department_id)
    if status is not None:
        query = query.filter(models.Camera.status == status)
    return query.all()


@router.post("/", response_model=schemas.CameraOut)
def onboard_camera(camera: schemas.CameraCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Camera).filter(models.Camera.code == camera.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Camera code already onboarded")
    db_camera = models.Camera(**camera.model_dump())
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera


@router.post("/bulk", response_model=List[schemas.CameraOut])
def bulk_onboard(cameras: List[schemas.CameraCreate], db: Session = Depends(get_db)):
    created = []
    for camera in cameras:
        if db.query(models.Camera).filter(models.Camera.code == camera.code).first():
            continue
        db_camera = models.Camera(**camera.model_dump())
        db.add(db_camera)
        created.append(db_camera)
    db.commit()
    for c in created:
        db.refresh(c)
    return created


@router.get("/{camera_id}", response_model=schemas.CameraOut)
def get_camera(camera_id: int, db: Session = Depends(get_db)):
    camera = db.query(models.Camera).get(camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera


@router.patch("/{camera_id}/status", response_model=schemas.CameraOut)
def update_status(camera_id: int, status: str, db: Session = Depends(get_db)):
    camera = db.query(models.Camera).get(camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    camera.status = status
    db.commit()
    db.refresh(camera)
    return camera


@router.get("/gaps/report")
def gap_analysis_report(db: Session = Depends(get_db)):
    """Simple gap-analysis: cameras offline or without recent onboarding, grouped by department."""
    cameras = db.query(models.Camera).all()
    departments = db.query(models.Department).all()
    report = []
    for dept in departments:
        dept_cameras = [c for c in cameras if c.department_id == dept.id]
        offline = [c.code for c in dept_cameras if c.status in ("offline", "maintenance", "unknown")]
        report.append({
            "department": dept.name,
            "total_cameras": len(dept_cameras),
            "offline_or_unhealthy": offline,
        })
    return report
