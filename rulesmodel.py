### model should be a class with the following interface:
# function __init__(player number, team (array of player numbers), other team (array),
#          starting cards, )
# function record_action(asker (player), askee (player), card (number), transfer (bool))
# function take_action() # tells this model to take an action

# if no knowledge, randomly ask
# numerical order of halfsuit
# if we know of card in that halfsuit, ask for it
# ask for lowest numerical card to random person
# you don't ask for a card you know they don't have
# declare halfsuit when we know exactly where all cards are and they are in our team's hands