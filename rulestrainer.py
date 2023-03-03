import fish
import rulesmodel
import sys
import random

from fish import PLAYERS, TEAM_LEN, HS_LEN, DECK_LEN


# this will be a class or function that instantiates a Fish game and some models
# and then communicates between game and models

"""
This class initializes a model and a game of fish.
"""
def get_otherteam(player):
    if player <= 2:
        otherteam = [i for i in range(3,6)]
        return otherteam
    
    otherteam = [i for i in range(3)]
    return otherteam

def get_team(player):
    if player <= 2: # numplayers/2
        team = [i for i in range(3)]
        return team
    
    team = [i for i in range(3,6)]
    return team

def play_game():
    turns = 0
    turns_per_player = [0 for i in range(PLAYERS)]
    sets_left = HS_LEN/DECK_LEN
    players = [i for i in range(PLAYERS)]

    current_game = fish.Fish()
    start_cards = [list(current_game.cards[i]) for i in players]
    
    print(start_cards)
    models = [rulesmodel.RulesModel(i, get_team(i), get_otherteam(i), start_cards[i]) for i in players]
    current_player = 0
    while (sets_left > 0):
        # have the model(player) decide what card to ask for
        (action, action_support) = models[current_player].take_action()

        if action == 1: # declared a halfsuit
            evidence = action_support[0]
            was_valid = current_game.declare_halfsuit(current_player, evidence)
            if not was_valid:
                raise Exception(" They declared a halfsuit that was invalid! Oh no!")
            

            halfsuit = action_support[1]
            for player in players: # each player records the action
                models[player].claim_halfsuit(current_player, get_team(current_player), halfsuit, was_valid)
            
        else:
            askee = action_support[0]
            card = action_support[1]
            transfer = current_game.perform_action(current_player, askee, card)
            
            # update who has what card in the fish game
            for player in players: # each player records the action
                models[player].record_action(current_player, askee, card, transfer)
            
            if transfer:
                current_player = askee
        
        # check if a player declared a halfsuit, and then decriment it
        turns += 1
        turns_per_player[current_player] += 1

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

    

    



        



