import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    contact_email = Column(String, nullable=True)

    cameras = relationship("Camera", back_populates="department")


class Camera(Base):
    """Model 1: Registry & GIS Foundation core asset."""
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    camera_type = Column(String, nullable=False)  # analog / ip
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location_desc = Column(String, nullable=True)
    vms_platform = Column(String, nullable=True)
    stream_protocol = Column(String, nullable=True)  # rtsp / onvif / vendor_sdk
    stream_url = Column(String, nullable=True)
    storage_type = Column(String, nullable=True)  # local / cloud
    retention_days = Column(Integer, nullable=True)
    status = Column(String, default="unknown")  # online / offline / maintenance / unknown
    onboarded_at = Column(DateTime, default=datetime.datetime.utcnow)

    department = relationship("Department", back_populates="cameras")


class WatchlistEntry(Base):
    """Representative watchlist database (stolen vehicles, wanted persons, etc.)."""
    __tablename__ = "watchlist_entries"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)  # stolen_vehicle / wanted_person / missing_person / blacklisted_vehicle
    reference_no = Column(String, nullable=False)  # vehicle reg no / person id
    description = Column(Text, nullable=True)
    source_db = Column(String, nullable=True)  # VAHAN / eGujCop / AFIS / NAFIS / custom
    added_at = Column(DateTime, default=datetime.datetime.utcnow)


class DetectionEvent(Base):
    """Model 2: Unified Viewing & Analytics output (ANPR / object detection)."""
    __tablename__ = "detection_events"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    detection_type = Column(String, nullable=False)  # anpr / face / object
    value = Column(String, nullable=False)  # plate number / matched tag
    confidence = Column(Float, default=0.0)
    detected_at = Column(DateTime, default=datetime.datetime.utcnow)

    camera = relationship("Camera")


class Alert(Base):
    """Real-time alert generated when a DetectionEvent matches a WatchlistEntry."""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    detection_event_id = Column(Integer, ForeignKey("detection_events.id"), nullable=False)
    watchlist_entry_id = Column(Integer, ForeignKey("watchlist_entries.id"), nullable=False)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    acknowledged = Column(Integer, default=0)  # 0/1 boolean flag

    detection_event = relationship("DetectionEvent")
    watchlist_entry = relationship("WatchlistEntry")
    camera = relationship("Camera")
