import torch
from base_model import BaseModel
from fish import HS_LEN, hs_of
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm


class QNetwork(torch.nn.Module):
    def __init__(self, inputSize):
        super(QNetwork, self).__init__()
        self.network = torch.nn.Sequential(
            torch.nn.Linear(inputSize, 1024),
            torch.nn.PReLU(),
            torch.nn.Linear(1024, 1024),
            torch.nn.PReLU(),
            torch.nn.Linear(1024, 512),
            torch.nn.PReLU(),
            torch.nn.Linear(512, 512),
            torch.nn.PReLU(),
            torch.nn.Linear(512, 1)
            )

    def forward(self, x):
        out = self.network(x.float())
        return out


class DeclarationNetwork(torch.nn.Module):
    def __init__(self, inputSize):
        super(DeclarationNetwork, self).__init__()
        self.network = torch.nn.Sequential(
            torch.nn.Linear(inputSize, 1024),
            torch.nn.PReLU(),
            torch.nn.Linear(1024, 1024),
            torch.nn.PReLU(),
            torch.nn.Linear(1024, 1024),
            torch.nn.PReLU(),
            torch.nn.Linear(1024, 1024),
            torch.nn.PReLU(),
            torch.nn.Linear(1024, 9 + (6 * 6))
            )

    def forward(self, x):
        out = self.network(x.float())
        return out


class CustomDataset(Dataset):
    def __init__(self, inputs, targets):
        self.inputs = inputs
        self.targets = targets

    def __len__(self):
        return len(self.inputs)

    def __getitem__(self, idx):
        return self.inputs[idx], self.targets[idx]


