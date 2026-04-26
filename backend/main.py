from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import config, intake

app = FastAPI(title="UNMAPPED API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(intake.router, prefix="/intake", tags=["intake"])
app.include_router(config.router, prefix="/config", tags=["config"])

