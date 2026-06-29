from fastapi import FastAPI
from routes import router


# -----------------------------
# APP INIT
# -----------------------------
app = FastAPI(
    title="FastAPI with JWT Auth serving a Tool-Calling AI Agent",
    description="29-06-2026 - FastAPI with JWT Auth serving a Tool-Calling AI Agent, built to use tools like Calculator and Wikipedia if decided by the Agent",
    version="1.0.0",
    contact={
        "name": "Per Olsen",
        "url": "https://persteenolsen.netlify.app",
    },
)

app.include_router(router)