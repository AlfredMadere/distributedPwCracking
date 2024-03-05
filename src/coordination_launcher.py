
import fastapi
from fastapi import FastAPI, Depends, Request
from src.coordination.coordination_router import coordination_router

def create_app() -> FastAPI:
  app = FastAPI()
  app.include_router(coordination_router)
  return app


app = create_app()