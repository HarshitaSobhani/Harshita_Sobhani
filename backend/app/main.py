from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import cameras, departments, gis, watchlist, analytics, streams

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sentinel CCTV Integration Platform",
    description=(
        "Gujarat Police Innovation Hackathon 2026 - Hybrid solution combining "
        "Model 1 (Registry & GIS Foundation) with Model 2 (Unified Viewing & Analytics)."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(departments.router)
app.include_router(cameras.router)
app.include_router(gis.router)
app.include_router(watchlist.router)
app.include_router(analytics.router)
app.include_router(streams.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
