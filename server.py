from fastapi import FastAPI 
import uvicorn
from app.router import router


app = FastAPI()
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("server:app",host="0.0.0.0",port=8000,reload=True)