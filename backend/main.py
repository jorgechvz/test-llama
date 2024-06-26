from dotenv import load_dotenv

load_dotenv()

import logging
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.api.routers.chat import chat_router
from app.settings import init_settings
from app.observability import init_observability
from fastapi.staticfiles import StaticFiles


app = FastAPI()

init_settings()
init_observability()

environment = os.getenv("ENVIRONMENT", "dev")  # Default to 'development' if not set
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
if environment == "dev":
    logger = logging.getLogger("uvicorn")
    logger.warning("Running in development mode - allowing CORS for all origins")

    # Redirect to documentation page when accessing base URL
    @app.get("/")
    async def redirect_to_docs():
        return RedirectResponse(url="/docs")


if os.path.exists("data"):
    app.mount("/api/files/data", StaticFiles(directory="data"), name="data-static")
app.include_router(chat_router, prefix="/api/chat")


if __name__ == "__main__":
    app_host = os.getenv("APP_HOST", "0.0.0.0")
    app_port = int(os.getenv("APP_PORT", "8000"))
    reload = True if environment == "dev" else False

    uvicorn.run(app="main:app", host=app_host, port=app_port, reload=reload)
