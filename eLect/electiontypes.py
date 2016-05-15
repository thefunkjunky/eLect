import os
import json

from eLect.main import app
from eLect import models
from eLect.database import Base, engine, session



class WinnerTakeAll(Object):
    """ Winner-Take-All elections class"""
    def __init__(self):
        # super(WinnerTakeAll, self).__init__()
        self.title = "Winner-Take-All"
        self.description_short = "Voter may choose only one of all the candidates, and only one winner may be declared." 
        self.description_long = "Good for up/down single vote issues and proposals, and two-party races."

class Proportional(Object):
    """ Proportional elections class"""
    def __init__(self):
        # super(Proportional, self).__init__()
        self.title = "Proportional"
        self.description_short = "Voter may choose only one of all the candidates, but all candidates are tallied proportionally in percentages." 
        self.description_long = "Good for determining each candidate's percentage of the overall vote, and Parliamentary-style elections."

class Schulze(Object):
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




