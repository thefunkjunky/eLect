import os.path
import datetime

from flask import url_for
from flask_login import UserMixin
from flask.json import jsonify
from sqlalchemy import Column, Integer, Text, DateTime, Boolean, Sequence, ForeignKey, Enum, CheckConstraint, event
from sqlalchemy.orm import relationship, validates, column_property, backref, configure_mappers
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.sql import func, select
# Not sure if this is the best way to go about creating this ENUM
# USE JSONB ALWAYS. Requires PostgreSQL v. >= 9.4
from sqlalchemy.dialects.postgresql import ENUM, JSONB

from eLect.custom_exceptions import *
from .database import Base, engine, session


### Define election type enum
# (not sure if this is the best way to do this
election_type_enum = ENUM(
    "WTA",
    "Proportional",
    "Schulze",
    name="election_type",
    create_type=False)

### Question: does it even make sense to use PostgreSQL TEXT type for fields which
#   should be limited in the first place?

class Election(Base):
    """ Election class scheme """
    __tablename__ = "election"
    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    description_short = Column(Text)
    description_long = Column(Text)
    icon_small_location = Column(Text, 
        default="static/site-images/election_small.gif")
    start_date = Column(DateTime, default=datetime.datetime.utcnow())
    last_modified = Column(DateTime, onupdate=datetime.datetime.utcnow())
    # end_date = Column(DateTime)
    elect_open = Column(Boolean, default=True)

    # Foreign relationships
    default_election_type = Column(election_type_enum, 
        ForeignKey('elect_type.election_type'), 
        default="WTA")
    races = relationship("Race", backref="election", cascade="all, delete-orphan")
    # TODO: Open this up to have ability to have multiple admins (many-to-many?)
    admin_id = Column(Integer, ForeignKey('user.id'), nullable=False, default=1)

    # Update race_open in child races on elect_open update.  Should only be one-way.
    @validates("elect_open")
    def update_elect_open(self, key, value):
        try:
            for race in self.races:
                race.race_open = value
            return value
        except Exception as e:
            raise Update_elect_open_Failed(
                "Update elect_open failed, Exception: ", e)

    def as_dictionary(self):
        election = {
        "id": self.id,
        "title": self.title,
        "description_short": self.description_short,
        "description_long": self.description_long,
        "start_date": self.start_date,
        # "end_date": self.end_date,
        "last_modified": self.last_modified,
        "elect_open": self.elect_open,
        "default_election_type": self.default_election_type,
        "admin_id": self.admin_id,
        "icon_small_location": self.icon_small_location,
        }
        return election


