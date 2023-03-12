
# deck of cards is represented as the numbers 0 - 53, with each number able to
# be mapped to a specific card. The half suits are each group of 6 adjacent
# cards. So, to tell if two cards A and B are in a half suit together, do:
# A//HS_LEN == B//HS_LEN.
# the half suits are assigned numbers 0-5 according to the result of card//HS_LEN

# The players are likewise split into two teams, with players 0, 1, 2 being on
# team 0 and 3, 4, 5 being on team 1

import random

PLAYERS = 6 # number of players
TEAM_LEN = 3 # number of players per team
HS_LEN = 6 # number of cards in each half suit
DECK_LEN = 54 # number of cards in the deck
PLAYER_NUM_CARDS_BEGIN = DECK_LEN // PLAYERS # number of cards each player begins with

def hs_of(card):
  return card // HS_LEN

class Fish:
  def __init__(self, seed=None, randomize=True):
    starting_deck = [card for card in range(DECK_LEN)]
    if seed:
      random.seed(seed)
    if randomize:
      random.shuffle(starting_deck)
    self.cards = dict(zip(range(PLAYERS), [set(starting_deck[i:i+PLAYER_NUM_CARDS_BEGIN]) for i in range(0, DECK_LEN, PLAYER_NUM_CARDS_BEGIN)])) # maps player to cards (each field is only viewable by that player, but num cards viewable by all). starts: {player : 9 random cards}
    self.half_suits_per_team = {0 : 0, 1 : 0} # maps team to num half suits taken. starts: {team : 0}. Game ends when one of the teams reaches 5
    self.taken_half_suits = set() # which half suits have been taken. start: set()

  def perform_action(self, player, ask_player, card):
    ### returns True if action was valid and successful, False if action was valid and unsuccessful, and None if action was invalid

    # action is invalid if 'player' does not have 'card' or 'player' does not have a card in the half suit of 'card'
    if card in self.cards[player] or hs_of(card) not in set([hs_of(c) for c in self.cards[player]]):
      return None

    if card not in self.cards[ask_player]:
      return False
    
    ## Below: ask_player did have card

    self.cards[ask_player].remove(card)
    self.cards[player].add(card)

    return True
  
  ## This function should be considered private
  def find_card(self, card):
    for p, cards in self.cards.items():
      if card in cards:
        return p
    raise "Card not found in cards"
  
  def team_won(self):
    threshold = (DECK_LEN // HS_LEN) / 2
    if self.half_suits_per_team[0] > threshold:
      return 0
    if self.half_suits_per_team[1] > threshold:
      return 1
    return None

  def declare_halfsuit(self, player, evidence):
    ### Returns True if action was valid and successful, False if action was valid and unsuccessful, and None if action was invalid
    # evidence should be of the form:
    # {
    #   'player_name_1' : set(
    #     ['card1', 'card2', ...]
    #   ),
    #   'player_name_2' : set(
    #     ['card3', ...]
    #   ),
    #   ...
    # }

    halfsuit = None # halfsuit being declared

    # check evidence is valid
    seen_cards = set()
    for p, cards in evidence.items():
      if p // TEAM_LEN != player // TEAM_LEN:
        return None
      for card in cards:
        if card in seen_cards:
          return None
        seen_cards.add(card)
        if halfsuit == None:
          halfsuit = hs_of(card)
        if hs_of(card) != halfsuit:
          return None
    if len(seen_cards) != HS_LEN:
      return None
    if halfsuit in self.taken_half_suits:
      return None
    # end check evidence is valid
    
    # check evidence is correct and find all cards
    correct = True
    card_locations = {}
    for p, cards in evidence.items():
      for card in cards:
        if card not in self.cards[p]:
          correct = False
          card_locations[card] = self.find_card(card)
        else:
          card_locations[card] = p
    # end check evidence is correct and find all cards

    # remove halfsuit from players' hands
    for card, p in card_locations.items():
      self.cards[p].remove(card)

    # give halfsuit to correct team
    team_getting_halfsuit = (player // TEAM_LEN + (not correct)) % 2
    self.half_suits_per_team[team_getting_halfsuit] += 1
    self.taken_half_suits.add(halfsuit)

    return (correct, card_locations)
