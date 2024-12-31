import random
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import matplotlib.pyplot as plt

# Card and Deck Classes
class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __repr__(self):
        return f"{self.rank} of {self.suit}" if self.suit else self.rank

    def is_trump(self, trump_suit):
        return self.suit == trump_suit or self.rank == "Joker"

class Deck:
    def __init__(self):
        self.suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
        self.ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"]
        self.cards = [Card(suit, rank) for suit in self.suits for rank in self.ranks]
        self.cards.append(Card(None, "Joker"))  # Add Joker

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, num_players, cards_per_player):
        if len(self.cards) < num_players * cards_per_player:
            raise ValueError("Not enough cards in the deck to deal.")
        hands = []
        for _ in range(num_players):
            hands.append([self.cards.pop() for _ in range(cards_per_player)])
        return hands

    def draw_trump(self):
        if not self.cards:
            raise ValueError("No cards left to draw trump.")
        trump_card = self.cards.pop()
        trump_suit = trump_card.suit if trump_card.rank != "Joker" else random.choice(self.suits)
        return trump_card, trump_suit

# Q-Network for Bernard
class QNetwork(nn.Module):
    def __init__(self, state_size, action_size):
        super(QNetwork, self).__init__()
        self.fc1 = nn.Linear(state_size, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, action_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

class DQLAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.q_network = QNetwork(state_size, action_size)
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=self.learning_rate)
        self.criterion = nn.MSELoss()

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if random.random() <= self.epsilon:
            return random.randrange(self.action_size)
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        q_values = self.q_network(state_tensor)
        return torch.argmax(q_values).item()

    def replay(self, batch_size):
        if len(self.memory) < batch_size:
            return
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            next_state_tensor = torch.FloatTensor(next_state).unsqueeze(0)
            target = reward
            if not done:
                target += self.gamma * torch.max(self.q_network(next_state_tensor)).item()
            target_f = self.q_network(state_tensor).detach().clone()
            target_f[0][action] = target
            self.optimizer.zero_grad()
            output = self.q_network(state_tensor)
            loss = self.criterion(output, target_f)
            loss.backward()
            self.optimizer.step()
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

# Player Classes
class Player:
    def __init__(self, name, hand):
        self.name = name
        self.hand = hand

    def play_card(self, trump_suit, playing_suit, best_card_on_table=None):
        playable_cards = [card for card in self.hand if card.suit == playing_suit or card.is_trump(trump_suit)]
        if playable_cards:
            best_card = max(playable_cards, key=lambda x: Game.card_rank_static(x, trump_suit, playing_suit))
            self.hand.remove(best_card)
            return best_card
        return self.hand.pop()

class Bernard(Player):
    def __init__(self, name, hand, state_size, action_size):
        super().__init__(name, hand)
        self.agent = DQLAgent(state_size, action_size)

    def encode_state(self, trump_suit, playing_suit, best_card_on_table):
        state = [0] * 53  # Include all cards (52 + Joker)
        for card in self.hand:
            idx = Game.card_to_index(card)
            if 0 <= idx < len(state):  # Ensure index is valid
                state[idx] = 1
        return state

    def play_card(self, trump_suit, playing_suit, best_card_on_table=None):
        state = self.encode_state(trump_suit, playing_suit, best_card_on_table)
        action = self.agent.act(state)
        playable_cards = [card for card in self.hand if card.suit == playing_suit or card.is_trump(trump_suit)]
        if action < len(playable_cards):
            card_to_play = playable_cards[action]
            self.hand.remove(card_to_play)
            return card_to_play
        return self.hand.pop()

class Game:
    @staticmethod
    def card_to_index(card):
        suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"]

        if card.rank == "Joker":
            return 52
        if card.suit not in suits or card.rank not in ranks:
            raise ValueError(f"Invalid card: {card}")
        return suits.index(card.suit) * 13 + ranks.index(card.rank)

    @staticmethod
    def card_rank_static(card, trump_suit, playing_suit):
        if card.rank == "Joker":
            return 100
        if card.rank == "5" and card.suit == trump_suit:
            return 99
        if card.rank == "Jack" and card.suit == trump_suit:
            return 98
        if card.rank == "Ace" and card.suit == trump_suit:
            return 97
        if card.suit == trump_suit:
            return 11 - int(card.rank) if card.rank.isdigit() else 95 - ["King", "Queen", "Jack", "Ace"].index(card.rank)
        if card.suit:
            return int(card.rank) if card.rank.isdigit() else 80 - ["King", "Queen", "Jack", "Ace"].index(card.rank)
        return 0

# Main Training Loop
state_size = 53  # Include Joker
action_size = 5  # Max cards Bernard can play in a turn
players = [Player(f"Player {i+1}", []) for i in range(4)]
players.append(Bernard("Bernard", [], state_size, action_size))
deck = Deck()

num_games = 100000
batch_size = 32
bernard_hands_won = 0
total_hands_played = 0
win_rates_hands = []

for episode in range(num_games):
    # Reset and shuffle the deck for each game
    deck = Deck()
    deck.shuffle()

    try:
        hands = deck.deal(len(players), 5)
        for i, player in enumerate(players):
            player.hand = hands[i]
        trump_card, trump_suit = deck.draw_trump()
    except ValueError:
        continue

    turns_won = {player.name: 0 for player in players}
    playing_suit = None
    best_card_on_table = None

    for turn in range(5):
        table = []
        for player in players:
            card_played = player.play_card(trump_suit, playing_suit, best_card_on_table)
            table.append((player, card_played))

            if playing_suit is None:
                playing_suit = card_played.suit
            if best_card_on_table is None or Game.card_rank_static(card_played, trump_suit, playing_suit) > Game.card_rank_static(best_card_on_table, trump_suit, playing_suit):
                best_card_on_table = card_played

        turn_winner = max(table, key=lambda x: Game.card_rank_static(x[1], trump_suit, playing_suit))[0]
        turns_won[turn_winner.name] += 1

        # Reward Bernard for winning the turn
        if turn_winner.name == "Bernard":
            bernard_hands_won += 1  # Count Bernard's turn win

        playing_suit = None
        best_card_on_table = None

        total_hands_played += 1  # Increment total hands played

    win_rates_hands.append(bernard_hands_won / total_hands_played)

    # Train Bernard's agent after each game
    players[-1].agent.replay(batch_size)

# Plot Bernard's win rate by hands
plt.plot(win_rates_hands)
plt.xlabel("Games Played")
plt.ylabel("Hand Win Rate")
plt.title("Bernard's Hand Win Rate Over Time")
plt.show()
