from fastapi import FastAPI

from . import models
from . import routers

from . import config

def create_app():
  settings = config.get_settings()
  app = FastAPI()

  models.init_db()
  routers.init_routers(app)

  @app.on_event("statup")
  async def startup_event():
    await models.create_all()

  return app