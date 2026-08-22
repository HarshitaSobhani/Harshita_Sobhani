from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])


@router.get("/", response_model=List[schemas.WatchlistEntryOut])
def list_watchlist(category: str | None = None, db: Session = Depends(get_db)):
    query = db.query(models.WatchlistEntry)
    if category:
        query = query.filter(models.WatchlistEntry.category == category)
    return query.all()


@router.post("/", response_model=schemas.WatchlistEntryOut)
def add_watchlist_entry(entry: schemas.WatchlistEntryCreate, db: Session = Depends(get_db)):
    db_entry = models.WatchlistEntry(**entry.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


@router.delete("/{entry_id}")
def remove_watchlist_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(models.WatchlistEntry).get(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(entry)
    db.commit()
    return {"deleted": entry_id}
