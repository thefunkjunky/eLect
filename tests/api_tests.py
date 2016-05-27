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

from eLect.main import app
from eLect.main import NoRaces, NoCandidates, ClosedElection, NoVotes, NoWinners,TiedResults, NoResults, OpenElection
from eLect import models
from eLect.utils import num_votes_cast
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


    def populate_database(self, election_type=1):
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
            election_id = self.electionA.id
            )
        self.raceB = models.Race(
            title = "Race B",
            election_id = self.electionB.id
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

        session.add_all([
            self.candidateAA,
            self.candidateAB,
            self.candidateBA,
            self.candidateBB])
        session.commit()

        # Add election types
        self.wta = WinnerTakeAll()
        self.proportional = Proportional()
        self.schulze = Schulze()
        session.add_all([self.wta, self.proportional, self.schulze])
        session.commit()


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

    def test_tally_no_votes(self):
        """Test for NoVotes exception to be raised by check_race()"""
        self.populate_database()
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

        votes_cast = num_votes_cast(self.raceA.id)
        self.assertEqual(votes_cast, 3)
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
        self.assertEqual(response.status_code, 200)
        self.assertEqual(longURL_response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(longURL_response.mimetype, "application/json")

        self.assertEqual(highscore_winners[1], 2)
        self.assertEqual(winners[0].id, 1)

        results = json.loads(response.data.decode("ascii"))
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
        self.populate_database(2)

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

        results = self.proportional.tally_race(self.raceA.id)

        self.assertEqual(results[1], 2/3)
        self.assertEqual(results[2], 1/3)


    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)


