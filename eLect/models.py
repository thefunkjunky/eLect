import os.path
import datetime

from flask import url_for
from sqlalchemy import Column, Integer, Text, DateTime, Boolean, Sequence, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.sql import func


from eLect.main import NoRaces, NoCandidates, ClosedElection, NoVotes, NoWinners,TiedResults, NoResults, OpenElection
# from .utils import num_votes_cast
from .database import Base, engine, session

class User(Base):
    """ User class scheme """
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    email = Column(Text, unique = True)
    password = Column(Text)

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
    title = Column(Text, nullable=False)
    description_short = Column(Text)
    description_long = Column(Text)
    ## datetime not json serializable.  need to fix
    # start_date = Column(DateTime, default=datetime.datetime.utcnow())
    # end_date = Column(DateTime)
    # last_modified = Column(DateTime, onupdate=datetime.datetime.utcnow())
    elect_open = Column(Boolean, default=False) #look into types.Boolean() create_constraint

    # Foreign relationships
    default_election_type = Column(Integer, ForeignKey('elect_type.id'), default=1)
    races = relationship("Race", backref="election", cascade="all, delete-orphan")
    # TODO: Open this up to have ability to have multiple admins (many-to-many?)
    admin_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    def as_dictionary(self):
        election = {
        "id": self.id,
        "title": self.title,
        "description_short": self.description_short,
        "description_long": self.description_long,
        # "start_date": self.start_date,
        # "end_date": self.end_date,
        # "last_modified": self.last_modified,
        "elect_open": self.elect_open,
        "default_election_type": self.default_election_type,
        "admin_id": self.admin_id,
        }
        return election


class Race(Base):
    """ Race class scheme """
    __tablename__ = "race"
    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    description_short = Column(Text)
    description_long = Column(Text)

    # Foreign relationships
    election_id = Column(Integer, ForeignKey('election.id'), nullable=False)
    election_type = Column(Integer, ForeignKey('elect_type.id'), default=1)
    candidates = relationship("Candidate", backref="race", cascade="all, delete-orphan")

    def as_dictionary(self):
        race = {
        "id": self.id,
        "title": self.title,
        "description_short": self.description_short,
        "description_long": self.description_long,
        "election_id": self.election_id,
        "election_type": self.election_type,
        }
        return race


class Candidate(Base):
    """ Candidate class scheme """
    __tablename__ = "candidate"
    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    description_short = Column(Text)
    description_long = Column(Text)

    # Foreign relationships
    race_id = Column(Integer, ForeignKey('race.id'), nullable=False)
    votes = relationship("Vote", backref="candidate", cascade="all, delete-orphan")

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
    value = Column(Integer, nullable=False, default=0)
    
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
    title = Column(Text, nullable=False)
    description_short = Column(Text)
    description_long = Column(Text)


    def as_dictionary(self):
        elect_type = {
        "id": self.id,
        "title": self.title,
        "description_short": self.description_short,
        "description_long": self.description_long,
        }
        return elect_type

    @hybrid_method
    def check_race(self, race_id):
        """Checks race conditions before attempting to tally votes. 
        Failed test returns Exception"""
        race = session.query(Race).get(race_id)
        # Fix this query to simply return the count #, not a list of tuples
        num_votes_cast = session.query(
            func.count(Vote.id)).filter(
            Vote.candidate.has(race_id = race_id)).all()[0][0]
        if not race:
            raise NoRaces("No race with id {}".format(race_id))
        elif not race.candidates:
            raise NoCandidates("No candidates found for race id {}".format(race_id))
        elif race.election.elect_open == True:
            raise OpenElection("Race id {} in Election {} is still open.".format(
                race_id, race.election_id))
        elif num_votes_cast == 0:
            raise NoVotes("No Votes cast in Race id {}".format(race_id))
        


    # NOTE: be sure that all ElectionType hybrid methods are represented here
    # @hybrid_method
    # def tally_race(self, race_id):
    #     pass

    # @hybrid_method
    # def check_results(self, results):
    #     pass