class Race(Base):
    """ Race class scheme """
    __tablename__ = "race"
    # list of election types that allow candidate ranking
    _ranking_types = ["Schulze"]
    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    description_short = Column(Text)
    description_long = Column(Text)
    icon_small_location = Column(Text,
        default="static/site-images/race_small.gif")
    race_open = Column(Boolean, default=True)
    # Needs the _ to differentiate from the hybrid property
    _min_vote_val = Column(Integer, default=0)
    _max_vote_val = Column(Integer, default=1)
    start_date = Column(DateTime, default=datetime.datetime.utcnow())
    last_modified = Column(DateTime, onupdate=datetime.datetime.utcnow())

    # Foreign relationships
    election_id = Column(Integer, ForeignKey('election.id'))
    election_type = Column(election_type_enum, 
        ForeignKey('elect_type.election_type'), 
        default=None)
    candidates = relationship("Candidate", backref="race", cascade="all, delete-orphan")
    votes = relationship("Vote", backref="race", cascade="all, delete-orphan")
    results = relationship("Results", backref="race", cascade="all, delete-orphan")



    def __init__(self, *args, **kwargs):
        """Things that need to be done on init, like assign election_type"""

        # This super() passes along the *args and **kwargs to the base class,
        # so that I don't have to bother with the complexitity of initializing 
        # the fields of the model here (again)
        super(Race, self).__init__(*args, **kwargs)

        # unpacks the kwargs into a dict
        params = dict((k, v) for k, v in kwargs.items())

        # check to see if elect_id was passed, or an election object,
        # then initializes the parent election object accordingly, and
        # assigns race.election_type to parent election.default_election_type
        # if no race.election_type found (default type = None)
        if "election_id" in params.keys():
            election_id = params["election_id"]
            self.election = session.query(Election).get(election_id)
            if self.election_type == None:
                self.election_type = self.election.default_election_type
        elif "election" in params.keys():
            self.election = params["election"]
            if self.election_type == None:
                self.election_type = self.election.default_election_type

    def check_n_fix_valuerange(self, is_remove=None):
        """Checks _min_vote_val and _max_vote_value against len(candidates), 
        and changes them accordingly when certain erroneus conditions are 
        met"""
        cand_count = len(self.candidates)
        # Adjust for the fact that self.candidates isn't actually updated 
        # on append() when the validator and this method are run
        if is_remove == False:
            cand_count += 1
        # if less than 2 candidates found, assigns default values 
        if cand_count < 2:
            self._min_vote_val = 0
            self._max_vote_val = 1
        # If _min_vote_val is > _max_vote_value, adjusts floor to ceiling-cand_count
        if self._min_vote_val > self._max_vote_val:
            self._min_vote_val = self._max_vote_val - cand_count
        # range between floor and ceiling are < cand_count, adjust ceiling
        value_range = self._max_vote_val - self._min_vote_val
        if value_range < cand_count:
            self._max_vote_val = self._min_vote_val + cand_count

    @validates('candidates', include_removes=True)
    def on_candidates_append_or_remove(self, key, candidate, is_remove):
        """On append or remove events in candidates, and if election_type
        allows candidate rankings (e.g.: Schulze, IRV, etc),
        runs check_n_fix_valuerange() to ensure vote value range is functional"""

        # Validation function isnt emitted by default if 
        # candidate in candidates collection is removed.
        # This forces shared code to be executed under both append 
        # and delete events

        # Event only works with list append() and remove() methods.
        # Will not trigger with indirect changes to db/collection.

        if is_remove or not is_remove:
            if self.election_type in self._ranking_types:
                self.check_n_fix_valuerange(is_remove)

        # Returns the candidate if being appended
        if not is_remove:
            return candidate

    @validates('election_type')
    def validate_election_type(self, key, election_type):
        """On update to election_type, and if election_type
        allows candidate rankings (e.g.: Schulze, IRV, etc),
        runs check_n_fix_valuerange() to ensure vote value range is functional"""

        if election_type in self._ranking_types:
            self.check_n_fix_valuerange()
        else:
            self._min_vote_val = 0
            self._max_vote_val = 1
        return election_type

    # Hybrid properties and setters needed to run 
    # check_n_fix_valuerange whenever min or max vote values are set.
    # Did not use @validators here, because the values need to be set 
    # BEFORE the check is run
    @hybrid_property
    def min_vote_val(self):
        """Returns the minimum vote value available for a race"""
        return self._min_vote_val

    @min_vote_val.setter
    def min_vote_val(self, value):
        """Sets the minimum vote value available for a race"""
        if self.election_type in self._ranking_types:
            self._min_vote_val = value
            self.check_n_fix_valuerange()
        else:
            self._min_vote_val = 0
            self._max_vote_val = 1

    @hybrid_property
    def max_vote_val(self):
        """Returns the maximum vote value available for a race"""
        return self._max_vote_val

    @max_vote_val.setter
    def max_vote_val(self, value):
        """Sets the maximum vote value available for a race"""
        if self.election_type in self._ranking_types:
            self._max_vote_val = value
            self.check_n_fix_valuerange()
        else:
            self._min_vote_val = 0
            self._max_vote_val = 1



    def as_dictionary(self):
        race = {
        "id": self.id,
        "title": self.title,
        "description_short": self.description_short,
        "description_long": self.description_long,
        "icon_small_location": self.icon_small_location,
        "election_id": self.election_id,
        "election_type": self.election_type,
        "start_date": self.start_date,
        "last_modified": self.last_modified,
        }
        return race


class Candidate(Base):
    """ Candidate class scheme """
    __tablename__ = "candidate"
    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    description_short = Column(Text)
    description_long = Column(Text)
    icon_small_location = Column(Text,
        default="static/site-images/candidate_small.gif")
    start_date = Column(DateTime, default=datetime.datetime.utcnow())
    last_modified = Column(DateTime, onupdate=datetime.datetime.utcnow())

    # Foreign relationships
    race_id = Column(Integer, ForeignKey('race.id'), nullable=False)
    votes = relationship("Vote", backref="candidate", cascade="all, delete-orphan")

    def as_dictionary(self):
        candidate = {
        "id": self.id,
        "title": self.title,
        "description_short": self.description_short,
        "description_long": self.description_long,
        "icon_small_location": self.icon_small_location,
        "race_id": self.race_id,
        "start_date": self.start_date,
        "last_modified": self.last_modified,
        }
        return candidate



