import os.path
from datetime import datetime
import json

from flask import request, Response, url_for, send_from_directory
from werkzeug.utils import secure_filename
from jsonschema import validate, ValidationError

from . import models
from . import decorators
from eLect.main import app
from .database import session

# schemas for schema validation go here...


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


### Define the API endpoints
@app.route("/api/elections", methods=["GET"])
@decorators.accept("application/json")
def elections_get():
    """ Returns a list of elections """
    elections = session.query(models.Election)
    elections = elections.order_by(models.Election.id)

    if not elections:
        message = "No elections in database."
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    data = json.dumps([election.as_dictionary() for election in elections])
    return Response(data, 200, mimetype="application/json")

@app.route("/api/elections/<int:id>", methods=["GET"])
@decorators.accept("application/json")
def election_get(id):
    """ Returns a single election """
    election = session.query(models.Election).get(id)

    # Check for election's existence
    if not election:
        message = "Could not find election with id {}".format(id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    data = json.dumps(election.as_dictionary())
    return Response(data, 200, mimetype="application/json")


@app.route("/api/elections/<int:elect_id>/races", methods=["GET"])
@app.route("/api/races", methods=["GET"])
@decorators.accept("application/json")
def races_get(elect_id = None):
    """ Returns a list of races, with option to limit query to a specific election """

    # Check for election's existence, if elect_id given
    if elect_id:
        check_election_id(elect_id)
        # Finds races for election with elect_id
        # QUESTION
        # what is the difference between .filter(SQL expressions),
        # and .filter_by(keyword expressions)?
        races = session.query(models.Race).filter(Race.election_id == elect_id)
    else:
        races = session.query(models.Race)

    races = races.order_by(models.Race.id)

    if not races:
        message = "No races found associated with election with id {}.".format(elect_id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    data = json.dumps([race.as_dictionary() for race in races])
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

    data = json.dumps(race.as_dictionary())
    return Response(data, 200, mimetype="application/json")

@app.route("/api/elections/<int:elect_id>/races/<int:race_id>/candidates",
 methods=["GET"])
@app.route("/api/candidates", methods=["GET"])
@decorators.accept("application/json")
def candidates_get(elect_id=None, race_id=None):
    """ Returns a list of candidates """
    if elect_id and race_id:
        # Check for election's existence
        check_election_id(elect_id)
        # Check for race's existence
        check_race_id(race_id)
        # Find candidates for given election / race
        candidates = session.query(models.Candidate).filter(models.Race.id == race_id)
    else:
        candidates = session.query(models.Candidate)

    candidates = candidates.order_by(models.Candidate.id)

    if not candidates:
        message = "No candidates found for race id #{}.".format(race_id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    data = json.dumps([candidate.as_dictionary() for candidate in candidates])
    return Response(data, 200, mimetype="application/json")

@app.route("/api/elections/<int:elect_id>/races/<int:race_id>/candidates/<int:cand_id>", methods=["GET"])
@app.route("/api/candidates/<int:cand_id>", methods=["GET"])
@decorators.accept("application/json")
def candidate_get(cand_id, elect_id=None, race_id=None):
    """ Returns information for a single candidate """
    if elect_id and race_id:
        # Check for election's existence
        check_election_id(elect_id)

        # Check for race's existence
        check_race_id(race_id)

    # Find and check the candidate
    candidate = session.query(models.Candidate).get(cand_id)

    # Check for candidates's existence
    if not candidate:
        message = "Could not find candidate with id {}".format(cand_id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    data = json.dumps(candidate.as_dictionary())
    return Response(data, 200, mimetype="application/json")

@app.route("/api/elections/<int:elect_id>/races/<int:race_id>/candidates/<int:cand_id>/votes", 
    methods=["GET"])
@app.route("/api/votes", methods=["GET"])
@decorators.accept("application/json")
def votes_get(elect_id=None, race_id=None, cand_id=None):
    """ Returns a list of votes cast """

    if elect_id and race_id and cand_id:
        # Check for election's existence
        check_election_id(elect_id)

        # Check for race's existence
        check_race_id(race_id)

        # Check for candidate's existence
        check_cand_id(cand_id)
        # Finds, checks, and returns a list of votes cast for candidate
        votes = session.query(models.Vote).filter(models.Vote.candidate_id == cand_id)
    else:
        votes = session.query(models.Vote)

    votes = votes.order_by(models.Vote.id)

    if not votes:
        message = "Could not find any votes cast for candidate with id #{}".format(cand_id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    data = json.dumps([vote.as_dictionary() for vote in votes])
    return Response(data, 200, mimetype="application/json")

@app.route("/api/elections/<int:elect_id>/races/<int:race_id>/candidates/<int:cand_id>/votes/<int:vote_id>", 
    methods=["GET"])
@app.route("/api/votes/<int:vote_id>", methods=["GET"])
@decorators.accept("application/json")
def vote_get(vote_id, elect_id=None, race_id=None, cand_id=None):
    """ Returns information regarding a vote cast """
    if elect_id and race_id and cand_id:
        # Check for election's existence
        check_election_id(elect_id)

        # Check for race's existence
        check_race_id(race_id)

        # Check for candidate's existence
        check_cand_id(cand_id)

    # Finds, checks, and returns a list of votes cast for candidate
    vote = session.query(models.Vote).get(vote_id)

    if not vote:
        message = "Could not find vote with id #{}".format(vote_id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    data = json.dumps(vote.as_dictionary())
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

    data = json.dumps(user.as_dictionary())
    return Response(data, 200, mimetype="application/json")


@app.route("/api/types", methods=["GET"])
@decorators.accept("application/json")
def types_get():
    """ Returns a list of election types """
    elect_types = session.query(models.ElectionType)
    elect_types = elect_types.order_by(models.ElectionType.id)

    if not elect_types:
        message = "No election types in database."
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    data = json.dumps([elect_type.as_dictionary() for elect_type in elect_types])
    return Response(data, 200, mimetype="application/json")

@app.route("/api/types/<int:types_id>", methods=["GET"])
@decorators.accept("application/json")
def type_get(type_id):
    """ Returns information about an election type """
    elect_type = session.query(models.ElectionType).get(type_id)

    if not elect_type:
        message = "No election type with id #{}.".format(type_id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    data = json.dumps(elect_type.as_dictionary())
    return Response(data, 200, mimetype="application/json")

