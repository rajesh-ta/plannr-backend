from fastapi import FastAPI
from app.routers import project
from app.models import user, project as project_model

app = FastAPI(title="Plannr Backend API", version="1.0.0")

app.include_router(project.router)

@app.get("/")
def root():
  return {"message": "Welcome to the Plannr Backend API"}