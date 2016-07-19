import os.path
from datetime import datetime
import json
import re

from flask import request, Response, url_for, send_from_directory
from werkzeug.utils import secure_filename
from jsonschema import validate, ValidationError

from . import models
from . import decorators
from eLect.main import app
from eLect.custom_exceptions import *
from .database import session
from eLect.utils import get_or_create, json_serial
from eLect.electiontypes import WinnerTakeAll, Proportional, Schulze

### Global variables


### Schemas for schema validation go here...
### GET schemas
#
user_GET_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "email": {"type": "string"}
    },
    "required": [] # How to require "id" OR "email"?
}

election_GET_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"}
    },
    "required": []
}

race_GET_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "elect_id": {"type": "number"}
    },
    "required": []
}

candidate_GET_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "race_id": {"type": "number"},
    },
    "required": []
}

vote_GET_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "candidate_id": {"type": "number"}
    },
    "required": []
}

### POST schemas
#
user_POST_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "email": {"type": "string"},
        "password": {"type": "string"}
    },
    "required": ["name", "email", "password"]
}
election_POST_schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "description_short": {"type": "string"},
        "description_long": {"type": "string"},
        "icon_small_location": {"type": "string"},
        "elect_open": {"type": "boolean"},
        "default_election_type": {"enum": [
                "WTA",
                "Proportional",
                "Schulze"]
                },
        "admin_id": {"type": "number"}
    },
    "required": ["title"]
}
race_POST_schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "description_short": {"type": "string"},
        "description_long": {"type": "string"},
        "icon_small_location": {"type": "string"},
        "election_id": {"type": "number"},
        "election_type": {"enum": [
                "WTA",
                "Proportional",
                "Schulze"]
                },
        "race_open": {"type": "boolean"},
    },
    "required": ["title", "election_id"]
}
candidate_POST_schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "description_short": {"type": "string"},
        "description_long": {"type": "string"},
        "icon_small_location": {"type": "string"},
        "race_id": {"type": "number"},
    },
    "required": ["title", "race_id"]
}
vote_POST_schema = {
    "type": "object",
    "properties": {
        "value": {"type": "number"},
        "user_id": {"type": "number"},
        "candidate_id": {"type": "number"},
    },
    "required": ["value", "candidate_id", "user_id"]
}

### PUT schemas
#

election_PUT_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "title": {"type": "string"},
        "description_short": {"type": "string"},
        "description_long": {"type": "string"},
        "icon_small_location": {"type": "string"},
        "elect_open": {"type": "boolean"},
        "default_election_type": {"enum": [
                "WTA",
                "Proportional",
                "Schulze"]
                },
        "admin_id": {"type": "number"}
    },
    "required": ["id"]
}
race_PUT_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "title": {"type": "string"},
        "description_short": {"type": "string"},
        "description_long": {"type": "string"},
        "icon_small_location": {"type": "string"},
        "election_id": {"type": "number"},
        "election_type": {"enum": [
                "WTA",
                "Proportional",
                "Schulze"]
                },
        "race_open": {"type": "boolean"},
    },
    "required": ["id"]
}
candidate_PUT_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "title": {"type": "string"},
        "description_short": {"type": "string"},
        "description_long": {"type": "string"},
        "icon_small_location": {"type": "string"},
        "race_id": {"type": "number"},
    },
    "required": ["id"]
}
vote_PUT_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "value": {"type": "number"},
        "user_id": {"type": "number"},
        "candidate_id": {"type": "number"},
    },
    "required": ["id"]
}
user_PUT_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "name": {"type": "string"},
        "email": {"type": "string"},
        "password": {"type": "string"}
    },
    "required": ["id"]
}

### DELETE schemas
#
user_DELETE_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "email": {"type": "string"}
    },
    "required": []
}

election_DELETE_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"}
    },
    "required": ["id"]
}

race_DELETE_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
    },
    "required": ["id"]
}

candidate_DELETE_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
    },
    "required": ["id"]
}

vote_DELETE_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"}
    },
    "required": ["id"]
}


