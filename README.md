### Harshita Sobhani

I build end-to-end ML and full-stack systems — from raw data to a working, deployed product — spanning computer vision, recommender systems, retrieval/LLM pipelines, and business-operations apps, with the backend APIs and frontends to serve them. I care about honest evaluation over polished-looking numbers: every project reports what its metrics do and don't prove.

**Currently exploring:** retrieval-augmented generation and real-time vision systems, with an eye toward production concerns (auth, CI, deployment) rather than notebook-only prototypes.

**Pinned highlights**

- **[ASLDetector](https://github.com/HarshitaSobhani/ASLDetector)** — real-time ASL alphabet detector; fine-tunes YOLOv8n vs YOLOv8s and benchmarks speed vs accuracy (yolov8s: 0.966 mAP50, yolov8n: 75+ fps on Apple Silicon), served via a live Gradio webcam demo.
- **[Multi-Object-Detection-and-Persistent-ID-Tracking](https://github.com/HarshitaSobhani/Multi-Object-Detection-and-Persistent-ID-Tracking-in-Public-Sports-Event-Footage)** — tracks every player in sports footage with YOLOv8 + ByteTrack, outputting annotated video with persistent IDs, heatmaps, and trajectories.
- **[PocketDocs](https://github.com/HarshitaSobhani/PocketDocs)** — local-first RAG document Q&A: hybrid FAISS+BM25 retrieval, cross-encoder re-ranking, Claude generation, real auth, and full CI — not just a LangChain demo.
- **[VyapaarOS](https://github.com/HarshitaSobhani/vyapaarOS)** — AI-assisted operations for Indian distributors: deterministic receivables-priority and stock-out engines, invoice import with human approval, and validated LLM-worded collection reminders. FastAPI + PostgreSQL on Railway, Next.js on Vercel, with role-based auth, login throttling, CI and 70 backend tests. The AI layer ships with a mock provider by default, and WhatsApp reminders are drafted for the user to send, not sent automatically.
- **[GlobalVox](https://globalvox.vercel.app)** — recruiter screening prototype: CSV candidate import with row-level validation, concurrency-limited campaign runs against a *simulated* calling provider (no real calls), an explainable 0–100 screening score, and recruiter overrides kept separate from the AI recommendation. Next.js 14, Prisma and PostgreSQL, tested with Vitest.
