from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database.core import engine, Base

from .entities.user import User  # Import models to register them
from .api import register_routes
from .logging import configure_logging, LogLevels
from .seed import seed

configure_logging(LogLevels.info)

""" Only uncomment below to create new tables, 
otherwise the tests will fail if not connected
"""
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    seed()
    yield
    # Shutdown logic (add if needed)

app = FastAPI(lifespan=lifespan)

register_routes(app)