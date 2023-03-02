import fish
import rulesmodel
import sys
import matplotlib.pyplot as plt
import math
import numpy as np
import pandas as pd
import random
from tqdm import tqdm

PLAYERS = 6 # number of players
TEAM_LEN = 3 # number of players per team


# this will be a class or function that instantiates a Fish game and some models
# and then communicates between game and models

# initialize a trainer

"""
This class initializes a model and a game of fish.
"""
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





def main():
    """if len(sys.argv) != 3:
        raise Exception("usage: python project1.py <infile>.csv <outfile>")

    inputfilename = sys.argv[1]
    outputfilename = sys.argv[2]
    policy = compute(inputfilename, outputfilename)"""

    turns = 0
    




if __name__ == '__main__':
    main()

    

    



        



