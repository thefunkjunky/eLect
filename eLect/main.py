from flask import Flask
import os

app = Flask(__name__)
config_path = os.environ.get("CONFIG_PATH", "eLect.config.DevelopmentConfig")
app.config.from_object(config_path)

from . import api

from .database import Base, engine
Base.metadata.create_all(engine)