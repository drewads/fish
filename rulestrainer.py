import fish
import rulesmodel
import sys
import random
import math
import statistics
import deep_q_model

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

def play_game(models, s = None):
    turns = 0
    turns_per_player = [0 for i in range(PLAYERS)]
    sets_left = DECK_LEN/HS_LEN 
    players = [i for i in range(PLAYERS)]
    who_declares = []
    
    time_since_transfer = 0
    num_actions_player = dict(zip([i for i in range(PLAYERS)], [0 for _ in range(PLAYERS)]))

    current_game = fish.Fish(seed=s)
    start_cards = [list(current_game.cards[i]) for i in players]
    halfsuit_declarations= {0: [0,0],  1: [0,0]}
    for player_number, model in enumerate(models):
        model.startNewGame(player_number, get_team(player_number), get_otherteam(player_number), start_cards[player_number])
    #print(start_cards)
    current_player = 0
    while (current_game.team_won() is None):
        # have the model(player) decide what card to ask for
        
        (action, action_support) = models[current_player].take_action(time_since_transfer)

        if action == 1: # declared a halfsuit
            who_declares.append(current_player)
            print("Current player is, ", current_player)
            print(" declaring halfsuit : ")
            print(" action_support[0] = ", action_support[0])
            print(" action_support[1] = ", action_support[1])
            input("")
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
            num_actions_player[current_player] += 1
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
    return halfsuit_declarations, current_game.team_won(), who_declares, num_actions_player


def main():
    """if len(sys.argv) != 3:
        raise Exception("usage: python project1.py <infile>.csv <outfile>")

    inputfilename = sys.argv[1]
    outputfilename = sys.argv[2]
    policy = compute(inputfilename, outputfilename)"""
    #play_game(s = 1501)

    team_1_percent = []
    team_2_percent = []
    winners = []

    models = [deep_q_model.DeepQModel()] + [rulesmodel.RulesModel() for _ in range(PLAYERS - 1)]
    
    num_batches = 100
    for batch_number in range(num_batches):
        print("Playing batch", batch_number)
        for i in range(10):
            hd, winner, who_declares, num_actions_player = play_game(models)
            print("Winner is", winner)
            print("QModel declares", who_declares.count(0), "times. Team 1 declares", who_declares.count(0) + who_declares.count(1) + who_declares.count(2), "times. Team 2 declares", who_declares.count(3) + who_declares.count(4) + who_declares.count(5), "times.")
            print("Actions per player: 0:", num_actions_player[0], "1:", num_actions_player[1], "2:", num_actions_player[2], "3:", num_actions_player[3], "4:",num_actions_player[4], "5:", num_actions_player[5])
            winners.append(winner)

            if sum(hd[0]) != 0:
                #print("win percent = ", hd[winner][0]/sum(hd[winner]))
                team_1_percent.append(hd[0][0]/sum(hd[0]))
            else:
                team_1_percent.append(0)

            if sum(hd[1]) != 0:
                #print("loss percent = ", hd[loser][0]/sum(hd[loser]))
                team_2_percent.append(hd[1][0]/sum(hd[1]))
            else:
                team_2_percent.append(0)
        (loss_average, declare_loss_average) = models[0].train_for_iteration()
        print("loss:", loss_average, "declare loss:", declare_loss_average)
        
    print("team 1 won", winners.count(0), "times. team 2 won", winners.count(1), "times.")
    print("percent correct, team 1 = ", statistics.mean(team_1_percent))
    print("percent correct, team 2 = ", statistics.mean(team_2_percent))
        





if __name__ == '__main__':
    main()

    

    



        