class DeepQModel(BaseModel):
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
        self.action_replay = []

        super(DeepQModel, self).__init__(None, None, None, None)

        self.model = QNetwork(len(self._generate_state((0, 0), False)))
        self.declaration_model = DeclarationNetwork(len(self._generate_state((0, 0), False)))
        self.discount_factor = .96  # I just randomly chose this lol

    def startNewGame(self, player_number, team, other_team, starting_cards):
        super(DeepQModel, self).startNewGame(player_number, team, other_team, starting_cards)

        # We should use a better implementation of state for our deep Q model, I just don't know how yet
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

        self.action_replay.append(('sog'))

    def _generate_state(self, proposed_action, declare):
        proposed_askee, proposed_card = proposed_action
        proposed_card_tensor = torch.nn.functional.one_hot(torch.tensor(proposed_card), num_classes=54)
        proposed_askee_tensor = torch.nn.functional.one_hot(torch.tensor(proposed_askee), num_classes=6)

        if declare:
            proposed_card_tensor = torch.zeros(len(proposed_card_tensor))
            proposed_askee_tensor = torch.zeros(len(proposed_askee_tensor))

        known_cards_tensor = torch.zeros(54 * 6)
        for player, cards in sorted(self.known_cards.items()):
            for card in cards:
                known_cards_tensor[(player * 54) + card] = 1
        known_not_cards_tensor = torch.zeros(54 * 6)
        for player, cards in sorted(self.known_not_cards.items()):
            for card in cards:
                known_not_cards_tensor[(player * 54) + card] = 1
        num_cards_tensor = torch.tensor([i[1] for i in sorted(self.num_cards.items())])
        known_minimum_in_half_suit_tensor = torch.zeros(9 * 6)
        for player, counts in sorted(self.known_minimum_in_half_suit.items()):
            for index, count in enumerate(counts):
                known_minimum_in_half_suit_tensor[(player * 9) + index] = count
        declare_indicator = torch.tensor([1 if declare else 0])
        return torch.cat([declare_indicator, proposed_card_tensor, proposed_askee_tensor, known_cards_tensor, known_not_cards_tensor, num_cards_tensor, known_minimum_in_half_suit_tensor])

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
        self.action_replay.append(('halfsuit_claim', team, halfsuit, successful, card_locations, self._generate_state((0, 0), True)))

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

    def _generate_declare_target(self, halfsuit, card_locations):
        halfsuit_tensor = torch.nn.functional.one_hot(torch.tensor(halfsuit), num_classes=9)
        location_tensors = []
        for card, location in sorted(card_locations.items()):
            location_tensors.append(torch.nn.functional.one_hot(torch.tensor(location), num_classes=6))
        location_stacked_tensor = torch.cat(location_tensors)
        return torch.cat([halfsuit_tensor, location_stacked_tensor])

    def _generate_declaration(self):
        breakpoint()
        state = self._generate_state((0, 0), True)
        declaration_prediction = self.declaration_model(state)
        halfsuit_prediction = torch.argmax(declaration_prediction[:9])

        declare_dict = {k: set() for k in self.team}

        current_card = int(halfsuit_prediction) * 6
        for index in range(6):
            card_location_prediction = declaration_prediction[9 + (index * 6):9 + ((index + 1) * 6)]
            card_location_prediction = card_location_prediction[self.team]
            card_location_prediction = torch.argmax(card_location_prediction)
            declare_dict[self.team[card_location_prediction]].add(current_card)
            current_card += 1
        
        return (declare_dict, halfsuit_prediction)

    def train_for_iteration(self):
        inputs = []
        targets = []

        declare_inputs = []
        declare_targets = []

        current_score = 0
        for action in reversed(self.action_replay):
            if action[0] == 'halfsuit_claim':
                _, team, halfsuit, successful, card_locations, state = action
                multiplier = -1
                if self.player_number in team:
                    multiplier = 1
                    declare_inputs.append(state)
                    declare_targets.append(self._generate_declare_target(halfsuit, card_locations))
                if successful:
                    current_score += multiplier
                else:
                    current_score -= multiplier
            elif action[0] == 'sog':
                current_score = 0
            else:
                _, action_type, state = action
                inputs.append(state)
                targets.append(current_score)
                current_score *= self.discount_factor

        train_declare_dataset = CustomDataset(declare_inputs, declare_targets)
        train_declare_dataloader = DataLoader(train_declare_dataset, batch_size=32, shuffle=True)
        declare_loss_fn = torch.nn.CrossEntropyLoss()
        declare_optimizer = torch.optim.Adam(self.declaration_model.parameters(), lr=1e-3)
        self.declaration_model.train()

        pbar = tqdm(train_declare_dataloader, desc="Training Declare", leave=False, position=1)
        running_average = 0
        seen_so_far = 0
        declare_loss_average = 0
        for index, (inp, target) in enumerate(pbar):
            prediction = torch.squeeze(self.model(inp))

            loss = declare_loss_fn(prediction, target)

            declare_optimizer.zero_grad()
            loss.backward()

            declare_optimizer.step()

            seen_so_far += 1
            running_average *= (seen_so_far - 1) / seen_so_far
            running_average += loss.item() / seen_so_far

            declare_loss_average += loss.item() / len(train_dataloader)

            pbar.set_postfix({'loss': running_average})

        train_dataset = CustomDataset(inputs, targets)
        train_dataloader = DataLoader(train_dataset, batch_size=32, shuffle=True)

        loss_fn = torch.nn.MSELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=1e-3)

        self.model.train()
        pbar = tqdm(train_dataloader, desc="Training action network", leave=False, position=1)
        running_average = 0
        seen_so_far = 0
        loss_average = 0
        for index, (inp, target) in enumerate(pbar):
            prediction = torch.squeeze(self.model(inp))

            loss = loss_fn(prediction, target)

            optimizer.zero_grad()
            loss.backward()

            optimizer.step()

            seen_so_far += 1
            running_average *= (seen_so_far - 1) / seen_so_far
            running_average += loss.item() / seen_so_far

            loss_average += loss.item() / len(train_dataloader)

            pbar.set_postfix({'loss': running_average})

        return (loss_average, declare_loss_average)

    def _generate_valid_actions(self):
        # return an array with pairs of proposed card, proposed askee
        #array of tuples (proposed card, proposed askee)
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
        #raise(NotImplementedError("TODO"))

    def take_action(self, turns):
        """
        Returns:
        if action is to ask for a card:
            (-1, (askee, card))

        if action is to declare a halfsuit:
            (1, (evidence, halfsuit index))
            where evidence is a dictionary of evidence. See fish.py for more information

        """
        valid_actions = self._generate_valid_actions()
        actions = [self._generate_state(action, False) for action in valid_actions]

        declare_action = self._generate_state((0, 0), True)
        actions.append(declare_action)

        action_tensors = torch.stack(actions)

        self.model.eval()
        predicted_value = self.model(action_tensors)
        best_predicted_action = torch.argmax(predicted_value)

        if best_predicted_action == len(actions) - 1:
            self.action_replay.append(('action', 'declare', declare_action))

            return (1, self._generate_declaration())
        else:
            self.action_replay.append(('action', 'ask', valid_actions[best_predicted_action]))

            return (-1, valid_actions[best_predicted_action])
