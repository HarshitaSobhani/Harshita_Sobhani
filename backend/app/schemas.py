import datetime
from typing import Optional
from pydantic import BaseModel


class DepartmentBase(BaseModel):
    name: str
    contact_email: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentOut(DepartmentBase):
    id: int

    class Config:
        from_attributes = True


class CameraBase(BaseModel):
    code: str
    name: str
    department_id: int
    camera_type: str
    latitude: float
    longitude: float
    location_desc: Optional[str] = None
    vms_platform: Optional[str] = None
    stream_protocol: Optional[str] = None
    stream_url: Optional[str] = None
    storage_type: Optional[str] = None
    retention_days: Optional[int] = None
    status: Optional[str] = "unknown"


class CameraCreate(CameraBase):
    pass


class CameraOut(CameraBase):
    id: int
    onboarded_at: datetime.datetime

    class Config:
        from_attributes = True


class WatchlistEntryBase(BaseModel):
    category: str
    reference_no: str
    description: Optional[str] = None
    source_db: Optional[str] = None


class WatchlistEntryCreate(WatchlistEntryBase):
    pass


class WatchlistEntryOut(WatchlistEntryBase):
    id: int
    added_at: datetime.datetime

    class Config:
        from_attributes = True


class DetectionEventCreate(BaseModel):
    camera_id: int
    detection_type: str
    value: str
    confidence: float = 0.0


class DetectionEventOut(DetectionEventCreate):
    id: int
    detected_at: datetime.datetime

    class Config:
        from_attributes = True


class AlertOut(BaseModel):
    id: int
    detection_event_id: int
    watchlist_entry_id: int
    camera_id: int
    message: str
    created_at: datetime.datetime
    acknowledged: int

    class Config:
        from_attributes = True
