from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db

router = APIRouter(prefix="/api/streams", tags=["streams"])


@router.get("/{camera_id}/session")
def get_stream_session(camera_id: int, db: Session = Depends(get_db)):
    """
    Model 2 unified viewer: hands the frontend a relay session for a camera
    without departments needing to change their VMS. Real implementation
    negotiates RTSP/ONVIF/vendor-SDK with the source system and returns a
    WebRTC/HLS relay URL; this stub returns the registry-declared stream info
    so the demo viewer can attempt playback directly where feasible.
    """
    camera = db.query(models.Camera).get(camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    if not camera.stream_url:
        raise HTTPException(status_code=422, detail="No stream_url registered for this camera")

    return {
        "camera_id": camera.id,
        "protocol": camera.stream_protocol,
        "relay_url": camera.stream_url,
        "note": "Replace with WebRTC/HLS relay gateway output in production.",
    }
