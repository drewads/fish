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
import random


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
            self.known_cards[player_number].add(card)

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
        if transfer:
            if asker == self.player_number:
                self.cards.append(card)
            if askee == self.player_number:
                self.cards.remove(card)

        if self.known_minimum_in_half_suit[asker][hs_of(card)] == 0:
            self.known_minimum_in_half_suit[asker][hs_of(card)] = 1

        if transfer:
            self.known_cards[asker].add(card)
            for player in self.team + self.other_team:
                if player != asker:
                    self.known_not_cards[player].add(card)

            if card in self.known_not_cards[asker]:
                self.known_not_cards[asker].remove(card)
            if card in self.known_cards[askee]:
                self.known_cards[askee].remove(card)
            self.known_minimum_in_half_suit[asker][hs_of(card)] += 1
            self.known_minimum_in_half_suit[askee][hs_of(card)] -= 1
        else:
            self.known_not_cards[asker].add(card)
            self.known_not_cards[askee].add(card)

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
        """
        Returns:
        if action is to ask for a card:
            (-1, (askee, card))

        if action is to declare a halfsuit:
            (1, (evidence, halfsuit index))
            where evidence is a dictionary of evidence. See fish.py for more information

        """
        for half_suit_to_find in self.half_suits_in_play:
            cards_in_hs = [card for card in range(54) if hs_of(card) == half_suit_to_find]
            valid_halfsuit = False
            for card in cards_in_hs:
                if card in self.cards:
                    valid_halfsuit = True
                    break
            if valid_halfsuit:
                break

        # If we know of a card in an opponents hand, ask for it
        for card in cards_in_hs:
            for player in self.other_team:
                if card in self.known_cards[player]:
                    return (-1, (player, card))

        # ask for lowest numerical card to lowest opposing player
        # you don't ask for a card you know they don't have
        for card in cards_in_hs:
            for player in self.other_team:
                if card not in self.known_not_cards[player]:
                    return (-1, (player, card))
        
        # declare halfsuit when we know exactly where all cards are and they are in our team's hands
        declare_dict = {k: set() for k in self.team}
        cards_with_unknown_location = cards_in_hs
        for card in cards_in_hs:
            for player in self.team:
                if card in self.known_cards[player]:
                    declare_dict[player].add(card)
                    cards_with_unknown_location.remove(card)

        if len(cards_with_unknown_location) == 0:
            return (1, (declare_dict, half_suit_to_find))

        for card in cards_in_hs:  # Basically just a base case in case the player's team has all the cards in the half-suit, but they don't know where they are
            if card not in self.known_cards[self.player_number]:
                return (-1, (random.choice(self.other_team), card))
