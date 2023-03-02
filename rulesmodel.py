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

from fish import HS_LEN, hs_of


class RulesModel:
    def __init__(self, player_number, team, other_team, starting_cards):
        """
        Parameters
        ----------
        player_number : int
            The player number governed by this model
        team : list(int)
            A list of members of the players team
        other_team : list(int)
            A list of members of the opposing team
        starting_cards : list(int)
            A list of the cards the player starts with
        """
        self.player_number = player_number
        self.team = team
        self.other_team = other_team
        self.cards = starting_cards

        self.half_suits_in_play = list(range(HS_LEN))
        self.known_cards = {k: set() for k in team + other_team}
        for card in starting_cards:
            self.known_cards[player_number].add(starting_cards)

        self.known_not_cards = {k: set() for k in team + other_team}
        for card in starting_cards:
            for player in team + other_team:
                if player == player_number:
                    continue
                self.known_not_cards[player].add(card)

        self.known_minimum_in_half_suit = {k: [0 for _ in range(HS_LEN)] for k in team + other_team}

    def record_action(self, asker, askee, card, transfer):
        """
        Parameters
        ----------
        asker : int
            The player asking for a card
        askee : int
            The player being asked for a card
        card : int
            The card being asked for
        transfer : bool
            Whether the card was given
        """
        if self.known_minimum_in_half_suit[asker][hs_of(card)] == 0:
            self.known_minimum_in_half_suit[asker][hs_of(card)] = 1

        self.known_not_cards[askee].add(card)
        if transfer:
            self.known_cards[asker].add(card)
            if card in self.known_not_cards[asker]:
                self.known_not_cards[asker].remove(card)
            if card in self.known_cards[askee]:
                self.known_cards[askee].remove(card)
            self.known_minimum_in_half_suit[asker][hs_of(card)] += 1
            self.known_minimum_in_half_suit[askee][hs_of(card)] -= 1
        else:
            self.known_not_cards[asker].add(card)

    def claim_halfsuit(self, team, halfsuit, successful):
        """
        Parameters
        ----------
        team : int
            The team claiming the halfsuit
        halfsuit : int
            The halfsuit being claimed
        successful : bool
            Whether the claim is successful
        """
        self.half_suits_in_play.remove(halfsuit)

    def take_action(self):
        pass
