from fastapi import APIRouter, HTTPException
import json
import uuid

from models.model import Job, JobRequest, Base
from database.database import SessionLocal, engine

Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/api",tags=["api"])

# Retrieve all jobs
@router.get("/jobs")
def get_all_jobs():
    db = SessionLocal()
    try: 
        return db.query(Job).all()
    except Exception:
        return {
            "status": "Error",
        }
    finally:
        db.close()

# Rerives a job by its id
@router.get("/jobs/{id}",status_code=200)
def get_job_with_id(id:str):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == id).first()
        if not job:
            raise HTTPException(status_code=404,detail="Job not found")
        return job
    finally:
        db.close()

# Post a new job
@router.post("/jobs",status_code=201)
def post_message(request: JobRequest):
    db = SessionLocal()

    job_id = str(uuid.uuid4())
    job_type = request.type
    job_payload = json.dumps(request.payload)
    job_status = "pending"
    
    job = Job(
        id=job_id,
        type=job_type,
        payload=job_payload,
        status=job_status,
    )

    try:
        db.add(job)
        db.commit()
        db.refresh(job)

        return job
    except:
        return {
            "status": "Error",
        }
    finally:
        db.close()