import fish
import rulesmodel
import sys
import random
import math
import statistics

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


def play_game(s = None):
    turns = 0
    turns_per_player = [0 for i in range(PLAYERS)]
    sets_left = DECK_LEN/HS_LEN 
    players = [i for i in range(PLAYERS)]
    
    time_since_transfer = 0

    current_game = fish.Fish(seed=s)
    start_cards = [list(current_game.cards[i]) for i in players]
    halfsuit_declarations= {0: [0,0],  1: [0,0]}
    
    #print(start_cards)
    models = [rulesmodel.RulesModel(i, get_team(i), get_otherteam(i), start_cards[i]) for i in players]
    current_player = 0
    while (current_game.team_won() is None):
        # have the model(player) decide what card to ask for
        
        (action, action_support) = models[current_player].take_action(time_since_transfer)

        if action == 1: # declared a halfsuit
            evidence = action_support[0]
            result = current_game.declare_halfsuit(current_player, evidence)
            if result is None:
                raise Exception(" They declared a halfsuit that was invalid! Oh no!")
            

            player_team = current_player//3
            was_successful = result[0]

            #print("player: ", current_player, " team is ", player_team)
            #print("Prior halfsuit declarations = ", halfsuit_declarations)
            if was_successful:
                halfsuit_declarations[player_team][0] += 1
                #print("declared correctly, increment hafsuit : ")
            else:
                halfsuit_declarations[player_team][1] += 1

            sets_left -= 1
            halfsuit = action_support[1]
            was_successful = result[0]
            # print("The set ", evidence, " was declared " + "successfully." if was_successful else "unsuccessfully.")
            card_locations = result[1]
            for player in players: # each player records the action
                models[player].claim_halfsuit(get_team(current_player), halfsuit, was_successful, card_locations)
            
        else:
            askee = action_support[0]
            card = action_support[1]
            transfer = current_game.perform_action(current_player, askee, card)
            if transfer is None:
                raise Exception("Invalid ask for card!")
            #print("Player ", current_player, " asks ", askee, " for card ", card)
            if transfer: 
                time_since_transfer = 0
                #print(askee, "had card ", card)
                start_cards = [list(current_game.cards[i]) for i in players]
    
                #print(start_cards)
                # input("")
            #else :
                #print(askee, "did not have card ", card)
            # update who has what card in the fish game
            for player in players: # each player records the action
                models[player].record_action(current_player, askee, card, transfer)
            
            if not transfer:
                # if current_player
                time_since_transfer += 1
                current_player = askee

        if current_game.team_won() is not None:
            break

        #print(current_game.cards_left(current_player))
        if current_game.cards_left(current_player) == 0:
            #print("prev current player = ", current_player)
            team = get_team(current_player)
            swap = False
            valid_players = []
            for player in team:
                if current_game.cards_left(player):
                    valid_players.append(player)
                    swap = True
                
            if not swap:
                
                for player in get_otherteam(current_player):
                    if current_game.cards_left(player):
                        valid_players.append(player)
            
            current_player = random.choice(valid_players)
            #print("new current player = ", current_player)
               
        # check if a player declared a halfsuit, and then decriment it
        turns += 1
        turns_per_player[current_player] += 1

        #print("Current player = ", current_player)
        #print("turns since transfer = ", time_since_transfer)
        #current_game.print_curr_state()
        #print("\n")


    #print("Game ended!")
    #print("halfsuits per team ", current_game.half_suits_per_team)
    #print("Team that won ", current_game.team_won())
    #print("Halfsuit declarations = ", halfsuit_declarations)
    #print("\n")
    return halfsuit_declarations, current_game.team_won()


def main():
    """if len(sys.argv) != 3:
        raise Exception("usage: python project1.py <infile>.csv <outfile>")

    inputfilename = sys.argv[1]
    outputfilename = sys.argv[2]
    policy = compute(inputfilename, outputfilename)"""
    #play_game(s = 1501)



    win_percent = []
    loss_percent = []
    for i in range(1, 1500):
        if i % 100:
            print("Game seed is = ", i)
            
        hd, winner = play_game(s = i)

        loser = 0
        if winner == 0:
            loser = 1

        if sum(hd[winner]) != 0:
            #print("win percent = ", hd[winner][0]/sum(hd[winner]))
            win_percent.append(hd[winner][0]/sum(hd[winner]))
        else:
            win_percent.append(0)

        if sum(hd[loser]) != 0:
            #print("loss percent = ", hd[loser][0]/sum(hd[loser]))
            loss_percent.append(hd[loser][0]/sum(hd[loser]))
        else:
            loss_percent.append(0)
        
        
    print("percent correct, winning team = ", statistics.mean(win_percent))
    print("percent correct, losing team = ", statistics.mean(loss_percent))
        





if __name__ == '__main__':
    main()

    

    



        



