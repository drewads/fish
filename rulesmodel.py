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
from pprint import pprint


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

        self.half_suits_in_play = list(range(int(54 / HS_LEN)))
        self.known_cards = {k: set() for k in team + other_team}
        for card in starting_cards:
            self.known_cards[player_number].add(card)

        self.known_not_cards = {k: set() for k in team + other_team}
        for card in starting_cards:
            for player in team + other_team:
                if player == player_number:
                    continue
                self.known_not_cards[player].add(card)

        self.num_cards = {k: len(starting_cards) for k in self.team + self.other_team}

        self.known_not_cards[self.player_number] = set(range(54)) - self.known_cards[self.player_number]

        self.known_minimum_in_half_suit = {k: [0 for _ in range(int(54 / HS_LEN))] for k in team + other_team}

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

        if self.known_minimum_in_half_suit[asker][hs_of(card)] <= 0:
            self.known_minimum_in_half_suit[asker][hs_of(card)] = 1

        if transfer:
            self.num_cards[asker] += 1
            self.num_cards[askee] -= 1
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

        # print(f'asker: {asker}, askee: {askee}, card: {card}, transfer: {transfer}, self.player_number: {self.player_number}')
        # pprint(self.known_cards)
        # pprint(self.known_not_cards)
        # breakpoint()

    def claim_halfsuit(self, team, halfsuit, successful, evidence):
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
        cards_in_hs = [card for card in range(54) if hs_of(card) == halfsuit]
        for card in cards_in_hs:
            if card in self.cards:
                self.cards.remove(card)
            for player in self.team + self.other_team:
                if card in self.known_not_cards[player]:
                    self.known_not_cards[player].remove(card)
                if card in self.known_cards[player]:
                    self.known_cards[player].remove(card)

        if successful:
            for player in evidence:
                for card in evidence[player]:
                    self.num_cards[player] -= 1
        else:
            breakpoint()

    def take_action(self):
        """
        Returns:
        if action is to ask for a card:
            (-1, (askee, card))

        if action is to declare a halfsuit:
            (1, (evidence, halfsuit index))
            where evidence is a dictionary of evidence. See fish.py for more information

        """
        print("\n\n")
        print("Cards: ", self.cards)
        print("Known cards: ", self.known_cards)
        print("Known not cards: ", self.known_not_cards)
        print("Player: ", self.player_number)
        print("Half suits in play: ", self.half_suits_in_play)
        print("Num cards: ", self.num_cards)
        foundAHalfSuit = False
        for half_suit_to_find in self.half_suits_in_play:
            cards_in_hs = [card for card in range(54) if hs_of(card) == half_suit_to_find]
            valid_halfsuit = False
            for card in cards_in_hs:
                if card in self.cards:
                    valid_halfsuit = True
                    break
            if valid_halfsuit:
                print(f"Searching for halfsuit {half_suit_to_find}")
                foundAHalfSuit = True
                break

        print("Known mins in halfsuit", [self.known_minimum_in_half_suit[player][half_suit_to_find] for player in range(6)])

        # if not foundAHalfSuit:
        #     breakpoint()
        # input("")

        # If we know of a card in an opponents hand, ask for it
        for card in cards_in_hs:
            for player in self.other_team:
                if card in self.known_cards[player]:
                    return (-1, (player, card))

        # ask for lowest numerical card to lowest opposing player
        # you don't ask for a card you know they don't have
        for card in cards_in_hs:
            for player in self.other_team:
                if self.num_cards[player] <= 0:
                    continue
                if card not in self.known_not_cards[player]:
                    return (-1, (player, card))
        
        # declare halfsuit when we know exactly where all cards are and they are in our team's hands
        declare_dict = {k: set() for k in self.team}
        cards_with_unknown_location = list(cards_in_hs)
        for card in cards_in_hs:
            for player in self.team:
                if card in self.known_cards[player]:
                    declare_dict[player].add(card)
                    cards_with_unknown_location.remove(card)

        if len(cards_with_unknown_location) != 0:
            other_team_members = set(self.team) - {self.player_number}
            for o_team_member in other_team_members:
                if self.known_minimum_in_half_suit[o_team_member][half_suit_to_find] <= 0:
                    team_member_with_cards = list(other_team_members - {o_team_member})[0]
                    for card in cards_with_unknown_location:
                        declare_dict[team_member_with_cards].add(card)
                    cards_with_unknown_location = []

        if len(cards_with_unknown_location) != 0:
            cwul_copy = list(cards_with_unknown_location)
            for card in cards_with_unknown_location:
                for player in declare_dict:
                    if self.known_minimum_in_half_suit[player][hs_of(card)] < len(declare_dict[player]):
                        declare_dict[player].add(card)
                        cwul_copy.remove(card)
                        break
            cards_with_unknown_location = cwul_copy

        if len(cards_with_unknown_location) == 0:
            return (1, (declare_dict, half_suit_to_find))
        else:
            breakpoint()

        for card in cards_in_hs:  # Basically just a base case in case the player's team has all the cards in the half-suit, but they don't know where they are
            if card not in self.known_cards[self.player_number]:
                return (-1, (random.choice(self.other_team), card))

        print("Cannot declare halfsuit ", half_suit_to_find, "containing cards", cards_in_hs, "with cards in unknown location", cards_with_unknown_location)
        # raise(Exception("Oops"))

        breakpoint()

