
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
    self.known_cards = dict(zip(range(PLAYERS), [set() for _ in range(PLAYERS)])) # maps player to known cards for that player. starts: {player : set()}
    starting_deck = [card for card in range(DECK_LEN)]
    if seed:
      random.seed(seed)
    if randomize:
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
    self.known_not_cards[ask_player].add(card)

    if card not in self.known_half_suits[ask_player]['independent_of']:
      new_dependent = None
      for ind_card in self.known_half_suits[ask_player]['independent_of']:
        if hs_of(card) == hs_of(ind_card):
          new_dependent = ind_card
          break
      if new_dependent is not None:
        # if we lose a card that is not in independent_of but we still have this
        # halfsuit represented in independent_of, remove one card from halfsuit
        # in independent_of and keep the halfsuit in known_halfsuits
        self.known_half_suits[ask_player]['independent_of'].remove(new_dependent)
      elif hs_of(card) in self.known_half_suits[ask_player]['half_suits']:
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
    
    def find_card(card):
      for p, cards in self.cards.items():
        if card in cards:
          return p
      raise "Card not found in cards"

    correct = True
    card_locations = {}
    # check evidence is correct
    for p, cards in evidence.items():
      for card in cards:
        if card not in self.cards[p]:
          correct = False
          card_locations[card] = find_card(card)
        else:
          card_locations[card] = p

    # remove halfsuit from players' hands and update other state
    for card, p in card_locations.items():
      self.cards[p].remove(card)
      self.known_cards[p].discard(card)
      for kn_p in range(PLAYERS):
        self.known_not_cards[kn_p].discard(card)
      self.known_half_suits[p]['half_suits'].discard(halfsuit)

    # give halfsuit to correct team
    self.half_suits_per_team[(player // TEAM_LEN + (not correct)) % 2] += 1
    self.taken_half_suits.add(halfsuit)

    return correct
