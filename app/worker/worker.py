from database.database import SessionLocal
from models.model import Job
from datetime import datetime, timezone, timedelta
import time
import json


# def get_pending_job():
#     db = SessionLocal()
#     job = db.query(Job).filter(Job.status == 'pending').first()
#     db.close()
    
#     return job


# def get_all_pending_jobs():
#     db = SessionLocal()
#     jobs = db.query(Job).filter(Job.status == 'pending').all()
#     return jobs    
#     db.close()

def claim_next_job(db:SessionLocal):
    """Find a pending job and atomically claim it."""
    candidate = db.query(Job).filter(Job.status == 'pending').first()
    if not candidate:
        return None

    rows_updated = db.query(Job).filter(
        Job.id == candidate.id,
        Job.status == 'pending'
    ).update({
        "status": "running"
    })

    db.commit()

    if rows_updated == 1:
        return candidate
    else:
        return None


def recover_stale_jobs():
    db = SessionLocal()
    
    cutoff_time = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(seconds=60)
    
    try:
        stale_jobs = db.query(Job).filter(
            Job.status == 'running', 
            Job.updated_at < cutoff_time
        ).all()

        for job in stale_jobs:
            print(f"Recovering jobID{job.id}")
            job.status = 'pending'

        if stale_jobs:
            db.commit()

        return stale_jobs

    finally:
        db.close()

def process_job(db,job):
    print(f"Executing {job.id}")
    
    # status update to running
    job.status = "running"
    db.commit()

    try:
        job_payload = json.loads(job.payload)

        if job.type == "sleep":
            seconds = int(job_payload["seconds"])
            time.sleep(seconds)
            job.result = json.dumps({
                "result": f"Slept for {seconds}s"
            })
            result = f"Slept for {seconds}s"


        elif job.type == "calculation":
            first = job_payload["first"]
            second = job_payload["second"]
            operator = job_payload["operator"]

            if operator == "+":
                result = int(first) + int(second)
            elif operator == "-":
                result = int(first) - int(second)
            elif operator == "*":
                result = int(first) * int(second)
            elif operator == "/":
                result = int(first) / int(second)
            elif operator == "//":
                result = int(first) // int(second)
            elif operator == "**":
                result = int(first) ** int(second)
            else:
                raise ValueError(f"Unsupported Operator")

            # simulate long task
            # time.sleep(2)
            job.result = json.dumps({
                "result": str(result)
            })

        job.status = "completed"
    
    except Exception as e:
        job.status = "failed"
        job.error = str(e)
        print(f"JobID {job.id} failed: {e}")

    finally:    
        db.commit()

def executor():
    while(True):
        print("Trying")
        db = SessionLocal()
        try:
            job = claim_next_job(db)
            if job:
                process_job(db,job)

            recover_stale_jobs()
        except Exception as e:
            print(f"Error processing jobs: {e}")
        finally:
            db.close()
                
        # Throttling
        time.sleep(1)


if __name__ == "__main__":
    executor()