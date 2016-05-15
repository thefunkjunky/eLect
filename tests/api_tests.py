import unittest
import os
import shutil
import json
try: from urllib.parse import urlparse
except ImportError: from urlparse import urlparse # Py2 compatibility
from io import StringIO

import sys
# print(list(sys.modules.keys()))
# Configure our app to use the testing databse
os.environ["CONFIG_PATH"] = "eLect.config.TestingConfig"

from eLect.main import app
from eLect import models
from eLect.database import Base, engine, session



class TestAPI(unittest.TestCase):
    """ Tests for the API """

    def setUp(self):
        """ Test setup """
        self.client = app.test_client()

        # Set up the tables in the database
        Base.metadata.create_all(engine)

    def populate_database(self):
        userA = models.User(
            name = "UserA",
            email = "userA@eLect.com",
            password = "asdf")
        userB = models.User(
            name = "UserB",
            email = "userB@eLect.com",
            password = "asdf")
        typeA = models.ElectionType(
            title = "Election type A"
            )
        typeB = models.ElectionType(
            title = "Election type B"
            )
        electionA = models.Election(
            title = "Election A",
            default_elect_type = typeA.id,
            admin_id = userA.id
            )
        electionB = models.Election(
            title = "Election A",
            default_elect_type = typeB.id,
            admin_id = userB.id
            )
        raceA = models.Race(
            title = "Race A",
            election_id = electionA.id
            )
        raceB = models.Race(
            title = "Race B",
            election_id = electionB.id
            )
        candidateAA = models.Candidate(
            title = "Candidate AA",
            race_id = raceA.id)
        candidateAB = models.Candidate(
            title = "Candidate AB",
            race_id = raceA.id)
        candidateBA = models.Candidate(
            title = "Candidate BA",
            race_id = raceB.id)
        candidateBB = models.Candidate(
            title = "Candidate BB",
            race_id = raceB.id)
        voteA1 = models.Vote(
            value = 1,
            candidate_id = candidateAA.id,
            user_id = userA.id)
        voteA2 = models.Vote(
            value = 1,
            candidate_id = candidateAA.id,
            user_id = userB.id)
        voteB1 = models.Vote(
            value = 1,
            candidate_id = candidateBA.id,
            user_id = userA.id)
        voteB2 = models.Vote(
            value = 1,
            candidate_id = candidateBB.id,
            user_id = userB.id)

        session.add_all([userA,
            userB,
            typeA,
            typeB,
            electionA,
            electionB,
            raceA,
            raceB,
            candidateAA,
            candidateAB,
            candidateBA,
            candidateBB,
            voteA1,
            voteA2,
            voteB1,
            voteB2])
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
        electionB = session.query(models.Election).filter(
            models.Election.title == "Election B")
        response = self.client.get("/api/elections/{}".format(electionB.id),
            headers=[("Accept", "application/json")])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

        election = json.loads(response.data.decode("ascii"))
        self.assertEqual(election["title"], "Election B")
        self.assertEqual(election["admin_id"], electionB.admin_id)

    def test_get_race(self):
        """ Testing GET method on /api/races endpoint """
        self.populate_database()
        raceB = session.query(models.Race).filter(
            models.Race.title == "Race B")
        response = self.client.get("/api/races/{}".format(raceB.id),
            headers=[("Accept", "application/json")])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

        race = json.loads(response.data.decode("ascii"))
        self.assertEqual(race["title"], "Race B")
        self.assertEqual(race["election_type"], raceB.election_type)

    def test_get_candidate(self):
        """ Testing GET method on /api/candidates endpoint """
        self.populate_database()
        candidateBB = session.query(models.Candidate).filter(
            models.Candidate.title == "Candidate BB")
        response = self.client.get("/api/candidates/{}".format(candidateBB.id),
            headers=[("Accept", "application/json")])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

        candidate = json.loads(response.data.decode("ascii"))
        self.assertEqual(candidate["title"], "Candidate BB")
        self.assertEqual(candidate["race_id"], candidateBB.race_id)

    def test_get_nonexistant_data(self):
        """ Tests GET requests for nonexistant data """
        response = self.client.get("/api/elections/1",
            headers=[("Accept", "application/json")])

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data["message"], "Could not find election with id 1")



    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)


