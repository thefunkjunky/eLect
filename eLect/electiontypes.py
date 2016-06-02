import os
import json
from operator import itemgetter

from sqlalchemy import text
from sqlalchemy.sql import func, select
from sqlalchemy.orm import aliased, with_polymorphic
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from eLect.main import app
from eLect.custom_exceptions import *
from eLect.utils import num_votes_cast
from eLect import models
from eLect.models import ElectionType
from eLect.database import Base, engine, session



class WinnerTakeAll(ElectionType):
    """ Winner-Take-All elections class """
    def __init__(self):
        # super().__init__()
        self.election_type = "WTA"
        self.title = "Winner-Take-All"
        self.description_short = "Voter may select one candidate,"\
        " and one winner is declared based upon a simple majority."
        self.description_long = "Good for up/down single vote issues and proposals,"\
        " and races with only 2 candidates.  Possibility of ties and other problems "\
        "makes this option less attractive than other options, despite its popularity."

    @hybrid_method
    def tally_race(self, race_id):
        """ Tallies the votes for a race. Returns a dict of {cand.ids:score} """

        # Checks race conditions before attempts at tallying
        self.check_race(race_id)

        # # The easy-to-read way of doing this
        try:
            results = session.query(
                func.sum(models.Vote.value)).add_column(
                models.Vote.candidate_id).filter(
                models.Vote.candidate.has(race_id = race_id)).group_by(
                models.Vote.candidate_id).all()
        except Exception as e:
            # TODO: Find better way to Except. what to return here?
            return None

        # # The supposedly faster way of doing this
        # results = session.query(
        #     func.count(models.Vote.value)).add_column(
        #     models.Vote.candidate_id).join(
        #     models.Vote.candidate, aliased = True).filter_by(
        #     race_id = race_id).group_by(
        #     models.Vote.candidate_id).all()
        if len(results) > 1 :
            highscore = max(results, key=itemgetter(0))[0]
            highscore_winners = {cand:score for score, cand in results if score == highscore}

        return highscore_winners

    @hybrid_method
    def check_results(self, results):
        """ Checks the results returned by the WTA tally_race() method """
        if not results:
            raise NoResults("No results found")
        if len(results) < 1:
            raise NoWinners("No winners found")
        if len(results) > 1:
            raise TiedResults("Election tied between cand_ids {}".format(
                list(results.keys())))

    @staticmethod
    def fetch():
        """Bill, what the hell am I doing here?"""
        query = session.query(models.ElectionType).get(1)
        return WinnerTakeAll()

class Proportional(ElectionType):
    """ Proportional elections class. Returns a dict of cand.ids:score"""
    def __init__(self):
        # super(Proportional, self).__init__()
        self.election_type = "Proportional"
        self.title = "Proportional"
        self.description_short = "Voter may choose one candidate, "\
        "and all candidates are tallied proportinally to each other as "\
        "a percentage."
        self.description_long = "Good for Parliamentary-style elections, "\
        "or in races where having a single winner is less important than having "\
        "all candidates ranked according to their percentage of the overall vote."

    @hybrid_method
    def tally_race(self, race_id):
        """ Tallies the votes for race_id with election_type = "Proportional" """

        # # The easy-to-read way of doing this
        # SEE WTA for a quicker method (commented out)
        results = session.query(
            func.sum(models.Vote.value)).add_column(
            models.Vote.candidate_id).filter(
            models.Vote.candidate.has(race_id = race_id)).group_by(
            models.Vote.candidate_id).all()

        total_scores = session.query(
            func.sum(models.Vote.value)).filter(
            models.Vote.candidate.has(race_id = race_id))[0][0]

        calculated_results = {cand: score/total_scores for score, cand in results}

        return calculated_results

    @hybrid_method
    def check_results(self, results):
        """ Checks the results returned by the Proportional tally_race() method """
        if not results:
            raise NoResults("No results found")
        # if len(results) < 1:
        #     raise NoWinners("No winners found")


