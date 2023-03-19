from base_model import BaseModel
from fish import HS_LEN, hs_of
import random


class RandomModel(BaseModel):
    def __init__(self):
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
        super(RandomModel, self).__init__(None, None, None, None)
        
    def startNewGame(self, player_number, team, other_team, starting_cards):
        super(RandomModel, self).__init__(player_number, team, other_team, starting_cards)
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
            self.known_minimum_in_half_suit[askee][hs_of(card)] = max(
                (self.known_minimum_in_half_suit[askee][hs_of(card)], 0)
              )
        else:
            self.known_not_cards[asker].add(card)
            self.known_not_cards[askee].add(card)

    def claim_halfsuit(self, team, halfsuit, successful, card_locations):
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

        for card in card_locations:
            self.num_cards[card_locations[card]] -= 1
    
    def _generate_declaration(self):
        for half_suit_to_find in self.half_suits_in_play:
            cards_in_hs = [card for card in range(54) if hs_of(card) == half_suit_to_find]
            valid_halfsuit = False
            for card in cards_in_hs:
                if card in self.cards:
                    valid_halfsuit = True
                    break
            if valid_halfsuit:
                # print(f"Searching for halfsuit {half_suit_to_find}")
                break

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

        for card in cards_with_unknown_location:
            player = random.choice(self.team)
            declare_dict[player].add(card)
        return (declare_dict, half_suit_to_find)

    def _generate_valid_actions(self):
        # return an array with pairs of proposed card, proposed askee
        # array of tuples (proposed card, proposed askee)
        cards_in_my_suits = set()
        for card in self.cards:
            for hs_card in range(hs_of(card)*6, (hs_of(card)*6)+6):
                cards_in_my_suits.add(hs_card)

        actions = []
        for askee in self.other_team:
            for card in cards_in_my_suits:
                if card not in self.cards:
                    actions.append((askee, card))
        
        return actions
        # raise(NotImplementedError("TODO"))

    def take_action(self, turns, batch_number):
        """
        Returns:
        if action is to ask for a card:
            (-1, (askee, card))

        if action is to declare a halfsuit:
            (1, (evidence, halfsuit index))
            where evidence is a dictionary of evidence. See fish.py for more information

        """
        valid_actions = self._generate_valid_actions()
        actions = valid_actions

        actions.append(('declare'))

        if turns > 250:

            return (1, self._generate_declaration())

        best_predicted_action = random.randint(0, len(actions) - 1)

        if best_predicted_action == len(actions) - 1:
            return (1, self._generate_declaration())
        else:

            return (-1, valid_actions[best_predicted_action])