# ## Init election types 
# # Where should this go?  This seems like a bad place
# def drop_tally_types():
#     try:
#         num_rows_deleted = session.query(
#             models.ElectionType).delete()
#         session.commit()
#         return num_rows_deleted
#     except Exception as e:
#         session.rollback()

# def init_tally_types():
#     try:
#         # BILL: What is this doing, or supposed to do?
#         wta = WinnerTakeAll.fetch()
#         proportional = Proportional()
#         schulze = Schulze()
#         session.add_all([wta, proportional, schulze])
#         session.commit()
#     except Exception as e:
#         session.rollback()

### Assign electiontypes model
# TODO: There has GOT to be a better way to do this
def assign_election_type(elect_type):
    """Assign ElectionTypes models"""
    if elect_type == "WTA":
        elect_type = WinnerTakeAll()
        return elect_type
    if elect_type == "Proportional":
        elect_type = Proportional()
        return elect_type
    if elect_type == "Schulze":
        elect_type = Schulze()
        return elect_type

# Putting repetitive session query validations here...
def check_election_id(elect_id):
    election = session.query(models.Election).get(elect_id)
    if not election:
        message = "Could not find election with id {}".format(elect_id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

def check_race_id(race_id):
    race = session.query(models.Race).get(race_id)
    if not race:
        message = "Could not find race with id {}".format(race_id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

def check_cand_id(cand_id):
    candidate = session.query(models.Candidate).get(cand_id)
    if not candidate:
        message = "Could not find candidate with id {}".format(cand_id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

def check_vote_id(vote_id):
    vote = session.query(models.Vote).get(vote_id)
    if not vote:
        message = "Could not find vote with id {}".format(vote_id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

def check_user_id(user_id):
    user = session.query(models.User).get(user_id)
    if not user:
        message = "Could not find user with id {}".format(user_id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")


### Define the API endpoints
############################
# GET endpoints
############################

### TODO: I really dislike the multiple endpoints with the 
### parameters passed through the URL. Need to update to single 
### endpoints, and require JSON header data to be passed with GET method


@app.route("/api/elections", methods=["GET"])
@decorators.accept("application/json")
def elections_get():
    """ Returns a list of elections """

    # TODO: how to paginate using API/JSON requests, WITHOUT
    # loading every damn thing at once

    elections = session.query(models.Election)
    elections = elections.order_by(models.Election.id)

    if not elections:
        message = "No elections in database."
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    data = json.dumps([election.as_dictionary() for election in elections],
        default=json_serial)
    return Response(data, 200, mimetype="application/json")

@app.route("/api/elections/<int:elect_id>", methods=["GET"])
@decorators.accept("application/json")
def election_get(elect_id):
    """ Returns a single election """
    election = session.query(models.Election).get(elect_id)

    # Check for election's existence
    if not election:
        message = "Could not find election with id {}".format(elect_id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    data = json.dumps(election.as_dictionary(), default=json_serial)
    return Response(data, 200, mimetype="application/json")


@app.route("/api/elections/<int:elect_id>/races", methods=["GET"])
@decorators.accept("application/json")
def races_get(elect_id):
    """ Returns a list of races from given election id """

    check_election_id(elect_id)
    # Finds races for election with elect_id
    # QUESTION
    # what is the difference between .filter(SQL expressions),
    # and .filter_by(keyword expressions)?
    races = session.query(models.Race).filter(
        models.Race.election_id == elect_id)

    races = races.order_by(models.Race.id)

    if not races:
        message = "No races found associated with election with id {}.".format(elect_id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    data = json.dumps([race.as_dictionary() for race in races],
        default=json_serial)
    return Response(data, 200, mimetype="application/json")

@app.route("/api/elections/<int:elect_id>/races/<int:race_id>", methods=["GET"])
@app.route("/api/races/<int:race_id>", methods=["GET"])
@decorators.accept("application/json")
def race_get(race_id, elect_id=None):
    """ Returns information for a single race """
    # Check for election's existence, if elect_id is included
    if elect_id:
        check_election_id(elect_id)

    # Finds race with race_id
    race = session.query(models.Race).get(race_id)

    # Check for race's existence
    if not race:
        message = "Could not find race with id {}".format(race_id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    data = json.dumps(race.as_dictionary(), default=json_serial)
    return Response(data, 200, mimetype="application/json")

@app.route("/api/races/<int:race_id>/candidates",
 methods=["GET"])
@decorators.accept("application/json")
def candidates_get(race_id):
    """ Returns a list of candidates from given race id"""
    # Check for race's existence
    check_race_id(race_id)
    # Find candidates for given election / race
    candidates = session.query(models.Candidate).filter(
        models.Candidate.race_id == race_id)

    candidates = candidates.order_by(models.Candidate.id)

    if not candidates:
        message = "No candidates found for race id #{}.".format(race_id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    data = json.dumps([candidate.as_dictionary() for candidate in candidates],
        default=json_serial)
    return Response(data, 200, mimetype="application/json")

@app.route("/api/races/<int:race_id>/candidates/<int:cand_id>", methods=["GET"])
@app.route("/api/candidates/<int:cand_id>", methods=["GET"])
@decorators.accept("application/json")
def candidate_get(cand_id, elect_id=None, race_id=None):
    """ Returns information for a single candidate """

    # Check for race's existence
    if race_id:
        check_race_id(race_id)

    # Find and check the candidate
    candidate = session.query(models.Candidate).get(cand_id)

    # Check for candidates's existence
    if not candidate:
        message = "Could not find candidate with id {}".format(cand_id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    data = json.dumps(candidate.as_dictionary(), default=json_serial)
    return Response(data, 200, mimetype="application/json")

@app.route("/api/races/<int:race_id>/votes", 
    methods=["GET"])
@app.route("/api/candidates/<int:cand_id>/votes", 
    methods=["GET"])
@decorators.accept("application/json")
def votes_get(elect_id=None, race_id=None, cand_id=None):
    """ Returns a list of votes cast """
    if cand_id:
        # Check for candidate's existence
        check_cand_id(cand_id)
        # Finds, checks, and returns a list of votes cast for candidate
        votes = session.query(models.Vote).filter(
            models.Vote.candidate_id == cand_id)
    elif race_id:
        check_race_id(race_id)
        votes = session.query(models.Vote).filter(
            models.Vote.race_id == race_id)

    votes = votes.order_by(models.Vote.id)

    if not votes:
        if cand_id:
            category = "candidate"
        elif race_id: 
            category = "race"
        message = "Could not find any votes cast for {} with id #{}".format(category, cand_id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    data = json.dumps([vote.as_dictionary() for vote in votes],
        default=json_serial)
    return Response(data, 200, mimetype="application/json")

@app.route("/api/candidates/<int:cand_id>/votes/<int:vote_id>", 
    methods=["GET"])
@app.route("/api/races/<int:race_id>/votes/<int:vote_id>", 
    methods=["GET"])
@app.route("/api/candidates/<int:cand_id>/votes/user/<int:user_id>", 
    methods=["GET"])
@app.route("/api/races/<int:race_id>/votes/user/<int:user_id>", 
    methods=["GET"])
@app.route("/api/votes/<int:vote_id>", methods=["GET"])
@decorators.accept("application/json")
def vote_get(vote_id=None, elect_id=None, race_id=None, cand_id=None, user_id=None):
    """ Returns information regarding a vote cast """
    if race_id:
        check_race_id(race_id)
    if cand_id:
        # Check for candidate's existence
        check_cand_id(cand_id)
    if user_id:
        check_user_id(user_id)
    if vote_id:
        check_vote_id(vote_id)

    # Returns a vote
    if user_id & race_id:
        vote = session.query(models.Vote).filter(
            models.Vote.race_id == race_id,
            models.Vote.user_id == user_id).first()
    elif user_id & cand_id:
        vote = session.query(models.Vote).filter(
            models.Vote.candidate_id == cand_id,
            models.Vote.user_id == user_id).first()
    else:
        vote = session.query(models.Vote).get(vote_id)

    if not vote:
        message = "Could not find vote"
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    data = json.dumps(vote.as_dictionary(), default=json_serial)
    return Response(data, 200, mimetype="application/json")


@app.route("/api/users/<int:user_id>", methods=["GET"])
@decorators.accept("application/json")
def user_get(user_id):
    """ Returns information about a specific user """
    user = session.query(models.User).get(user_id)

    if not user:
        message = "Could not find user with id #{}".format(user_id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    data = json.dumps(user.as_dictionary(), default=json_serial)
    return Response(data, 200, mimetype="application/json")


@app.route("/api/types", methods=["GET"])
@decorators.accept("application/json")
def types_get():
    """ Returns a list of election types """
    elect_types = session.query(models.ElectionType)

    if not elect_types:
        message = "No election types in database."
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    data = json.dumps([elect_type.as_dictionary() for elect_type in elect_types],
        default=json_serial)
    return Response(data, 200, mimetype="application/json")

@app.route("/api/types/<type_enum>", methods=["GET"])
@decorators.accept("application/json")
def type_get(type_enum):
    """ Returns information about an election type """
    elect_type = session.query(models.ElectionType).get(type_enum)

    if not elect_type:
        message = "No election type with enum value of \"{}\".".format(type_enum)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    data = json.dumps(elect_type.as_dictionary(), default=json_serial)
    return Response(data, 200, mimetype="application/json")

@app.route("/api/elections/<int:elect_id>/races/<int:race_id>/tally", methods=["GET"])
@app.route("/api/races/<int:race_id>/tally", methods=["GET"])
@decorators.accept("application/json")
def get_tally(race_id, elect_id=None):
    """ Tallies results for race [race_id] """
    # Check for election's existence, if elect_id is included
    if elect_id:
        check_election_id(elect_id)

    # Checks race_id
    check_race_id(race_id)

    # Finds race with race_id
    race = session.query(models.Race).get(race_id)

    # Finds race election type
    elect_type_enum = race.election_type

    # Inits elect_type object with elect_type_enum identifier
    elect_type = assign_election_type(elect_type_enum)
    if not elect_type:
        message = "Could not find election type with enum {}".format(
            elect_type_enum)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    # Attempts to tally race and check results, according to elect_type rules
    try:
        results = elect_type.tally_race(race_id)
        elect_type.check_results(results)
    except Exception as e:
        message = "Tally Error: {}".format(e)
        data = json.dumps({"message": message})
        return Response(data, 400, mimetype="application/json")

    data = json.dumps(results)
    return Response(data, 200, mimetype="application/json")

############################
# POST endpoints
############################

@app.route("/api/elections", methods=["POST"])
@decorators.accept("application/json")
@decorators.require("application/json")
def election_post():
    """ Add new election """
    data = request.json

    # Validate submitted header data, as json, against schema
    try:
        validate(data, election_POST_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")

    # # Check if Election title already exists
    # # NOTE: Duplicate titles should probably be allowed
    # duplicate_election = session.query(models.Election).filter(
    #     models.Election.title == data["title"])
    # if duplicate_election:
    #         message = "Election with title {} already exists, id #{}.".format(
    #             election.title, election.id)
    #         data = json.dumps({"message": message})
    #         return Response(data, 403, mimetype="application/json")

    # Inits election object from request data and populates db
    election=models.Election(**data)
    session.add(election)
    session.commit()

    # Return a 201 Created, containing the election as JSON and with the 
    # Location header set to the location of the election
    data = json.dumps(election.as_dictionary(), default=json_serial)
    headers = {"Location": url_for("election_get", elect_id=election.id)}
    return Response(data, 201, headers=headers, mimetype="application/json")

@app.route("/api/races", methods=["POST"])
@decorators.accept("application/json")
@decorators.require("application/json")
def race_post():
    """ Add new race """
    data = request.json

    # Validate header data vs. schema
    try:
        validate(data, race_POST_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")

    # Check if election exists
    check_election_id(data["election_id"])

    # Check if race title already exists in election
    election = session.query(models.Election).get(
        data["election_id"])
    for race in election.races:
        if race.title == data["title"]:
                message = "Race with title {} already exists in election with id #{}.".format(
                    race.title, election.id)
                data = json.dumps({"message": message})
                return Response(data, 403, mimetype="application/json")
    # Populate defaults if no data given for optional keys
    
    # Add the race to the database
    race = models.Race(**data)
    session.add(race)
    session.commit()

    # Return a 201 Created, containing the election as JSON and with the 
    # Location header set to the location of the election
    data = json.dumps(race.as_dictionary(), default=json_serial)
    headers = {"Location": url_for("race_get", race_id=race.id)}
    return Response(data, 201, headers=headers, mimetype="application/json")

@app.route("/api/candidates", methods=["POST"])
@decorators.accept("application/json")
@decorators.require("application/json")
def candidate_post():
    """ Add new candidate """
    data = request.json

    # Validate header data vs. schema
    try:
        validate(data, candidate_POST_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")

    # Check if race exists
    check_race_id(data["race_id"])

    # Check if candidate title already exists in race
    race = session.query(models.Race).filter(
        models.Race.id == data["race_id"]).first()
    for candidate in race.candidates:
        if candidate.title == data["title"]:
            message = "Candidate with title {} already exists in race id #{}.".format(
                candidate.title, race.id)
            data = json.dumps({"message": message})
            return Response(data, 403, mimetype="application/json")

    # Check if race is already closed

    # Add the candidate to the database
    candidate = models.Candidate(**data)
    # session.add(candidate)
    ### NOTE: appending candidate to race.candidates collection to trigger 
    ### validator event
    race.candidates.append(candidate)
    session.commit()

    # Return a 201 Created, containing the candidate as JSON and with the 
    # Location header set to the location of the candidate
    data = json.dumps(candidate.as_dictionary(), default=json_serial)
    headers = {"Location": url_for("candidate_get", cand_id=candidate.id)}
    return Response(data, 201, headers=headers, mimetype="application/json")

@app.route("/api/votes", methods=["POST"])
@decorators.accept("application/json")
@decorators.require("application/json")
def vote_post():
    """ Add new vote """
    data = request.json

    # Validate header data vs. schema
    try:
        validate(data, vote_POST_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")

    # Check if candidate exists
    check_cand_id(data["candidate_id"])
    candidate = session.query(models.Candidate).filter(
        models.Candidate.id == data["candidate_id"]).first()

    # Check if election is still currently open
    if not candidate.race.election.elect_open:
        message = "Election with id {} is currently closed, and not accepting new votes.".format(
            candidate.race.election.id)
        data = json.dumps({"message": message})
        return Response(data, 403, mimetype="application/json")

    # Check if user already voted for this candidate
    existing_votes = session.query(models.Vote).filter(
        models.Vote.user_id == data["user_id"],
        models.Vote.candidate_id == data["candidate_id"]).count()
    if existing_votes > 0:
        message = "User with id {} has already voted for candidate with id {}.".format(
            data["user_id"],
            data["candidate_id"])
        data = json.dumps({"message": message})
        return Response(data, 403, mimetype="application/json")

    # Add the vote to the database
    vote = models.Vote(**data)
    session.add(vote)
    session.commit()

    # Return a 201 Created, containing the vote as JSON and with the 
    # Location header set to the location of the election
    data = json.dumps(vote.as_dictionary(), default=json_serial)
    headers = {"Location": url_for("election_get", elect_id=candidate.race.election.id)}
    return Response(data, 201, headers=headers, mimetype="application/json")

@app.route("/api/users", methods=["POST"])
@decorators.accept("application/json")
@decorators.require("application/json")
def user_post():
    """ Add new user """
    data = request.json

    # Validate request JSON data vs schema
    try:
        validate(data, user_POST_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")

    # Check if user already exists
    duplicate_user = session.query(models.User).filter(
        models.User.email == data["email"]).first()
    if duplicate_user:
            message = "User with email {} already exists.".format(
                duplicate_user.id)
            data = json.dumps({"message": message})
            return Response(data, 403, mimetype="application/json")

    # Add the user to the database
    user = models.User(**data)
    session.add(user)
    session.commit()

    # Return a 201 Created, 
    data = json.dumps(user.as_dictionary(), default=json_serial)
    # Update this to send them back to previous page before 
    headers = {"Location": url_for("elections_get")}
    return Response(data, 201, headers=headers, mimetype="application/json")


############################
# PUT endpoints
############################

@app.route("/api/elections", methods=["PUT"])
@decorators.accept("application/json")
@decorators.require("application/json")
def election_put():
    """ Edits election """
    data = request.json

    # Validate submitted header data, as json, against schema
    try:
        validate(data, election_PUT_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")

    check_election_id(data["id"])

    # Init Election object with id=data["id"]
    election = session.query(models.Election).get(data["id"])

    # Update target election
    for key, value in data.items():
        election[key] = value
    session.commit()

    data = json.dumps(election.as_dictionary(), default=json_serial)
    headers = {"Location": url_for("election_get", id=election.id)}
    return Response(data, 200, headers=headers, mimetype="application/json")

@app.route("/api/races", methods=["PUT"])
@decorators.accept("application/json")
@decorators.require("application/json")
def race_put():
    """ Edits race """
    data = request.json

    # Validate submitted header data, as json, against schema
    try:
        validate(data, race_PUT_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")

    check_race_id(data["id"])

    # Init Race object with id=data["id"]
    race = session.query(models.Race).get(data["id"])

    # Update target race
    for key, value in data.items():
        race[key] = value
    session.commit()

    data = json.dumps(race.as_dictionary(), default=json_serial)
    headers = {"Location": url_for("race_get", id=race.id)}
    return Response(data, 200, headers=headers, mimetype="application/json")


@app.route("/api/candidates", methods=["PUT"])
@decorators.accept("application/json")
@decorators.require("application/json")
def candidate_put():
    """ Edits candidate """
    data = request.json

    # Validate submitted header data, as json, against schema
    try:
        validate(data, candidate_PUT_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")

    check_candidate_id(data["id"])

    # Init Candidate object with id=data["id"]
    candidate = session.query(models.Candidate).get(data["id"])

    # Update target candidate
    for key, value in data.items():
        candidate[key] = value
    session.commit()

    data = json.dumps(candidate.as_dictionary(), default=json_serial)
    headers = {"Location": url_for("candidate_get", id=candidate.id)}
    return Response(data, 200, headers=headers, mimetype="application/json")

@app.route("/api/votes", methods=["PUT"])
@decorators.accept("application/json")
@decorators.require("application/json")
def vote_put():
    """ Edits vote """
    data = request.json

    # Validate submitted header data, as json, against schema
    try:
        validate(data, vote_PUT_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")
    # Check if vote exists
    check_vote_id(data["id"])
    # Check if candidate exists
    check_cand_id(data["candidate_id"])
    candidate = session.query(models.Candidate).filter(
        models.Candidate.id == data["candidate_id"]).first()


    # Init Vote object with id=data["id"]
    vote = session.query(models.Vote).get(data["id"])

    # Checks if election is still open
    if not candidate.race.election.elect_open:
        message = "Election with id {} is currently closed, and not accepting new votes.".format(
            candidate.race.election.id)
        data = json.dumps({"message": message})
        return Response(data, 403, mimetype="application/json")

    # Update target vote
    for key, value in data.items():
        vote[key] = value
    session.commit()

    data = json.dumps(vote.as_dictionary(), default=json_serial)
    headers = {"Location": url_for("vote_get", id=vote.id)}
    return Response(data, 200, headers=headers, mimetype="application/json")

@app.route("/api/users", methods=["PUT"])
@decorators.accept("application/json")
@decorators.require("application/json")
def user_put():
    """ Edits user """
    data = request.json

    # Validate submitted header data, as json, against schema
    try:
        validate(data, user_PUT_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")

    check_user_id(data["id"])

    # Init User object with id=data["id"]
    user = session.query(models.User).get(data["id"])

    # Update target user
    for key, value in data.items():
        user[key] = value
    session.commit()

    data = json.dumps(user.as_dictionary(), default=json_serial)
    headers = {"Location": url_for("user_get", id=user.id)}
    return Response(data, 200, headers=headers, mimetype="application/json")

############################
# DELETE endpoints
############################

### NOTE about response codes re: DELETE method
# 9.7 DELETE
# A successful response SHOULD be 
# 200 (OK) if the response includes an entity describing the status, 
# 202 (Accepted) if the action has not yet been enacted, or 
# 204 (No Content) if the action has been enacted but the response 
# does not include an entity. 

@app.route("/api/elections", methods=["DELETE"])
@decorators.accept("application/json")
@decorators.require("application/json")
def election_delete():
    """ Deletes election """
    data = request.json

    # Validate submitted header data, as json, against schema
    try:
        validate(data, election_DELETE_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")

    check_election_id(data["id"])

    # Deletes Election object with id=data["id"]
    election = session.query(models.Election).get(data["id"])
    session.delete(election)
    session.commit()

    message = "Deleted election id #{}".format(data["id"])
    data = json.dumps({"message": message})
    headers = {"Location": url_for("elections_get")}

    return Response(data, 200, headers=headers, mimetype="application/json")

@app.route("/api/races", methods=["DELETE"])
@decorators.accept("application/json")
@decorators.require("application/json")
def race_delete():
    """ Deletes race """
    data = request.json

    # Validate submitted header data, as json, against schema
    try:
        validate(data, race_DELETE_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")

    check_race_id(data["id"])

    # Deletes race object with id=data["id"]
    race = session.query(models.Race).get(data["id"])
    # Obtains parent election_id and creates JSON header data for subsequent redirect
    election_data = json.dump({"id": race.election_id})
    # Deletes race and commits
    session.delete(race)
    session.commit()

    message = "Deleted race id #{}".format(data["id"])
    data = json.dumps({"message": message})
    headers = {"Location": url_for("election_get", data=election_data)}

    return Response(data, 200, headers=headers, mimetype="application/json")

@app.route("/api/candidates", methods=["DELETE"])
@decorators.accept("application/json")
@decorators.require("application/json")
def candidate_delete():
    """ Deletes candidate """
    data = request.json

    # Validate submitted header data, as json, against schema
    try:
        validate(data, candidate_DELETE_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")

    check_candidate_id(data["id"])

    # Deletes candidate object with id=data["id"]
    candidate = session.query(models.Candidate).get(data["id"])
    # Obtains parent race_id and creates JSON header data for subsequent redirect
    race = session.query(models.Race).get(candidate.race_id)
    race_data = json.dump({"id": candidate.race_id})
    # Deletes candidate and commits
    # session.delete(candidate)
    ### NOTE: deleteing from race.candidates collection to trigger
    ### validator event
    race.candidates.remove(candidate)
    session.commit()

    message = "Deleted candidate id #{}".format(data["id"])
    data = json.dumps({"message": message})
    headers = {"Location": url_for("race_get", data=race_data)}

    return Response(data, 200, headers=headers, mimetype="application/json")

@app.route("/api/votes", methods=["DELETE"])
@decorators.accept("application/json")
@decorators.require("application/json")
def vote_delete():
    """ Deletes vote """
    data = request.json

    # Validate submitted header data, as json, against schema
    try:
        validate(data, vote_DELETE_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")

    check_vote_id(data["id"])

    # Obtains vote object with id=data["id"]
    vote = session.query(models.Vote).get(data["id"])
    # Obtains parent race_id and creates JSON header data for subsequent redirect
    race_id = vote.candidate.race_id
    race_data = json.dump({"id": race_id})
    # Deletes vote and commits
    session.delete(vote)
    session.commit()

    message = "Deleted vote id #{}".format(data["id"])
    data = json.dumps({"message": message})
    headers = {"Location": url_for("race_get", data=race_data)}

    return Response(data, 200, headers=headers, mimetype="application/json")
