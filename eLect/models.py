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
    # registered_elections = relationship("Election", backref="user")
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
    default_elect_type = Column(Integer, ForeignKey('elect_type.id'), nullable=False)
    races = relationship("Race", backref="election")
    # TODO: Open this up to have ability to have multiple admins (many-to-many?)
    administrator_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    def as_dictionary(self):
        election = {
        "id": self.id,
        "title": self.title,
        "description_short": self.description_short,
        "description_long": self.description_long,
        "start_date": self.start_date,
        "end_date": self.end_date,
        "elect_open": self.elect_open,
        "default_elect_type": self.default_elect_type,
        "administrator_id": self.administrator_id,
        }
        return election


class Race(Base):
    """ Race class scheme """
    __tablename__ = "race"
    id = Column(Integer, primary_key=True)
    title = Column(String(128), nullable=False)
    description_short = Column(String(1000))
    description_long = Column(String(60000))

    # Foreign relationships
    election_id = Column(Integer, ForeignKey('election.id'), nullable=False)
    elect_type = Column(Integer, ForeignKey('elect_type.id'), nullable=False)
    candidates = relationship("Candidate", backref="race")

    def as_dictionary(self):
        race = {
        "id": self.id,
        "title": self.title,
        "description_short": self.description_short,
        "description_long": self.description_long,
        "election_id": self.election_id,
        "elect_type": self.elect_type,
        }
        return race


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

    def as_dictionary(self):
        candidate = {
        "id": self.id,
        "title": self.title,
        "description_short": self.description_short,
        "description_long": self.description_long,
        "race_id": self.race_id,
        }
        return candidate


class Vote(Base):
    """ Vote class scheme """
    __tablename__ = "vote"
    id = Column(Integer, primary_key=True)
    value = Column(Integer, nullable=False)
    
    # Foreign relationships
    candidate_id = Column(Integer, ForeignKey('candidate.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    def as_dictionary(self):
        vote = {
        "id": self.id,
        "value": self.value,
        "candidate_id": self.candidate_id,
        "user_id": self.user_id,
        }
        return vote

class ElectionType(Base):
    """ Election Type class scheme """
    __tablename__ = "elect_type"
    id = Column(Integer, primary_key=True)
    title = Column(String(128), nullable=False)
    description_short = Column(String(1000))
    description_long = Column(String(60000))

    # Foreign relationships
    # elections = relationship("Election", backref="default_type")
    # races = relationship("Race", backref="elect_type")

    def as_dictionary(self):
        elect_type = {
        "id": self.id,
        "title": self.title,
        "description_short": self.description_short,
        "description_long": self.description_long,
        }
        return elect_type








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

