from database import SessionLocal
from models.model import Job
from datetime import datetime,timezone

db = SessionLocal()
jobs = db.query(Job).all()
# job = db.query(Job).filter(Job.id == "a08d4a34-6e9e-47fe-9767-821c59d07f90").first()
# current = datetime.now(timezone.utc).replace(tzinfo=None)
# time = current - job.updated_at
# print(time.total_seconds())

for job in jobs:
    job.status = 'pending'
    job.result = None
    job.error = None
    job.created_at = datetime.now(timezone.utc)
    job.updated_at = datetime.now(timezone.utc)
db.commit()
db.close()