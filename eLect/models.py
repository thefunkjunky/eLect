import os.path
from datetime import datetime

from flask import url_for
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Sequence, ForeignKey
from sqlalchemy.orm import relationship


from .database import Base, engine

class User(Base):
    """ User class scheme """
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    email = Column(String(128), unique = True)
    password = Column(String(10084))
    
    # Foreign relationships
    registered_elections = relationship("Election", backref="user")
    administered_elections = relationship("Election", backref="admin")
    votes = relationship("Vote", backref="user")
    # groups = relationship("Group", backref="user")


    def as_dictionary(self):
        user = {
        "id": self.id,
        "name": self.name,
        "email": self.email,
        "password": self.password

        # "file": {
        #     "id": self.file.id,
        #     "filename": self.file.filename,
        #     "path": url_for("uploaded_file", filename=self.file.filename)
        #     }
        }
        return user

class Election(Base):
    """ Election class scheme """
    __tablename__ = "election"
    id = Column(Integer, primary_key=True)
    title = Column(String(128), nullable=False)
    description_short = Column(String(1000))
    description_long = Column(String(60000))
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    elect_open = Column(Boolean, nullable=False) #look into types.Boolean() create_constraint

    # Foreign relationships
    default_race_type = Column(Integer, ForeignKey('race_type.id'), nullable=False)
    races = relationship("Race", backref="election")
    administrators = relationship("User", backref="election")


class Race(Base):
    """ Race class scheme """
    __tablename__ = "race"
    id = Column(Integer, primary_key=True)
    title = Column(String(128), nullable=False)
    description_short = Column(String(1000))
    description_long = Column(String(60000))

    # Foreign relationships
    election_id = Column(Integer, ForeignKey('election.id'), nullable=False)
    race_type = Column(Integer, ForeignKey('race_type.id'), nullable=False)
    candidates = relationship("Candidate", backref="race")

class Candidate(Base):
    """ Candidate class scheme """
    __tablename__ = "candidate"
    id = Column(Integer, primary_key=True)
    title = Column(String(128), nullable=False)
    description_short = Column(String(1000))
    description_long = Column(String(60000))

    # Foreign relationships
    race_id = Column(Integer, ForeignKey('race.id'), nullable=False)
    votes = relationship("Vote", backref="candidate")

class Vote(Base):
    """ Vote class scheme """
    __tablename__ = "vote"
    id = Column(Integer, primary_key=True)
    value = Column(Integer, nullable=False)
    
    # Foreign relationships
    candidate_id = Column(Integer, ForeignKey('candidate.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

class RaceType(Base):
    """ RaceType class scheme """
    __tablename__ = "race_type"
    id = Column(Integer, primary_key=True)
    title = Column(String(128), nullable=False)
    description_short = Column(String(1000))
    description_long = Column(String(60000))
    
    # Foreign relationships








# class File(Base):
#     """ File class scheme """
#     __tablename__ = "file"
#     id = Column(Integer, primary_key=True)
#     filename = Column(String(128), nullable=False)

#     def as_dictionary(self):
#         file = {
#             "id": self.id,
#             "filename": self.filename,
#             "path": url_for("file", filename=self.filename)
#         }
#         return file

Base.metadata.create_all(engine)