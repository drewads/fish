from fish import Fish

def correct_init():
  game = Fish(5)
  cards = set()
  for player in range(6):
    if len(game.cards[player]) != 9:
      return "Player does not have 9 cards"
    for card in game.cards[player]:
      if card in cards:
        return "Card seen twice"
      cards.add(card)
  if len(cards) != 54:
    return "Not 54 cards"
  for card in range(54):
    if card not in cards:
      return "Card not in cards"
  return "Passed"

def invalid_action():
  game = Fish(5)
  player = 0
  player_cards = [card for card in game.cards[player]]
  card = player_cards[0]
  if game.perform_action(player, 3, card) is not None:
    return "Did not return None after invalid ask for had card"
  if game.perform_action(player, 3, 0) is not None:
    return "Did not return None after invalid ask for not had halfsuit"
  if game.perform_action(player, 3, 1) is not None:
    return "Did not return None after invalid ask for not had halfsuit"
  return "Passed"

def valid_action_with_result():
  game = Fish(5)
  player = 0
  player_ask = 3
  card = 38
  if game.perform_action(player, player_ask, card) is not True:
    return "Action incorrectly failed"
  if len(game.cards[player]) == 10 and card in game.cards[player] \
     and len(game.cards[player_ask]) == 8 and card not in game.cards[player_ask]:
    return "Passed"
  return "Validation incorrect"

def valid_action_with_no_result():
  game = Fish(5)
  player = 0
  player_ask = 3
  card = 39
  if game.perform_action(player, player_ask, card) is not False:
    return "Incorrectly does not reject action"
  if len(game.cards[player]) == 9 and card not in game.cards[player] \
     and len(game.cards[player_ask]) == 9 and card not in game.cards[player_ask]:
    return "Passed"
  return "Validation incorrect"

def correctly_declare_halfsuit():
  game = Fish(5)
  # 0 asks 4 for 48
  game.perform_action(0, 4, 48)
  # 0 asks 5 for 51
  game.perform_action(0, 5, 51)
  # declare with
  evidence = {
    0 : set([48, 51, 52, 53, 49]),
    1 : set([50])
  }
  if game.declare_halfsuit(0, evidence) is not True:
    return "Declare halfsuit did not go through"
  if len(game.cards[0]) == 6 and len(game.cards[1]) == 8 \
     and game.half_suits_per_team[0] == 1 and 8 in game.taken_half_suits:
    return "Passed"
  return "did not pass"
  
# declare invalid halfsuit
def declare_invalid_halfsuit():
  game = Fish(5)
  evidence = {
    0 : set([22, 51, 52, 53, 49]),
    1 : set([50])
  }
  if game.declare_halfsuit(0, evidence) is not None:
    return "Declare halfsuit check incorrect 1"
  evidence = {
    0 : set([48, 51, 52, 53, 49]),
    1 : set([50, 54])
  }
  if game.declare_halfsuit(0, evidence) is not None:
    return "Declare halfsuit check incorrect 2"
  evidence = {
    0 : set([48, 51, 52, 53, 49]),
    1 : set([50, 51])
  }
  if game.declare_halfsuit(0, evidence) is not None:
    return "Declare halfsuit check incorrect 3"
  evidence = {
    0 : set([9, 11]),
    3 : set([6, 8]),
    4 : set([7, 10])
  }
  if game.declare_halfsuit(0, evidence) is not None:
    return "Declare halfsuit check incorrect 4"
  evidence = {
    0 : set([48, 51, 52, 53, 49]),
    1 : set([51])
  }
  if game.declare_halfsuit(0, evidence) is not None:
    return "Declare halfsuit check incorrect 5"
  return "Passed"

# incorrectly declare 5 halfsuits to end game and check that game has ended
def incorrectly_declare_to_end():
  game = Fish(5)
  # halfsuit 8
  evidence = {
    0 : set([48, 51, 52, 53, 49]),
    1 : set([50])
  }
  if game.declare_halfsuit(0, evidence) is not False:
    return "Declare halfsuit check incorrect 1"
  # halfsuit 1
  evidence = {
    0 : set([9, 11]),
    1 : set([6, 8]),
    2 : set([7, 10])
  }
  if game.declare_halfsuit(0, evidence) is not False:
    return "Declare halfsuit check incorrect 2"
  # halfsuit 6
  evidence = {
    3 : set([36, 38]),
    4 : set([37, 40]),
    5 : set([39, 41])
  }
  if game.declare_halfsuit(3, evidence) is not False:
    return "Declare halfsuit check incorrect 3"
  # halfsuit 7
  evidence = {
    4 : set([43]),
    3 : set([42, 44, 45, 46, 47])
  }
  if game.declare_halfsuit(4, evidence) is not False:
    return "Declare halfsuit check incorrect 4"
  # halfsuit 0
  evidence = {
    5 : set([1]),
    3 : set([0, 5, 2, 3, 4])
  }
  if game.declare_halfsuit(5, evidence) is not False:
    return "Declare halfsuit check incorrect 5"
  # halfsuit 2
  evidence = {
    5 : set([12, 13, 14, 15, 16, 17])
  }
  if game.declare_halfsuit(5, evidence) is not False:
    return "Declare halfsuit check incorrect 6"
  # halfsuit 5
  evidence = {
    5 : set([30, 31, 32, 33, 34, 35])
  }
  if game.declare_halfsuit(5, evidence) is not False:
    return "Declare halfsuit check incorrect 7"
  if game.half_suits_per_team[0] == 5 and game.half_suits_per_team[1] == 2 and \
     len(game.taken_half_suits) == 7 and game.team_won() == 0:
    return "Passed"
  return "State incorrect"


if __name__ == "__main__":
  # all use 5 as seed for Fish()
  print("Correct init:", correct_init())
  print("Invalid action:", invalid_action())
  print("Valid action with result:", valid_action_with_result())
  print("Valid action with no result:", valid_action_with_no_result())
  print("Correctly declare halfsuit:", correctly_declare_halfsuit())
  print("Declare invalid halfsuits:", declare_invalid_halfsuit())
  print("Incorrectly declare to end:", incorrectly_declare_to_end())
