from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, SessionLocal, engine
from app.routers.auth import router as auth_router
from app.routers.department import router as department_router
from app.routers.grades import router as grades_router
from app.seed import seed_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed_db(db)
    finally:
        db.close()

    yield


app = FastAPI(
    title="Electronic Department Backend API",
    description=(
        "Backend service for Academic Electronic Department "
        "managing groups, students, teachers, grades, and auth."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router, prefix="/api")
app.include_router(department_router, prefix="/api")
app.include_router(grades_router, prefix="/api")


@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Electronic Department API is running"}
