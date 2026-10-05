from sqlalchemy import String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from pydantic import BaseModel

# Application models
class JobRequest(BaseModel):
    type: str
    payload: dict

# DB Classes and Models
class Base(DeclarativeBase):
    pass

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    type: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String, default="pending")
    result: Mapped[str | None] = mapped_column(Text, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self):
        return f"<Job id={self.id} type={self.type} status={self.status}>"
