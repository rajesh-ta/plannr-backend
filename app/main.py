from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import project, sprint, user, task, user_story
from app.routers import auth
from app.routers import role as role_router
from app.models import user as user_model
from app.models import project as project_model
from app.models import sprint as sprint_model
from app.models import task as task_model
from app.models import user_story as user_story_model
from app.models import role as role_model

app = FastAPI(title="Plannr Backend API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(auth.router)
app.include_router(project.router)
app.include_router(sprint.router)
app.include_router(user.router)
app.include_router(task.router)
app.include_router(user_story.router)
app.include_router(role_router.router)

@app.get("/")
def root():
  return {"message": "Welcome to the Plannr Backend API"}