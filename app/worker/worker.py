from database.database import SessionLocal
from models.model import Job
import time
import json
# from collections import List

def get_pending_job():
    db = SessionLocal()
    job = db.query(Job).filter(Job.status == 'pending').first()
    db.close()
    
    return job


def get_all_pending_jobs():
    db = SessionLocal()
    jobs = db.query(Job).filter(Job.status == 'pending').all()
    return jobs    
    db.close()

def process_job(db,job):
    print(f"Executing {job.id}")
    
    # status update to running
    job.status = "running"
    db.commit()

    try:
        job_payload = json.loads(job.payload)

        if job.type == "sleep":
            seconds = job_payload["seconds"]
            time.sleep(seconds)
            job.result = json.dumps({
                "result": f"Slept for {seconds}s"
            })


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
        time.sleep(2)
        job.result = json.dumps({
            "result": str(result)
        })

        job.status = "completed"
        db.commit()

def executor():
    while(True):
        db = SessionLocal()
        try:
            job = db.query(Job).filter(Job.status == 'pending').first()
            if job:
                process_job(db,job)
        except Exception as e:
            print(f"Error processing jobs: {e}")
        finally:
            db.close()
                
        # Throttling
        time.sleep(1)


if __name__ == "__main__":
    executor()