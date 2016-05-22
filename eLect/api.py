import os.path
from datetime import datetime
import json

from flask import request, Response, url_for, send_from_directory
from jsonschema import validate, ValidationError

from . import models
from . import decorators
from eLect.main import app
from .database import session
from eLect.electiontypes import WinnerTakeAll, Proportional, Schulze

# schemas for schema validation go here...


### Init election types 
# Where should this go?  This seems like a bad place
def drop_tally_types():
    try:
        num_rows_deleted = session.query(
            models.ElectionType).delete()
        session.commit()
    except Exception as e:
        session.rollback()

def init_tally_types():
    try:
        wta = WinnerTakeAll()
        proportional = Proportional()
        schulze = Schulze()
        session.add_all([wta, proportional, schulze])
        session.commit()
    except Exception as e:
        session.rollback()



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
############################
# GET endpoints
############################

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
        races = session.query(models.Race).filter(
            Race.election_id == elect_id)
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
    if elect_id:
        # Check for election's existence
        check_election_id(elect_id)
    if race_id:
        # Check for race's existence
        check_race_id(race_id)
        # Find candidates for given election / race
        candidates = session.query(models.Candidate).filter(
            models.Race.id == race_id)
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
    if elect_id: 
        # Check for election's existence
        check_election_id(elect_id)
    if race_id:
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

    if elect_id:
        # Check for election's existence
        check_election_id(elect_id)
    if race_id:
        # Check for race's existence
        check_race_id(race_id)
    if cand_id:
        # Check for candidate's existence
        check_cand_id(cand_id)
        # Finds, checks, and returns a list of votes cast for candidate
        votes = session.query(models.Vote).filter(
            models.Vote.candidate_id == cand_id)
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
    if elect_id:
        # Check for election's existence
        check_election_id(elect_id)
    if race_id:
        # Check for race's existence
        check_race_id(race_id)
    if cand_id:
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

