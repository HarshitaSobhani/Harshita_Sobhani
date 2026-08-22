from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


def _normalize(value: str) -> str:
    return "".join(ch for ch in value.upper() if ch.isalnum())


@router.post("/detections", response_model=schemas.DetectionEventOut)
def ingest_detection(event: schemas.DetectionEventCreate, db: Session = Depends(get_db)):
    """
    Model 2: ingest an ANPR/face/object detection from a camera feed, then
    cross-reference it against the watchlist database and raise an Alert on match.
    In production this endpoint is called by the stream-analytics pipeline
    (ANPR/FRS inference workers); here it's exposed directly for demo/testing.
    """
    camera = db.query(models.Camera).get(event.camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    db_event = models.DetectionEvent(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    if event.detection_type in ("anpr", "face"):
        normalized_value = _normalize(event.value)
        candidates = db.query(models.WatchlistEntry).all()
        for entry in candidates:
            if _normalize(entry.reference_no) == normalized_value:
                alert = models.Alert(
                    detection_event_id=db_event.id,
                    watchlist_entry_id=entry.id,
                    camera_id=camera.id,
                    message=(
                        f"Watchlist match: {entry.category} '{entry.reference_no}' "
                        f"detected on camera {camera.code} ({camera.name})"
                    ),
                )
                db.add(alert)
        db.commit()

    return db_event


@router.get("/vehicle-track/{reg_no}")
def vehicle_track(reg_no: str, db: Session = Depends(get_db)):
    """Cross-camera vehicle movement history for a given registration number."""
    normalized = _normalize(reg_no)
    events = db.query(models.DetectionEvent).filter(models.DetectionEvent.detection_type == "anpr").all()
    matches = [e for e in events if _normalize(e.value) == normalized]
    matches.sort(key=lambda e: e.detected_at)

    route = []
    for e in matches:
        camera = db.query(models.Camera).get(e.camera_id)
        route.append({
            "camera_code": camera.code if camera else None,
            "camera_name": camera.name if camera else None,
            "latitude": camera.latitude if camera else None,
            "longitude": camera.longitude if camera else None,
            "detected_at": e.detected_at,
            "confidence": e.confidence,
        })
    return {"reg_no": reg_no, "hits": len(route), "route": route}


@router.get("/alerts", response_model=List[schemas.AlertOut])
def list_alerts(acknowledged: bool | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Alert)
    if acknowledged is not None:
        query = query.filter(models.Alert.acknowledged == (1 if acknowledged else 0))
    return query.order_by(models.Alert.created_at.desc()).all()


@router.patch("/alerts/{alert_id}/ack")
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).get(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.acknowledged = 1
    db.commit()
    return {"id": alert_id, "acknowledged": True}
