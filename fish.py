
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
  def __init__(self, seed=None):
    self.known_cards = dict(zip(range(PLAYERS), [set() for _ in range(PLAYERS)])) # maps player to known cards for that player. starts: {player : set()}
    starting_deck = range(DECK_LEN)
    if seed:
      random.seed(seed)
    random.shuffle(starting_deck)
    self.cards = dict(zip(range(PLAYERS), [set(starting_deck[i:i+PLAYER_NUM_CARDS_BEGIN]) for i in range(0, DECK_LEN, PLAYER_NUM_CARDS_BEGIN)])) # maps player to cards (each field is only viewable by that player, but num cards viewable by all). starts: {player : 9 random cards}
    self.half_suits_per_team = {0 : 0, 1 : 0} # maps team to num half suits taken. starts: {team : 0}
    self.taken_half_suits = set() # which half suits have been taken. start: set()
    self.known_half_suits = dict(zip(range(PLAYERS), [{'half_suits' : set(), 'independent_of' : set()} for _ in range(PLAYERS)]))    # which half suits a player is known to have - though we should keep more state like when we knew this so it doesnt get messed up by other cards - can keep list of cards this is independent of. start: {player : {'half_suits' : set(), 'independent_of' : set()}}
      # known_half_suits should take the structure:
      # {
      #   'player_name' : {
      #     'half_suits' : set()
      #     'independent_of' : set()
      #   }
      # }
      # where 'independent of' are the cards where our knowledge of that player's half suits does not change if the player loses one of those cards
    self.known_not_cards = dict(zip(range(PLAYERS), [set() for _ in range(PLAYERS)]))     # maps player to cards that player is known to not have (they asked for it and didn't get it). start: {player : set()}

  def perform_action(self, player, ask_player, card):
    ### returns True if action was valid and successful, False if action was valid and unsuccessful, and None if action was invalid

    # action is invalid if 'player' does not have 'card' or 'player' does not have a card in the half suit of 'card'
    if card in self.cards[player] or hs_of(card) not in set([hs_of(c) for c in self.cards[player]]):
      return None

    self.known_half_suits[player]['half_suits'].add(hs_of(card))

    if card not in self.cards[ask_player]:
      self.known_not_cards[player].add(card)
      self.known_not_cards[ask_player].add(card)
      return False
    
    ## Below: ask_player did have card

    self.cards[ask_player].remove(card)
    self.cards[player].add(card)
    self.known_cards[player].add(card)

    if card not in self.known_half_suits[ask_player]['independent_of']:
      self.known_half_suits[ask_player]['half_suits'].remove(hs_of(card))

    self.known_half_suits[player]['independent_of'].add(card)
    return True

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

    halfsuit = None

    # check evidence is valid
    for p, cards in evidence.items():
      if p // TEAM_LEN != player // TEAM_LEN:
        return None
      num_cards = 0
      for card in cards:
        num_cards += 1
        if halfsuit == None:
          halfsuit = hs_of(card)
        if hs_of(card) != halfsuit:
          return None
      if num_cards != HS_LEN:
        return None

    correct = True
    # check evidence is correct
    for p, cards in evidence.items():
      for card in cards:
        if card not in self.cards[p]:
          correct = False

    # remove halfsuit from players' hands and update other state
    for p, cards in evidence.items():
      for card in cards:
        self.cards[p].remove(card)
        self.known_cards[p].discard(card)
        for p in range(PLAYERS):
          self.known_not_cards[p].discard(card)
      self.known_halfsuits[p].discard(halfsuit)

    # give halfsuit to correct team
    self.half_suits_per_team[player // TEAM_LEN] += 1
    self.taken_half_suits.add(halfsuit)

    # TODO: if game is over, award game

    return correct