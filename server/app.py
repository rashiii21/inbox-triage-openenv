from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from models import Action
from env import InboxTriageEnv

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

env = InboxTriageEnv(task_name="easy")


@app.get("/")
def home():
    return FileResponse("static/index.html")


@app.post("/reset")
def reset(payload: dict = {}):
    try:
        task_name = payload.get("task_name", "easy")
        obs = env.reset(task_name=task_name)
        return {
            "observation": obs.model_dump(),
            "done": False,
        }
    except Exception as e:
        return {"error": str(e)}


@app.post("/step")
def step(action_data: dict):
    try:
        action = Action(**action_data)
        result = env.step(action)
        return result.model_dump()
    except Exception as e:
        return {"error": str(e)}


@app.get("/state")
def state():
    try:
        return env.state().model_dump()
    except Exception as e:
        return {"error": str(e)}


def main():
    uvicorn.run("app:app", host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()