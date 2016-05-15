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
        self.userA = models.User(
            name = "UserA",
            email = "userA@eLect.com",
            password = "asdf")
        self.userB = models.User(
            name = "UserB",
            email = "userB@eLect.com",
            password = "asdf")

        session.add_all([self.userA,self.userB])
        session.commit()

        self.typeA = models.ElectionType(
            title = "Election type A"
            )
        self.typeB = models.ElectionType(
            title = "Election type B"
            )

        session.add_all([self.typeA,self.typeB])
        session.commit()

        self.electionA = models.Election(
            title = "Election A",
            default_elect_type = self.typeA.id,
            admin_id = self.userA.id
            )
        self.electionB = models.Election(
            title = "Election B",
            default_elect_type = self.typeB.id,
            admin_id = self.userB.id
            )

        session.add_all([self.electionA,self.electionB])
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

        session.add_all([self.candidateAA,self.candidateAB,self.candidateBA,self.candidateBB])
        session.commit()

        self.voteA1 = models.Vote(
            value = 1,
            candidate_id = self.candidateAA.id,
            user_id = self.userA.id)
        self.voteA2 = models.Vote(
            value = 1,
            candidate_id = self.candidateAA.id,
            user_id = self.userB.id)
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
            self.voteB1,
            self.voteB2])
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
        # raceB = session.query(models.Race).filter(
        #     models.Race.title == "Race B")
        response = self.client.get("/api/races/{}".format(self.raceB.id),
            headers=[("Accept", "application/json")])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

        race = json.loads(response.data.decode("ascii"))
        self.assertEqual(race["title"], "Race B")
        self.assertEqual(race["election_type"], self.raceB.election_type)

    def test_get_candidate(self):
        """ Testing GET method on /api/candidates endpoint """
        self.populate_database()
        # candidateBB = session.query(models.Candidate).filter(
        #     models.Candidate.title == "Candidate BB")
        response = self.client.get("/api/candidates/{}".format(self.candidateBB.id),
            headers=[("Accept", "application/json")])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

        candidate = json.loads(response.data.decode("ascii"))
        self.assertEqual(candidate["title"], "Candidate BB")
        self.assertEqual(candidate["race_id"], self.candidateBB.race_id)

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


