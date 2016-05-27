import os
import json
from operator import itemgetter

from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from eLect.main import app
from eLect.main import NoRaces, NoCandidates, ClosedElection, NoVotes, NoWinners,TiedResults, NoResults, OpenElection
from eLect.utils import num_votes_cast
from eLect import models
from eLect.models import ElectionType
from eLect.database import Base, engine, session



class WinnerTakeAll(ElectionType):
    """ Winner-Take-All elections class """
    def __init__(self):
        # super().__init__()
        # self.id = 1
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
        # self.id = 2
        self.title = "Proportional"
        self.description_short = "Voter may choose one candidate, "\
        "and all candidates are tallied proportinally to each other as "\
        "a percentage."
        self.description_long = "Good for Parliamentary-style elections, "\
        "or in races where having a single winner is less important than having "\
        "all candidates ranked according to their percentage of the overall vote."

    @hybrid_method
    def tally_race(self, race_id):
        """ Tallies the votes for a race """

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


class Schulze(ElectionType):
    """ Schulze elections class """
    def __init__(self):
        # super(Schulze, self).__init__()
        # self.id = 3
        self.title = "Schulze (Condorcet)"
        self.description_short = "Voter may rank ALL candidates in relation to each other." 
        self.description_long = "Offers voters the most power for their vote. "\
        "Ability to rank all candidates relative to each other allows voters to give "\
        "higher preferences to their preferred candidates, without taking votes away "\
        "from their 2nd, 3rd, etc. choices.  Fosters true multi-party systems, "\
        "prevents ties and eliminates the need for recounts, among many other advantages.\n"\
        "The best option for races with 3 or more candidates, that must end with a single winner."

    @hybrid_method
    def tally_race(self, race_id):
        """ Tallies the votes for a race """
        race = session.query("models.Race").get(race_id)