@app.route("/api/elections/<int:elect_id>/races/<int:race_id>/tally/", methods=["GET"])
@app.route("/api/races/<int:race_id>/tally/", methods=["GET"])
@decorators.accept("application/json")
def get_tally(race_id, elect_id=None):
    """ Tallies results for race [race_id] """
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

    # Finds race type_id
    type_id = race.query(Race.election_type)

    # Finds type with type_id
    elect_type = session.query(models.ElectionType).get(type_id)
    if not elect_type:
        message = "Could not find election type with id {}".format(race_id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    # Init tally object
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

    # # Validate submitted header data, as json, against post_schema
    # try:
    #     validate(data, post_schema)
    # except ValidationError as error:
    #     data = {"message": error.message}
    #     return Response(json.dumps(data), 422, mimetype="application/json")

    # Check if Election title already exists
    duplicate_election = session.query(models.Election).filter(
        models.Election.title == data["title"])
    if duplicate_election:
            message = "Election with title {} already exists, id #{}.".format(
                election.title, election.id)
            data = json.dumps({"message": message})
            return Response(data, 403, mimetype="application/json")

    # Add the election to the database
    election = models.Election(
        title = data["title"],
        description_short = data["description_short"],
        description_long = data["description_long"],
        end_date = data["end_date"],
        elect_open = data["elect_open"],
        default_elect_type = data["default_election_type"],
        admin_id = data["admin_id"]
        )
    session.add(election)
    session.commit()

    # Return a 201 Created, containing the election as JSON and with the 
    # Location header set to the location of the election
    data = json.dumps(election.as_dictionary())
    headers = {"Location": url_for("election_get", elect_id=election.id)}
    return Response(data, 201, headers=headers, mimetype="application/json")

@app.route("/api/races", methods=["POST"])
@decorators.accept("application/json")
@decorators.require("application/json")
def race_post():
    """ Add new race """
    data = request.json

    # Validate header data vs. schema

    # Check if election exists
    check_election_id(data["election_id"])

    # Check if race title already exists in election
    election = session.query(models.Elections).filter(
        models.Election.title == data["title"])
    for race in election.races:
        if race.title == data["title"]:
                message = "Race with title {} already exists in election with id #{}.".format(
                    race.title, election.id)
                data = json.dumps({"message": message})
                return Response(data, 403, mimetype="application/json")

    # Add the race to the database
    race = models.Race(
        title = data["title"],
        description_short = data["description_short"],
        description_long = data["description_long"],
        end_date = data["end_date"],
        election_id = data["election_id"],
        election_type = data["election_type"],
        )
    session.add(race)
    session.commit()

    # Return a 201 Created, containing the election as JSON and with the 
    # Location header set to the location of the election
    data = json.dumps(race.as_dictionary())
    headers = {"Location": url_for("race_get", race_id=race.id)}
    return Response(data, 201, headers=headers, mimetype="application/json")

@app.route("/api/candidates", methods=["POST"])
@decorators.accept("application/json")
@decorators.require("application/json")
def candidate_post():
    """ Add new candidate """
    data = request.json

    # Validate header data vs. schema

    # Check if race exists
    check_race_id(data["race_id"])

    # Check if candidate title already exists in race
    race = session.query(models.Race).filter(
        models.Race.id == data["race_id"])
    for candidate in race.candidates:
        if candidate.title == data["title"]:
            message = "Candidate with title {} already exists in race id #{}.".format(
                candidate.title, race.id)
            data = json.dumps({"message": message})
            return Response(data, 403, mimetype="application/json")
    
    # Add the candidate to the database
    candidate = models.Candidate(
        title = data["title"],
        description_short = data["description_short"],
        description_long = data["description_long"],
        race_id = data["race_id"]
        )
    session.add(candidate)
    session.commit()

    # Return a 201 Created, containing the candidate as JSON and with the 
    # Location header set to the location of the candidate
    data = json.dumps(candidate.as_dictionary())
    headers = {"Location": url_for("candidate_get", cand_id=candidate.id)}
    return Response(data, 201, headers=headers, mimetype="application/json")

@app.route("/api/votes", methods=["POST"])
@decorators.accept("application/json")
@decorators.require("application/json")
def vote_post():
    """ Add new vote """
    data = request.json

    # Validate header data vs. schema

    # Check if candidate exists
    check_cand_id(data["cand_id"])

    # Check if election is still currently open
    candidate = session.query(models.Candidate).filter(
        models.Candidate.id == data["candidate_id"])
    if not candidate.race.election.elect_open:
        message = "Election with id {} is currently closed, and not accepting new votes.".format(
            candidate.race.election.id)
        data = json.dumps({"message": message})
        return Response(data, 403, mimetype="application/json")

    # Check if user already voted for this candidate
    existing_vote = session.query(models.Vote).filter(
        models.Vote.user_id == data["user_id"],
        models.Vote.candidate_id == data["candidate_id"])
    if existing_vote:
        message = "User with id {} has already voted for candidate with id {}.".format(
            data["user_id"],
            data["candidate_id"])
        data = json.dumps({"message": message})
        return Response(data, 403, mimetype="application/json")

    # Add the vote to the database
    vote = models.Vote(
        value = data["value"],
        candidate_id = data["candidate_id"],
        user_id = data["user_id"]
        )
    session.add(vote)
    session.commit()

    # Return a 201 Created, containing the vote as JSON and with the 
    # Location header set to the location of the candidate
    data = json.dumps(vote.as_dictionary())
    headers = {"Location": url_for("races_get", race_id=candidate.race.id)}
    return Response(data, 201, headers=headers, mimetype="application/json")

@app.route("/api/users", methods=["POST"])
@decorators.accept("application/json")
@decorators.require("application/json")
def user_post():
    """ Add new user """
    data = request.json

    # Check if user already exists
    duplicate_user = session.query(models.User).filter(
        models.User.email == data["email"])
    if duplicate_user:
            message = "User with email {} already exists.".format(
                duplicate_user.id)
            data = json.dumps({"message": message})
            return Response(data, 403, mimetype="application/json")

    # Add the user to the database
    user = models.User(
        name = data["name"],
        email = data["email"],
        password = data["password"],
        )
    session.add(user)
    session.commit()

    # Return a 201 Created, containing the election as JSON and with the 
    # Location header set to the location of the election
    data = json.dumps(user.as_dictionary())
    headers = {"Location": url_for("elections_get")}
    return Response(data, 201, headers=headers, mimetype="application/json")
