### Custom exceptions for eLect project

class NoRaces(Exception):
    pass
class NoCandidates(Exception):
    pass
class NotEnoughCandidates(Exception):
    pass
class Update_elect_open_Failed(Exception):
    pass
class ClosedElection(Exception):
    pass
class OpenElection(Exception):
    pass
class NoVotes(Exception):
    pass
class AlreadyVoted(Exception):
    pass
class NoResults(Exception):
    # Just raise nonetype?
    pass
class NoWinners(Exception):
    # this might not be needed, 
    # other exceptions may offer more useful information
    pass
class TiedResults(Exception):
    pass