class Vote(Base):
    """ Vote class scheme """
    __tablename__ = "vote"
    id = Column(Integer, primary_key=True)
    value = Column(Integer, nullable=False, default=0)
    start_date = Column(DateTime, default=datetime.datetime.utcnow())
    last_modified = Column(DateTime, onupdate=datetime.datetime.utcnow())
    
    # Foreign relationships
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    race_id = Column(Integer, ForeignKey('race.id'))
    candidate_id = Column(Integer, ForeignKey('candidate.id'), nullable=False)

    def __init__(self, *args, **kwargs):
        """Things that need to be done on init, like assign race_id"""

        super(Vote, self).__init__(*args, **kwargs)
        params = dict((k, v) for k, v in kwargs.items())
        print(params)

        self.candidate = session.query(Candidate).get(
            params["candidate_id"])
        self.race_id = self.candidate.race_id

    def as_dictionary(self):
        vote = {
        "id": self.id,
        "value": self.value,
        "candidate_id": self.candidate_id,
        "user_id": self.user_id,
        "race_id": self.race_id,
        "start_date": self.start_date,
        "last_modified": self.last_modified,
        }
        return vote


class Results(Base):
    """Tallied Results class scheme"""
    __tablename__ = "results"
    id = Column(Integer, primary_key=True)
    results = Column(JSONB)
    start_date = Column(DateTime, default=datetime.datetime.utcnow())
    last_modified = Column(DateTime, onupdate=datetime.datetime.utcnow())

    # Foreign Keys
    race_id = Column(Integer, ForeignKey("race.id"), nullable = False)
    election_type = Column(election_type_enum, 
        ForeignKey("elect_type.election_type"), default=None)

    def __init__(self, *args, **kwargs):
        """On __init__ of Results, assigns things like elect_type from parent Race"""
        super(Results, self).__init__(*args, **kwargs)
        params = dict((k, v) for k, v in kwargs.items())
        
        self.race = session.query(Race).get(params["race_id"])
        self.election_type = self.race.election_type

    def as_dictionary(self):
        results = {
        "id": self.id,
        "start_date": self.start_date,
        "last_modified": self.last_modified,
        "race_id": self.race_id,
        "election_type": self.election_type,
        "results": self.results,
        "start_date": self.start_date,
        "last_modified": self.last_modified,
        }

class ElectionType(Base):
    """ Election Type class scheme """
    __tablename__ = "elect_type"
    # id = Column(Integer, primary_key=True)

    election_type = Column(election_type_enum, primary_key=True, nullable=False)
    title = Column(Text, nullable=False)
    description_short = Column(Text)
    description_long = Column(Text)
    last_modified = Column(DateTime, onupdate=datetime.datetime.utcnow())

    def __init__(self, *args, **kwargs):
        """Things that need to be done on init, like delete duplicate entries"""

        # Pass along any *args and **kwargs to parent ElectionType class
        super(ElectionType, self).__init__(*args, **kwargs)

        # unpacks the kwargs into a dict
        params = dict((k, v) for k, v in kwargs.items())

        # Find and remove any duplicate entries
        existing_elect_type = session.query(ElectionType).filter(
            ElectionType.election_type == params["election_type"]).all()
        for instance in existing_elect_type:
            session.delete(instance)
            session.commit()

    def as_dictionary(self):
        elect_type = {
        "election_type": self.election_type,
        "title": self.title,
        "description_short": self.description_short,
        "description_long": self.description_long,
        "last_modified": self.last_modified,
        }
        return elect_type


    @hybrid_method
    def check_race(self, race_id):
        """Checks race conditions before attempting to tally votes. 
        Failed test returns Exception"""
        from .utils import num_votes_cast
        race = session.query(Race).get(race_id)
        # Fix this query to simply return the count #, not a list of tuples
        num_votes_cast = num_votes_cast(race_id)
        if not race:
            raise NoRaces("No race with id {}".format(race_id))
        elif not race.candidates:
            raise NoCandidates("No candidates found for race id {}".format(race_id))
        elif race.race_open == True:
            raise OpenElection("Race id {} in Election {} is still open.".format(
                race_id, race.election_id))
        elif num_votes_cast == 0:
            raise NoVotes("No Votes cast in Race id {}".format(race_id))


class User(Base, UserMixin):
    """ User class scheme """
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    email = Column(Text, unique = True)
    password = Column(Text)
    icon_small_location = Column(Text)
    start_date = Column(DateTime, default=datetime.datetime.utcnow())
    last_modified = Column(DateTime, onupdate=datetime.datetime.utcnow())

    # Foreign relationships
    # registered_elections = relationship("Election", backref="registered_user")
    administered_elections = relationship("Election", backref="admin")
    votes = relationship("Vote", backref="user")
    # groups = relationship("Group", backref="user")

    def as_dictionary(self):
        user = {
        "id": self.id,
        "name": self.name,
        "email": self.email,
        "password": self.password,
        "start_date": self.start_date,
        "last_modified": self.last_modified,
        }
        return user