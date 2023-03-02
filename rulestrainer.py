import fish
import rulesmodel
import sys
import random

PLAYERS = 6 # number of players
TEAM_LEN = 3 # number of players per team

# this will be a class or function that instantiates a Fish game and some models
# and then communicates between game and models

"""
This class initializes a model and a game of fish.

class Trainer:
    def __init__(self, tmodel, tseed):
        self.players = [tmodel() for _ in PLAYERS]
        self.playersindex = [i for i in range(PLAYERS)] # 0-2 are a team, 3-5 are a team
        self.current_game = fish(seed = tseed)

    def action(self, player, ask_player, cardOrEvidence):
        if type(cardOrEvidence) != dict:
            self.current_game.perform_action(player, ask_player, cardOrEvidence)
        else:
            self.current_game.declare_halfsuit(player, cardOrEvidence)

"""
def get_otherteam(player):
    if player <= 2:
        otherteam = [i for i in range(3,6) if i != player]
        return otherteam
    
    otherteam = [i for i in range(3) if i != player]
    return otherteam

def get_team(player):
    if player <= 2: # numplayers/2
        team = [i for i in range(3) if i != player]
        return team
    
    team = [i for i in range(3,6) if i != player]
    return team


def play_game():
    turns = 0
    sets_left = 9
    players = [i for i in range(PLAYERS)]

    current_game = fish.Fish()
    print(current_game.cards)


    start_cards = []
    models = [rulesmodel(i, get_team(i), get_otherteam(i), start_cards[i]) for i in players]
    while (sets_left > 0):
        pass

    return


def main():
    """if len(sys.argv) != 3:
        raise Exception("usage: python project1.py <infile>.csv <outfile>")

    inputfilename = sys.argv[1]
    outputfilename = sys.argv[2]
    policy = compute(inputfilename, outputfilename)"""
    play_game()




if __name__ == '__main__':
    main()

    

    



        



