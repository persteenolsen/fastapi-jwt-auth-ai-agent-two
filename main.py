from fastapi import FastAPI
from routes import router


# -----------------------------
# APP INIT
# -----------------------------
app = FastAPI(
    title="FastAPI + JWT Auth + Tool-Calling AI Agent",
    description="08-06-2026 - FastAPI using JWT Auth hosted at Render serving AI tool calling agent",
    version="1.0.0",
    contact={
        "name": "Per Olsen",
        "url": "https://persteenolsen.netlify.app",
    },
)


app.include_router(router)