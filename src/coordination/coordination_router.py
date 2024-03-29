from fastapi import APIRouter, Depends, Request
from src.password_breaking_agent.sub_job import SubJob
from src.coordination.coordination_service import CoordinationService, get_coordination_service, StartJob, FinishJob, Status
from pydantic import BaseModel
import fastapi
import logging

logger = logging.getLogger(__name__)

coordination_router = APIRouter()






@coordination_router.get("/coordination/health", summary="Check the health of the coordination service", responses={200: {"description": "coordination service is healthy"}})
def health(request: Request) -> fastapi.Response:
  return fastapi.Response(status_code=200, content="Coordination service is healthy")


@coordination_router.get("/coordination/get_job", response_model=StartJob, summary="Get a job to break a password", responses={200: {"model": StartJob}, 401: {"description": "no more passwords to crack"}})
def get_job(request: Request, coordination_service: CoordinationService = Depends(get_coordination_service)) -> SubJob:
  worker_id = request.headers.get("worker_id")
  job = coordination_service.get_job(worker_id)
  if job is None:
    return fastapi.Response(status_code=401)
  else:
    return job

#add an examle response
@coordination_router.post("/coordination/finish_job", summary="Finish a job to break a password", responses={200: {"description": "job finished"}, 401: {"description": "job not found"}})
def finish_job(request: Request, job: FinishJob, coordination_service: CoordinationService = Depends(get_coordination_service)) -> fastapi.Response:
  worker_id = request.headers.get("worker_id")
  coordination_service.finish_job(job, worker_id)
  return fastapi.Response(status_code=200)

@coordination_router.get("/coordination/status", response_model=Status, summary="Get the status of the coordination service", responses={200: {"model": StartJob}})
def status(request: Request, coordination_service: CoordinationService = Depends(get_coordination_service)) -> StartJob:
  return coordination_service.get_status()