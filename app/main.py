from fastapi import FastAPI
from app.routers import project, sprint, user
from app.models import user as user_model
from app.models import project as project_model
from app.models import sprint as sprint_model

app = FastAPI(title="Plannr Backend API", version="1.0.0")

app.include_router(project.router)
app.include_router(sprint.router)
app.include_router(user.router)

@app.get("/")
def root():
  return {"message": "Welcome to the Plannr Backend API"}