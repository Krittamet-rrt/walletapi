from fastapi import FastAPI

from models import init_db, create_all
from routers import init_routers

import config

def create_app():
  settings = config.get_settings()
  app = FastAPI()

  init_db(settings)
  init_routers(app)

  @app.on_event("startup")
  async def startup_event():
    await create_all()

  return app
