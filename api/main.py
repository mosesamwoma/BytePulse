from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import init_db
from .routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="BytePulse API", version="1.0.0", lifespan=lifespan)
app.include_router(router)