class Schulze(ElectionType):
    """ Schulze elections class """
    def __init__(self):
        # super(Schulze, self).__init__()
        self.election_type = "Schulze"
        self.title = "Schulze (Condorcet)"
        self.description_short = "Voter may rank ALL candidates in relation to each other." 
        self.description_long = "Offers voters the most power for their vote. "\
        "Ability to rank all candidates relative to each other allows voters to give "\
        "higher preferences to their preferred candidates, without taking votes away "\
        "from their 2nd, 3rd, etc. choices.  Fosters true multi-party systems, "\
        "prevents ties and eliminates the need for recounts, among many other advantages.\n"\
        "The best option for races with 3 or more candidates, that must end with a single winner."

    @hybrid_method
    def gen_pair_results(self, race):
        """Method required by Schulze tally_race() that generates 
        dict of key:value pairs, defined as 
        (candA, CandB) tuple of unique canididate pairs from race:
        # of voters who preferred candA over candB on each individual ballot """

        pair_results = {}
        ### Original SELECT from previous version
        ## NOTE: previous version used a BALLOT table, which represented 
        ##      all of a user's votes for a given race
        ##      Let's try to do this without creating a (permanent) ballot table
        ##      Maybe create a View, or temporary table
        #
        # SELECT tmp.cand1 As 'candidate1', tmp.cand2 AS 'candidate2', COUNT(*) FROM 
        # ( SELECT v1.`ballot_id`, v1.cand_id AS 'cand1', v1.score AS 'score1', v2.cand_id AS 'cand2', v2.score AS 'score2' 
        # FROM votes v1 INNER JOIN votes v2 
        # ON (v1.ballot_id = v2.ballot_id) AND v1.cand_id <> v2.cand_id ) 
        # AS tmp WHERE tmp.score1 > tmp.score2 
        # GROUP BY tmp.cand1, tmp.cand2"

        # Figure out a way to scale this appropriately 
        # in order to avoid loading too much data on large elections, or spending
        # too long on Python loops.  Remember how fast the original SELECT was


        cand2 = aliased(models.Candidate, name="cand2")
        cand_pairs = session.query(models.Candidate.id.label("cand1_id"),
        cand2.id.label("cand2_id")).filter(
            models.Candidate.race_id == race.id,
            cand2.race_id == race.id,
            models.Candidate.id != cand2.id).subquery()

        vote2 = aliased(models.Vote, name="vote_cand2")
        # where to change use_labels=True? How to access underlying select()?
        votes = session.query(models.User.id.label("user_id"), 
            cand_pairs.c.cand1_id.label("vote_cand1_id"),
            cand_pairs.c.cand2_id.label("vote_cand2_id"),
        models.Vote.value.label("vote_cand1_value"), 
        vote2.value.label("vote_cand2_value")).filter(
            models.Vote.user_id == models.User.id,
            vote2.user_id == models.User.id,
            models.Vote.candidate_id == cand_pairs.c.cand1_id,
            vote2.candidate_id == cand_pairs.c.cand2_id,
            ).subquery() 

        cand_pair_results = session.query(
            cand_pairs,
            func.count("*").label("num_users_prefer")).filter(
            votes.c.vote_cand1_id == cand_pairs.c.cand1_id,
            votes.c.vote_cand2_id == cand_pairs.c.cand2_id,
            votes.c.vote_cand1_value > votes.c.vote_cand2_value
            ).group_by(cand_pairs).order_by(
            cand_pairs.c.cand1_id, cand_pairs.c.cand2_id).all()

        dict_cand_pair_results = {(cand1, cand2):num_users_prefer for \
        cand1, cand2, num_users_prefer in cand_pair_results}
        return dict_cand_pair_results

    @hybrid_method
    def tally_race(self, race_id):
        """ Tallies the votes for race_id with election_type = "Schulze" """
        race = session.query(models.Race).get(race_id)
        pair_results = self.gen_pair_results(race)

