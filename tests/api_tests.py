import unittest
import os
import shutil
import json
try: from urllib.parse import urlparse
except ImportError: from urlparse import urlparse # Py2 compatibility
from io import StringIO
from operator import itemgetter

import sys
# print(list(sys.modules.keys()))
# Configure our app to use the testing database
os.environ["CONFIG_PATH"] = "eLect.config.TestingConfig"

from sqlalchemy.orm import aliased
from eLect.main import app
from eLect.custom_exceptions import *
from eLect import models
from eLect import utils
from eLect.database import Base, engine, session
from eLect.electiontypes import WinnerTakeAll, Proportional, Schulze



class TestAPI(unittest.TestCase):
    """ Tests for the API """

    def setUp(self):
        """ Test setup """
        self.client = app.test_client()

        # Set up the tables in the database
        Base.metadata.create_all(engine)

    def init_elect_types(self):
        """Set up ElectionType Objects"""
        self.wta = WinnerTakeAll()
        self.proportional = Proportional()
        self.schulze = Schulze()

        session.add_all([self.wta, self.proportional, self.schulze])

    def populate_database(self, election_type="WTA"):
        self.init_elect_types()

        self.userA = models.User(
            name = "UserA",
            email = "userA@eLect.com",
            password = "asdf")
        self.userB = models.User(
            name = "UserB",
            email = "userB@eLect.com",
            password = "asdf")
        self.userC = models.User(
            name = "UserC",
            email = "userC@eLect.com",
            password = "asdf")

        session.add_all([self.userA, self.userB, self.userC])
        session.commit()

        self.electionA = models.Election(
            title = "Election A",
            admin_id = self.userA.id,
            default_election_type = election_type
            )
        self.electionB = models.Election(
            title = "Election B",
            admin_id = self.userB.id,
            default_election_type = election_type
            )

        session.add_all([self.electionA, self.electionB])
        session.commit()

        self.raceA = models.Race(
            title = "Race A",
            election = self.electionA
            )
        self.raceB = models.Race(
            title = "Race B",
            election = self.electionB
            )

        session.add_all([self.raceA,self.raceB])
        session.commit()

        self.candidateAA = models.Candidate(
            title = "Candidate AA",
            race_id = self.raceA.id)
        self.candidateAB = models.Candidate(
            title = "Candidate AB",
            race_id = self.raceA.id)
        self.candidateBA = models.Candidate(
            title = "Candidate BA",
            race_id = self.raceB.id)
        self.candidateBB = models.Candidate(
            title = "Candidate BB",
            race_id = self.raceB.id)
        self.candidateBC = models.Candidate(
            title = "Candidate BC",
            race_id = self.raceB.id)
        self.candidateBD = models.Candidate(
            title = "Candidate BD",
            race_id = self.raceB.id)

        session.add_all([
            self.candidateAA,
            self.candidateAB,
            self.candidateBA,
            self.candidateBB,
            self.candidateBC,
            self.candidateBD])
        session.commit()

    def test_unsupported_accept_header(self):
        response = self.client.get("/api/elections",
            headers=[("Accept", "application/xml")]
            )
        self.assertEqual(response.status_code, 406)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data["message"],
            "Request must accept application/json data")

    def test_get_empty_datasets(self):
        """ Getting elections, races, etc from an empty database """
        endpoints = ["elections", "races", "candidates", "votes", "types"]
        for endpoint in endpoints:
            response = self.client.get("/api/{}".format(endpoint),
                headers=[("Accept", "application/json")])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.mimetype, "application/json")

            data = json.loads(response.data.decode("ascii"))
            self.assertEqual(data, [])

    def test_get_election(self):
        """ Testing GET method on /api/elections endpoint """
        self.populate_database()
        # electionB = session.query(models.Election).filter(
        #     models.Election.title == "Election B")
        response = self.client.get("/api/elections/{}".format(self.electionB.id),
            headers=[("Accept", "application/json")])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

        election = json.loads(response.data.decode("ascii"))
        self.assertEqual(election["title"], "Election B")
        self.assertEqual(election["admin_id"], self.electionB.admin_id)

    def test_get_race(self):
        """ Testing GET method on /api/races endpoint """
        self.populate_database()
        response = self.client.get("/api/races/{}".format(self.raceB.id),
            headers=[("Accept", "application/json")])
        longURL_response = self.client.get(
            "/api/elections/{}/races/{}".format(
                self.electionA.id, self.raceB.id),
            headers=[("Accept", "application/json")])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(longURL_response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(longURL_response.mimetype, "application/json")

        race = json.loads(response.data.decode("ascii"))
        race_long = json.loads(longURL_response.data.decode("ascii"))
        self.assertEqual(race["title"], "Race B")
        self.assertEqual(race["election_type"], self.raceB.election_type)
        self.assertEqual(race_long["election_type"], self.raceB.election_type)

    def test_get_candidate(self):
        """ Testing GET method on /api/candidates endpoint """
        self.populate_database()
        response = self.client.get("/api/candidates/{}".format(self.candidateBB.id),
            headers=[("Accept", "application/json")])
        longURL_response = self.client.get(
            "/api/elections/{}/races/{}/candidates/{}".format(
                self.electionA.id, self.raceB.id, self.candidateBB.id),
            headers=[("Accept", "application/json")])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(longURL_response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(longURL_response.mimetype, "application/json")

        candidate = json.loads(response.data.decode("ascii"))
        candidate_long = json.loads(longURL_response.data.decode("ascii"))
        self.assertEqual(candidate["title"], "Candidate BB")
        self.assertEqual(candidate["race_id"], self.candidateBB.race_id)
        self.assertEqual(candidate_long["race_id"], self.candidateBB.race_id)

    def test_get_nonexistant_data(self):
        """ Tests GET requests for nonexistant data """
        response = self.client.get("/api/elections/1",
            headers=[("Accept", "application/json")])

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data["message"], "Could not find election with id 1")

    def test_post_user(self):
        """Test POST method for Users"""
        data = {
        "name": "Francis",
        "email": "francis@francis.com",
        "password": "asdf"
        }

        response = self.client.post("/api/users",
              data=json.dumps(data),
              content_type="application/json",
              headers=[("Accept", "application/json")]
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(urlparse(response.headers.get("Location")).path,
            "/api/elections")

        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["name"], "Francis")

        users = session.query(models.User).all()
        self.assertEqual(len(users), 1)

        user = users[0]
        self.assertEqual(user.name, "Francis")

    def test_POST_election(self):
        """Test POST method for election"""
        self.init_elect_types()
        userA = models.User(
            name = "UserA",
            email = "userA@eLect.com",
            password = "asdf")
        session.add(userA)
        session.commit()

        data = {
        "title": "Election A",
        "admin_id": userA.id
        }

        response = self.client.post("/api/elections",
              data=json.dumps(data),
              content_type="application/json",
              headers=[("Accept", "application/json")]
          )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(urlparse(response.headers.get("Location")).path,
            "/api/elections/1")

        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["title"], "Election A")

        elections = session.query(models.Election).all()
        self.assertEqual(len(elections), 1)

        election = elections[0]
        self.assertEqual(election.title, "Election A")

    def test_POST_race(self):
        """Test POST method for Race"""
        self.init_elect_types()
        userA = models.User(
            name = "UserA",
            email = "userA@eLect.com",
            password = "asdf")
        session.add(userA)
        session.commit()

        electionA = models.Election(
            title = "Election A",
            admin_id = userA.id,
            )
        session.add(electionA)
        session.commit()

        data = {
        "title": "Race A",
        "election_id": electionA.id
        }

        response = self.client.post("/api/races",
            data=json.dumps(data),
            content_type="application/json",
            headers=[("Accept", "application/json")]
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(urlparse(response.headers.get("Location")).path,
            "/api/races/1")

        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["title"], "Race A")

        races = session.query(models.Race).all()
        self.assertEqual(len(races), 1)

        race = races[0]
        self.assertEqual(race.title, "Race A")

    def test_POST_candidate(self):
        """Test POST method for Candidate"""
        self.init_elect_types()
        userA = models.User(
            name = "UserA",
            email = "userA@eLect.com",
            password = "asdf")
        session.add(userA)
        session.commit()

        electionA = models.Election(
            title = "Election A",
            admin_id = userA.id,
            )
        session.add(electionA)
        session.commit()

        raceA = models.Race(
            title = "Race A",
            election_id = electionA.id
            )
        session.add(raceA)
        session.commit()

        data = {
        "title": "Candidate A",
        "race_id": raceA.id
        }

        response = self.client.post("/api/candidates",
            data=json.dumps(data),
            content_type="application/json",
            headers=[("Accept", "application/json")]
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(urlparse(response.headers.get("Location")).path,
            "/api/candidates/1")

        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["title"], "Candidate A")

        candidates = session.query(models.Candidate).all()
        self.assertEqual(len(candidates), 1)

        candidate = candidates[0]
        self.assertEqual(candidate.title, "Candidate A")

    def test_POST_vote(self):
        """Test POST method for Vote, and checks for already voted error"""
        self.init_elect_types()
        userA = models.User(
            name = "UserA",
            email = "userA@eLect.com",
            password = "asdf")
        session.add(userA)
        session.commit()

        electionA = models.Election(
            title = "Election A",
            admin_id = userA.id,
            )
        session.add(electionA)
        session.commit()

        raceA = models.Race(
            title = "Race A",
            election_id = electionA.id
            )
        session.add(raceA)
        session.commit()

        candidateA = models.Candidate(
            title = "Candidate A",
            race_id = raceA.id)
        session.add(candidateA)
        session.commit()

        data = {
        "value": 1,
        "user_id": userA.id,
        "candidate_id": candidateA.id
        }

        response = self.client.post("/api/votes",
            data=json.dumps(data),
            content_type="application/json",
            headers=[("Accept", "application/json")]
        )

        data = json.loads(response.data.decode("ascii"))

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(urlparse(response.headers.get("Location")).path,
            "/api/elections/{}".format(electionA.id))

        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data["value"], 1)
        self.assertEqual(data["candidate_id"], candidateA.id)

        votes = session.query(models.Vote).all()
        self.assertEqual(len(votes), 1)

        vote = votes[0]
        self.assertEqual(vote.user_id, userA.id)

        # Try POST same vote again to test for already voted error
        vote_count = session.query(models.Vote).filter(
        models.Vote.user_id == userA.id,
        models.Vote.candidate_id == candidateA.id).count()
        self.assertEqual(vote_count, 1)

        data = {
        "value": 1,
        "user_id": userA.id,
        "candidate_id": candidateA.id
        }

        response = self.client.post("/api/votes",
            data=json.dumps(data),
            content_type="application/json",
            headers=[("Accept", "application/json")]
        )

        data = json.loads(response.data.decode("ascii"))

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data["message"],
        "User with id {} has already voted for candidate with id {}.".format(
            userA.id, candidateA.id))

    def test_invalid_header_data(self):
        """Tests invalid JSON schema for POST/PUT endpoints"""
        elect_data = {
        "title": "Election A",
        "admin_id": 1,
        "default_election_type": "WinnerTakeAll"
        }

        race_data = {
        "title": "Race A",
        "elect_id": 1
        }

        cand_data = {
        "name": "Candidate A",
        "race_id": 1
        }

        vote_data = {
        "value": "1",
        "user_id": 1,
        "candidate_id": 1
        }

        user_data = {
        "name": "User A",
        "password": "whatever",
        }

        datalist = [elect_data, race_data, cand_data, vote_data, user_data]
        endpoint_list = ["elections", "races", "candidates", "votes", "users"]
        endpoint_data_dict = dict(zip(endpoint_list, datalist))

        for endpoint, data in endpoint_data_dict.items():
            response = self.client.post("/api/{}".format(endpoint),
                data=json.dumps(data),
                content_type="application/json",
                headers=[("Accept", "application/json")]
            )
            self.assertEqual(response.status_code, 422)
            self.assertEqual(response.mimetype, "application/json")

    def test_tally_no_races(self):
        """Test for NoRaces exception to be raised by check_race()"""
        self.init_elect_types()

        userA = models.User(
            name = "UserA",
            email = "userA@eLect.com",
            password = "asdf")

        session.add(userA)
        session.commit()

        electionA = models.Election(
            title = "Election A",
            admin_id = userA.id)

        session.add(electionA)
        session.commit()

        with self.assertRaises(NoRaces):
            self.wta.check_race(1)

        with self.assertRaises(NoRaces):
            self.proportional.check_race(1)

        with self.assertRaises(NoRaces):
            self.schulze.check_race(1)

    def test_tally_no_candidates(self):
        """Test for NoCandidates exception to be raised by check_race()"""
        self.init_elect_types()

        userA = models.User(
            name = "UserA",
            email = "userA@eLect.com",
            password = "asdf")

        session.add(userA)
        session.commit()

        electionA = models.Election(
            title = "Election A",
            admin_id = userA.id)

        session.add(electionA)
        session.commit()

        raceA = models.Race(
            title = "Race A",
            election_id = electionA.id
            )

        session.add(raceA)
        session.commit()

        with self.assertRaises(NoCandidates):
            self.wta.check_race(raceA.id)

        with self.assertRaises(NoCandidates):
            self.proportional.check_race(raceA.id)

        with self.assertRaises(NoCandidates):
            self.schulze.check_race(raceA.id)

    def test_tally_no_votes(self):
        """Test for NoVotes exception to be raised by check_race()"""
        self.populate_database()
        self.electionA.elect_open = False
        with self.assertRaises(NoVotes):
            self.wta.check_race(self.raceA.id)

        with self.assertRaises(NoVotes):
            self.proportional.check_race(self.raceA.id)

        with self.assertRaises(NoVotes):
            self.schulze.check_race(self.raceA.id)

    def test_closed_election(self):
        """Test open/closed election conditions"""
        self.populate_database()
        self.voteA1 = models.Vote(
            value = 1,
            candidate_id = self.candidateAA.id,
            user_id = self.userA.id)
        self.voteA2 = models.Vote(
            value = 1,
            candidate_id = self.candidateAA.id,
            user_id = self.userB.id)
        self.voteA3 = models.Vote(
            value = 1,
            candidate_id = self.candidateAB.id,
            user_id = self.userC.id)
        self.electionA.elect_open = True
        session.add_all([
            self.voteA1,
            self.voteA2,
            self.voteA3])
        session.commit()

        with self.assertRaises(OpenElection):
            self.wta.check_race(self.raceA.id)
        with self.assertRaises(OpenElection):
            self.proportional.check_race(self.raceA.id)
        with self.assertRaises(OpenElection):
            self.schulze.check_race(self.raceA.id)

        self.electionA.elect_open = False

        highscore_winners = self.wta.tally_race(self.raceA.id)
        self.assertEqual(highscore_winners, {1:2})

        data = {
        "candidate_id": self.candidateAA.id,
        "user_id": 1,
        "value": 1 
        }

        candidate = session.query(models.Candidate).get(1)
        elect_id = candidate.race.election.id
        response = self.client.post("/api/votes",
            data=json.dumps(data),
            content_type="application/json",
            headers=[("Accept", "application/json")])
        response_json = json.loads(response.data.decode("ascii"))
        self.assertEqual(response_json["message"],
         "Election with id {} is currently closed, and not accepting new votes.".format(
            elect_id))

    def test_race_max_vote_val_onupdate(self):
        """Test the race methods that automatically check and adjust 
        the min and max vote values for ranking type elections on update"""
        self.populate_database()
        self.assertEqual(len(self.raceB.candidates), 4)
        self.assertEqual(self.raceB.min_vote_val, 0)
        self.assertEqual(self.raceB.max_vote_val, 1)

        self.raceB.election_type = "Schulze"
        self.assertEqual(len(self.raceB.candidates), 4)
        self.assertEqual(self.raceB.min_vote_val, 0)
        self.assertEqual(self.raceB.max_vote_val, 4)

        ### WHY DO THESE WORK:
        self.raceB.candidates.append(self.candidateAB)
        self.assertEqual(len(self.raceB.candidates), 5)
        self.assertEqual(self.raceB.min_vote_val, 0)
        self.assertEqual(self.raceB.max_vote_val, 5)

        self.raceB.max_vote_val = 1
        self.raceB.candidates.remove(self.candidateBD)

        self.assertEqual(len(self.raceB.candidates), 4)
        self.assertEqual(self.raceB.min_vote_val, 0)
        self.assertEqual(self.raceB.max_vote_val, 4)

        ### BUT THESE DO NOT ?!?!? ( obviously indirect changes to the 
        ### db/collection aren't handled by the validator event)
        # session.delete(self.candidateBD)
        # self.candidateAB.race_id = self.raceB.id

        # self.assertEqual(0,1)

    def test_tally_WTA(self):
        """Test standard Winner-Take-All tallying"""
        self.populate_database()

        self.voteA1 = models.Vote(
            value = 1,
            candidate_id = self.candidateAA.id,
            user_id = self.userA.id)
        self.voteA2 = models.Vote(
            value = 1,
            candidate_id = self.candidateAA.id,
            user_id = self.userB.id)
        self.voteA3 = models.Vote(
            value = 1,
            candidate_id = self.candidateAB.id,
            user_id = self.userC.id)

        self.voteB1 = models.Vote(
            value = 1,
            candidate_id = self.candidateBA.id,
            user_id = self.userA.id)
        self.voteB2 = models.Vote(
            value = 1,
            candidate_id = self.candidateBB.id,
            user_id = self.userB.id)

        session.add_all([
            self.voteA1,
            self.voteA2,
            self.voteA3,
            self.voteB1,
            self.voteB2])
        session.commit()

        votes_cast = utils.num_votes_cast(self.raceA.id)
        self.assertEqual(votes_cast, 3)
        # Close election
        self.electionA.elect_open = False
        # Tally
        highscore_winners = self.wta.tally_race(self.raceA.id)
        winner_ids = list(highscore_winners.keys())
        winners = session.query(models.Candidate).filter(
            models.Candidate.id.in_(winner_ids)).all()

        response = self.client.get("/api/races/{}/tally".format(self.raceA.id),
            headers=[("Accept", "application/json")])
        longURL_response = self.client.get(
            "/api/elections/{}/races/{}/tally".format(
                self.electionA.id, self.raceA.id),
            headers=[("Accept", "application/json")])
        
        results = json.loads(response.data.decode("ascii"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(longURL_response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(longURL_response.mimetype, "application/json")

        self.assertEqual(highscore_winners[1], 2)
        self.assertEqual(winners[0].id, 1)

        results_long = json.loads(longURL_response.data.decode("ascii"))
        # I don't know why it turns the key into a str, but the value is still int
        self.assertEqual(results["1"], 2)
        self.assertEqual(results_long["1"], 2)


    def test_tally_WTA_tied(self):
        """Tests tallying of tied race"""
        self.populate_database()

        self.voteA1 = models.Vote(
            value = 1,
            candidate_id = self.candidateAA.id,
            user_id = self.userA.id)
        self.voteA2 = models.Vote(
            value = 0,
            candidate_id = self.candidateAA.id,
            user_id = self.userB.id)
        self.voteA3 = models.Vote(
            value = 1,
            candidate_id = self.candidateAB.id,
            user_id = self.userC.id)

        session.add_all([
            self.voteA1,
            self.voteA2,
            self.voteA3])
        session.commit()

        self.electionA.elect_open = False
        highscore_winners = self.wta.tally_race(self.raceA.id)
        # How to use assertRaises correctly:
        with self.assertRaises(TiedResults):
            self.wta.check_results(highscore_winners)

        response = self.client.get("/api/races/{}/tally".format(self.raceA.id),
            headers=[("Accept", "application/json")])
        longURL_response = self.client.get(
            "/api/elections/{}/races/{}/tally".format(
                self.electionA.id, self.raceA.id),
            headers=[("Accept", "application/json")])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(longURL_response.status_code, 400)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(longURL_response.mimetype, "application/json")

        error = json.loads(response.data.decode("ascii"))
        self.assertEqual(error["message"], "Tally Error: Election tied between cand_ids [1, 2]")


    def test_tally_proportional(self):
        """Test standard Proportional tallying"""
        self.populate_database(election_type="Proportional")

        self.voteA1 = models.Vote(
            value = 1,
            candidate_id = self.candidateAA.id,
            user_id = self.userA.id)
        self.voteA2 = models.Vote(
            value = 1,
            candidate_id = self.candidateAA.id,
            user_id = self.userB.id)
        self.voteA3 = models.Vote(
            value = 1,
            candidate_id = self.candidateAB.id,
            user_id = self.userC.id)

        session.add_all([
            self.voteA1,
            self.voteA2,
            self.voteA3])
        session.commit()

        self.electionA.elect_open = False
        results = self.proportional.tally_race(self.raceA.id)

        self.assertEqual(results[1], 2/3)
        self.assertEqual(results[2], 1/3)

    def test_tally_Schulze(self):
        """Test standard Schulze tally """
        self.populate_database(election_type="Schulze")

        uAvote1 = models.Vote(
            user = self.userA,
            candidate = self.candidateBA,
            value =5)
        uAvote2 = models.Vote(
            user = self.userA,
            candidate = self.candidateBB,
            value = 0)
        uAvote3 = models.Vote(
            user = self.userA,
            candidate = self.candidateBC,
            value = 3)
        uAvote4 = models.Vote(
            user = self.userA,
            candidate = self.candidateBD,
            value = -2)

        uBvote1 = models.Vote(
            user = self.userB,
            candidate = self.candidateBA,
            value = 6)
        uBvote2 = models.Vote(
            user = self.userB,
            candidate = self.candidateBB,
            value = 1)
        uBvote3 = models.Vote(
            user = self.userB,
            candidate = self.candidateBC,
            value = -2)
        uBvote4 = models.Vote(
            user = self.userB,
            candidate = self.candidateBD,
            value = 5)

        uCvote1 = models.Vote(
            user = self.userC,
            candidate = self.candidateBA,
            value = -2)
        uCvote2 = models.Vote(
            user = self.userC,
            candidate = self.candidateBB,
            value = 5)
        uCvote3 = models.Vote(
            user = self.userC,
            candidate = self.candidateBC,
            value = 2)
        uCvote4 = models.Vote(
            user = self.userC,
            candidate = self.candidateBD,
            value = 3)
        # Check gen_pair_results() method in Schulze()
        cand_pair_results = self.schulze.gen_pair_results(self.raceB)
        # Generate expected pair_results dict for comparitive purposes
        vote2 = aliased(models.Vote, name="vote2")
        expected_pair_results = {}
        for cand1, cand2 in cand_pair_results.keys():
            preferred_expected = 0
            for user in [self.userA, self.userB, self.userC]:
                v1, v2 = session.query(
                    models.Vote.value.label("vote1"),
                    vote2.value.label("vote2")).filter(
                    models.Vote.user_id == user.id,
                    vote2.user_id == user.id,
                    models.Vote.candidate_id == cand1,
                    vote2.candidate_id == cand2).all()[0]
                if v1 > v2:
                    preferred_expected += 1
            expected_pair_results[(cand1, cand2)] = preferred_expected
            self.assertEqual(cand_pair_results[(cand1, cand2)],
                expected_pair_results[(cand1, cand2)])

        final_result = self.schulze.tally_race(self.raceB.id)

        self.dbresults = models.Results(
            race_id = self.raceB.id,
            results = final_result) 
        session.add(self.dbresults)
        session.commit()

        # JSON doesn't allow dict keys as anything but strings, so 
        # the original model's keys must be converted for comparative
        # purposes
        print("results", self.dbresults.results)
        final_result_keys_to_str = utils.dict_keys_to_str(final_result.items())

        self.assertEqual(final_result, {3:True, 4:False, 5:False, 6:False})
        self.assertEqual(self.dbresults.results, final_result_keys_to_str)
        self.assertEqual(self.dbresults.election_type, self.raceB.election_type)
        # self.assertEqual(1,0)



    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)


