# Sentinel: Hybrid Model 1 + Model 2 Architecture

## Quick start

**Local (SQLite, fastest for a demo):**

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python seed_demo_data.py        # onboards ~50 demo cameras + a sample watchlist
uvicorn app.main:app --reload   # http://localhost:8000/docs
```

Then open `frontend/index.html` directly in a browser (it talks to
`http://localhost:8000` by default; override with
`window.SENTINEL_API_BASE` before the script tag if needed).

**Full stack with PostGIS via Docker:**

```bash
docker compose up --build
# backend: http://localhost:8000/docs
# frontend: http://localhost:8080
```


## Why this hybrid

Model 1 (Registry & GIS Foundation) is mandatory and is treated here as the
common foundation: every camera onboarded by any department is first
registered with standardised metadata (location, department, VMS, storage,
retention) and placed on the GIS layer. Model 2 (Unified Viewing &
Analytics) is layered on top of that registry: it reads the registry to know
*which* cameras exist and how to reach them, then connects to each
department's existing VMS/camera directly (RTSP/ONVIF/vendor SDK) without
requiring departments to change their infrastructure.

## Components

```
Department CCTV / VMS (unchanged)
        |  RTSP / ONVIF / vendor SDK
        v
+-------------------+        +----------------------+
| Stream Gateway     |<------ | Camera Registry (M1) |
| (relay, session    |        | GIS + metadata store |
| negotiation)        |        +----------------------+
+-------------------+                  ^
        |                              |
        v                              | onboarding (bulk/manual/API)
+-------------------+                  |
| Analytics Workers  |                 |
| ANPR / face / obj   |                 |
+-------------------+                  |
        |                              |
        v                              |
+-------------------+        +----------------------+
| Detection Events    |------>| Watchlist Cross-check |
+-------------------+        | (VAHAN/eGujCop/AFIS)  |
        |                    +----------------------+
        v                              |
+-------------------+                  v
| Alerts             |<-----------------
+-------------------+
        |
        v
+---------------------------------------------+
| Unified Dashboard: GIS map, camera grid,     |
| vehicle track search, live alerts feed       |
+---------------------------------------------+
```

## What's implemented in this scaffold

- **Registry & GIS (Model 1)**: `backend/app/models.py::Camera`, bulk/manual
  onboarding endpoints (`/api/cameras`), GIS GeoJSON layer
  (`/api/gis/cameras.geojson`), gap-analysis report
  (`/api/cameras/gaps/report`).
- **Unified viewing (Model 2)**: `/api/streams/{camera_id}/session` stub that
  resolves a camera's registered stream info into a relay session (swap for a
  real WebRTC/HLS gateway in production).
- **Analytics & watchlist correlation (Model 2)**: `/api/analytics/detections`
  ingests ANPR/face events, normalises the value, and cross-references it
  against `WatchlistEntry` records, raising an `Alert` on match.
- **Vehicle tracking**: `/api/analytics/vehicle-track/{reg_no}` reconstructs a
  route across cameras/timestamps for the test-scenario requirement.
- **Frontend**: a single-page GIS dashboard (Leaflet) showing onboarded
  cameras color-coded by status, a vehicle-track search panel, and a live
  alerts feed, plus a "simulate detection" button for demoing without live
  camera feeds.

## What's a stub / next step for a real deployment

- `streams.py` returns the registry's declared `stream_url` directly instead
  of negotiating a real WebRTC/HLS relay session per department VMS.
- `analytics.py`'s detection ingestion is a plain HTTP endpoint; in
  production this is called by real ANPR/FRS inference workers consuming
  live RTSP frames (e.g. OpenALPR/YOLO-based pipelines), not typed in by a
  human.
- Auth is not implemented; production needs department-wise RBAC as noted in
  the problem statement (Model 1 suggested stack).
- Storage tiering (hot/warm/cold) and the ~80,000-camera scale-out plan are
  described in the presentation deck, not implemented in this PoC.

## Scaling to ~80,000 cameras

- Registry stays a single PostgreSQL/PostGIS source of truth; horizontally
  scale read replicas for the GIS/dashboard queries.
- Stream gateway and analytics workers scale out per-region (edge clusters
  near camera clusters) to avoid backhauling raw video statewide; only
  detection events/metadata travel to the central platform.
- Detection events and alerts flow through a message bus (Kafka) so
  ingestion volume from thousands of concurrent analytics workers doesn't
  bottleneck the registry API.
