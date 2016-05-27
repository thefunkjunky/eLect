from flask import Flask
import os

# Custom exceptions
class NoRaces(Exception):
    pass
class NoCandidates(Exception):
    pass
class ClosedElection(Exception):
    pass
class OpenElection(Exception):
    pass
class NoVotes(Exception):
    pass
class NoResults(Exception):
    # Just raise nonetype?
    pass
class NoWinners(Exception):
    # this might not be needed, 
    # other exceptions may offer more useful information
    pass
class TiedResults(Exception):
    pass


app = Flask(__name__)
config_path = os.environ.get("CONFIG_PATH", "eLect.config.DevelopmentConfig")
app.config.from_object(config_path)

from . import api

from .database import Base, engine
Base.metadata.create_all(engine)