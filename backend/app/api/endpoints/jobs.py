"""
BTC-SHIELD Job / Task Status API Router
Exposes asynchronous background task progress, status, and execution diagnostics.
"""
from fastapi import APIRouter, HTTPException, Query
from app.services import job_service

router = APIRouter()

@router.get("")
def list_jobs(limit: int = Query(50, ge=1, le=100)):
    """List recent background jobs and their execution states."""
    return job_service.list_jobs(limit=limit)

@router.get("/{job_id}")
def get_job(job_id: str):
    """Retrieve detailed execution status of a single job."""
    job = job_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
