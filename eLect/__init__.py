# import os

# Find out what we did in 'posts' project to get the Flask app initiation
# out of __init__.py and into its own, separate main.py or whatever.
# Also why? Guessing we want control over when and where the app 
# is run, preventing duplicate attempts by the code every time __init__.py
# is read.

# from flask import Flask

# app = Flask(__name__)
# config_path = os.environ.get("CONFIG_PATH", "tuneful.config.DevelopmentConfig")
# app.config.from_object(config_path)

# from . import api
# from . import views

# from .database import Base, engine
# Base.metadata.create_all(engine)
