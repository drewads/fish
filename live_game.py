import fish
import rulesmodel
import sys
import random
import math
import statistics

from fish import PLAYERS, TEAM_LEN, HS_LEN, DECK_LEN, hs_of


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

def get_team_number(player):
    return player//3

def get_action(player, current_game):
    print("Player ", player, "'s turn! ")
    print("Player ", player, " has cards, ", current_game.cards[player])
    print("This corresponds to halfsuits ; ", set([hs_of(j) for j in current_game.cards[player]]))
    
    user_input = input(" What is your action? 1 = declare halfsuit, 0 = ask for card \n")

    #while(type(user_input) != int):
    #    user_input = input("Wrong input! What is your action? 1 = declare halfsuit, 0 = ask for card \n")
    #    print(user_input)
    action = int(user_input)
    action_support = None

    if action == 1: # user is declaring a halfsuit
        print("You are declaring a halfsuit! Bold!")
        action_support = []
        correct = False
        while not correct:

            print("Now we need evidence! First, give the cards you think player 3 has: ")
            p3_cards = list(map(int, input("Player 3 cards, as a list separated by spaces: \n").split()))
            p4_cards = list(map(int, input("Player 4 cards, as a list separated by spaces: \n").split()))
            p5_cards = list(map(int, input("Player 3 cards, as a list separated by spaces: \n").split()))
            evidence = {3: p3_cards, 4: p4_cards, 5:p5_cards}

            print("your evidence is = ", evidence)
            check = str(input("Is this correct? yes if so \n"))
            if check == "yes":
                correct = True
            

        action_support.append(evidence)
        correct = False
        while not correct:

            print("Now we need more evidence! what halfsuit are you declaring ")
            hs = int(input("Halfsuit you're declaring is: \n"))

            print("Your halfsuit is = ", hs)

            check = str(input("Is this correct? yes if so \n"))
            if check == "yes":
                correct = True

        action_support.append(hs)

    else:
        print(" You are asking for cards!")
        correct = False

        while not correct:
            action_support = []
            action_support.append(int(input("The player you are asking for a card from from is: \n")))
            action_support.append(int(input("The card you are asking for is : \n")))

            print("your asking ", action_support[0], " for card ", action_support[1])

            check = str(input("Is this correct? yes if so \n"))
            if check == "yes":
                correct = True

    return (action, action_support)

def print_player_cards(players, cards):
    for i in players:
        if i > 2:
            print("Player ", i, " has cards, ", cards[i])
            print("This corresponds to halfsuits ; ", set([hs_of(j) for j in cards[i]]))
            input(" press enter to get the next players cards")
            for _ in range(15):
                print("\n")

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
    for i in players:
        if i > 2:
            print("Player ", i, " has cards, ", start_cards[i])
            input(" press enter to get the next players cards")
            for _ in range(15):
                print("\n")

    models = [rulesmodel.RulesModel(i, get_team(i), get_otherteam(i), start_cards[i]) for i in players]
    current_player = 0
    while (current_game.team_won() is None):

        if get_team_number(current_player) == 0: # Team 0 is the model team

            (action, action_support) = models[current_player].take_action(time_since_transfer)
        else: # Team 1 is the users team!
            (action, action_support) = get_action(current_player, current_game)
        
        if action == 1: # declared a halfsuit
            evidence = action_support[0]
            result = current_game.declare_halfsuit(current_player, evidence)
            if result is None:
                raise Exception(" They declared a halfsuit that was invalid! Oh no!")
            
            player_team = current_player//3
            was_successful = result[0]

            if was_successful:
                halfsuit_declarations[player_team][0] += 1
            else:
                halfsuit_declarations[player_team][1] += 1

            sets_left -= 1
            halfsuit = action_support[1]
            was_successful = result[0]
            print("The set ", evidence, " was declared successfully." if was_successful else " was declared unsuccessfully.")
            card_locations = result[1]

            for player in players: # each player records the action
                models[player].claim_halfsuit(get_team(current_player), halfsuit, was_successful, card_locations)
            
        else:
            askee = action_support[0]
            card = action_support[1]
            transfer = current_game.perform_action(current_player, askee, card)
            if transfer is None:
                raise Exception("Invalid ask for card!")
            print("Player ", current_player, " asks ", askee, " for card ", card)
            if transfer: 
                time_since_transfer = 0
                print(askee, "had card ", card)
                start_cards = [list(current_game.cards[i]) for i in players]

            else :
                print(askee, "did not have card ", card)

            for player in players: # each player records the action
                models[player].record_action(current_player, askee, card, transfer)
            
            if not transfer:
                time_since_transfer += 1
                current_player = askee


        if current_game.team_won() is not None:
            break

        if current_game.cards_left(current_player) == 0:
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
               
        turns += 1
        turns_per_player[current_player] += 1

        #print("turns since transfer = ", time_since_transfer)
        #current_game.print_curr_state()
        print("Turn ended! ")
        print_cards = input("Type any key to get all players cards")

        if print_cards:
            print_player_cards(players, current_game.cards)

        input("Press enter for next turn!")
        for _ in range(20):
            print("\n")


    #print("Game ended!")
    #print("halfsuits per team ", current_game.half_suits_per_team)
    #print("Team that won ", current_game.team_won())
    #print("Halfsuit declarations = ", halfsuit_declarations)
    #print("\n")
    return 


def main():
    
    play_game(s = 1)


if __name__ == '__main__':
    main()

    

    



        



