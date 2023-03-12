class BaseModel:
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
        self.startNewGame(player_number, team, other_team, starting_cards)

    def startNewGame(self, player_number, team, other_team, starting_cards):
        pass

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
        raise(NotImplementedError("No existing implementation for record_action"))

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
        raise(NotImplementedError("No existing implementation for claim_halfsuit"))

    def take_action(self):
        """
        Returns:
        if action is to ask for a card:
            (-1, (askee, card))

        if action is to declare a halfsuit:
            (1, (evidence, halfsuit index))
            where evidence is a dictionary of evidence. See fish.py for more information

        """
        raise(NotImplementedError("No existing implementation for take_action"))
