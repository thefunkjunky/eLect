import os.path

# from eLect.main import app
from sqlalchemy.sql import func
# For some reason, it will not let me import models when utils is imported into models.py
from . import models
from eLect.database import Base, engine, session

def get_or_create(model, defaults=None, **kwargs):
    """ Returns instance if already exists, creates and returns one if not """
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        params = dict((k, v) for k, v in kwargs.iteritems() if not isinstance(v, ClauseElement))
        params.update(defaults or {})
        instance = model(**params)
        session.add(instance)
        return instance, True

def num_votes_cast(race_id):
    """Returns the number of votes cast for a race"""
    # TODO: Fix this query to simply return the count #, not a list of tuples
    num_votes_cast = session.query(
            func.count(models.Vote.id)).filter(
            models.Vote.candidate.has(race_id = race_id)).all()[0][0] 
    return num_votes_cast
