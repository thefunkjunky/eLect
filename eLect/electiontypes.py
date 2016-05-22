import os
import json
from operator import itemgetter

from sqlalchemy.sql import func
from eLect.main import app
from eLect import models
from eLect.database import Base, engine, session



class WinnerTakeAll:
    """ Winner-Take-All elections class"""
    def __init__(self):
        # super(WinnerTakeAll, self).__init__()
        self.title = "Winner-Take-All"
        self.description_short = "Voter may choose only one of all the candidates, and only one winner may be declared." 
        self.description_long = "Good for up/down single vote issues and proposals,\n"\
        " and two-party races."

    def tally_race(self, race_id):
        """ Tallies the votes for a race """

        # # The easy-to-read way of doing this
        results = session.query(
            func.sum(models.Vote.value)).add_column(
            models.Vote.candidate_id).filter(
            models.Vote.candidate.has(race_id = race_id)).group_by(
            models.Vote.candidate_id).all()

        # # The supposedly faster way of doing this
        # results = session.query(
        #     func.count(models.Vote.value)).add_column(
        #     models.Vote.candidate_id).join(
        #     models.Vote.candidate, aliased = True).filter_by(
        #     race_id = race_id).group_by(
        #     models.Vote.candidate_id).all()

        highscore = max(results, key=itemgetter(0))[0]
        highscore_winners = [cand for score, cand in results if score == highscore]

        return highscore, highscore_winners



class Proportional:
    """ Proportional elections class"""
    def __init__(self):
        # super(Proportional, self).__init__()
        self.title = "Proportional"
        self.description_short = "Voter may choose only one of all the candidates, but all candidates are tallied proportionally in percentages." 
        self.description_long = "Good for determining each candidate's percentage \n"\
        "of the overall vote, and Parliamentary-style elections."

    def tally_race(self, race_id):
        """ Tallies the votes for a race """
        race = session.query("models.Race").get(race_id)

class Schulze:
    """ Schulze elections class """
    def __init__(self):
        # super(Schulze, self).__init__()
        self.title = "Schulze (Condorcet)"
        self.description_short = "Voter may rank all candidates in relation to each other." 
        self.description_long = "Offers voters the most power for their vote.\n"\
        "Ability to rank all candidates relative to each other allows voters to give\n"\
        "higher preferences to their preferred candidates, without taking votes away\n"\
        "from their 2nd, 3rd, etc. choices.  Fosters true multi-party/multi-choice systems,\n"\
        "prevents ties and eliminates the need for recounts, among other advantages.\n\n"\
        "The best option for races with 3 or more candidates, that must end with a single winner."

    def tally_race(self, race_id):
        """ Tallies the votes for a race """
        race = session.query("models.Race").get(race_id)


