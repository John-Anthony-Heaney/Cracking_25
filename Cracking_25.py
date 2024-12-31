import random

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
        self.cards.append(Card(None, "Joker"))  # Add a single Joker

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, num_players, cards_per_player):
        hands = []
        for _ in range(num_players):
            hands.append([self.cards.pop() for _ in range(cards_per_player)])
        return hands

    def draw_trump(self):
        """Turn over the top card to determine the trump suit."""
        trump_card = self.cards.pop()
        if trump_card.rank == "Joker":
            self.trump_suit = random.choice(self.suits)
        else:
            self.trump_suit = trump_card.suit
        return trump_card

class Player:
    def __init__(self, name, hand):
        self.name = name
        self.hand = hand

    def play_card(self, card):
        self.hand.remove(card)
        return card

    def has_trump(self, trump_suit):
        return any(card.is_trump(trump_suit) for card in self.hand)

    def worst_card(self, trump_suit, playing_suit):
        """Return the worst playable card."""
        playable_cards = [card for card in self.hand if card.suit == playing_suit or card.is_trump(trump_suit)]
        return min(playable_cards, key=lambda x: Game.card_rank_static(x, trump_suit, playing_suit)) if playable_cards else None

    def best_card(self, trump_suit, playing_suit):
        """Return the best playable card."""
        playable_cards = [card for card in self.hand if card.suit == playing_suit or card.is_trump(trump_suit)]
        return max(playable_cards, key=lambda x: Game.card_rank_static(x, trump_suit, playing_suit)) if playable_cards else None

    def __repr__(self):
        return f"{self.name}: {self.hand}"

class Game:
    def __init__(self, players):
        self.players = [Player(name, []) for name in players]
        self.deck = Deck()
        self.trump_suit = None
        self.playing_suit = None

    def start_round(self):
        """Starts a new round by shuffling, dealing, and setting the trump suit."""
        self.deck.shuffle()
        hands = self.deck.deal(len(self.players), 5)
        for i, player in enumerate(self.players):
            player.hand = hands[i]

        trump_card = self.deck.draw_trump()
        self.trump_suit = self.deck.trump_suit

        # Handle Ace of Trump Rule for Trump Card
        if trump_card.rank == "Ace":
            dealer = self.players[-1]
            worst_card = min(dealer.hand, key=lambda x: self.card_rank_static(x, self.trump_suit, None))
            dealer.hand.remove(worst_card)
            dealer.hand.append(trump_card)
            print(f"Dealer {dealer.name} swaps {worst_card} for Ace of trump {trump_card}.")

        print(f"Trump suit is {self.trump_suit} (from {trump_card}).")
        for player in self.players:
            print(f"{player.name}'s hand: {player.hand}")

    def play_turn(self, starting_player):
        """Simulates a turn starting with a specific player."""
        current_player = starting_player
        table = []

        # First player places a card
        first_card = current_player.play_card(current_player.hand[0])  # Simplified for now
        self.playing_suit = first_card.suit
        table.append((current_player, first_card))

        print(f"{current_player.name} plays {first_card}.")

        # Subsequent players play cards
        for _ in range(len(self.players) - 1):
            current_player = self.next_player(current_player)

            # Special Rule: Ace of Trump allows player to exchange
            if any(card.rank == "Ace" and card.suit == self.trump_suit for card in current_player.hand):
                ace_trump_card = next(card for card in current_player.hand if card.rank == "Ace" and card.suit == self.trump_suit)
                worst_card = min(current_player.hand, key=lambda x: self.card_rank_static(x, self.trump_suit, self.playing_suit))
                current_player.hand.remove(ace_trump_card)
                current_player.hand.append(self.deck.draw_trump())
                print(f"{current_player.name} exchanges Ace of Trump for the trump card.")
                continue

            valid_cards = [card for card in current_player.hand if card.suit == self.playing_suit or card.is_trump(self.trump_suit)]

            if valid_cards:
                # Player logic based on rules
                if self.playing_suit == self.trump_suit:
                    if first_card.rank in ["Joker", "5", "Jack"] and current_player.best_card(self.trump_suit, self.playing_suit).rank not in ["Joker", "5", "Jack"]:
                        card_to_play = current_player.best_card(self.trump_suit, self.playing_suit)
                    else:
                        card_to_play = current_player.worst_card(self.trump_suit, self.playing_suit)
                else:
                    if not any(card.suit == self.playing_suit for card in current_player.hand) and not any(card.is_trump(self.trump_suit) for card in current_player.hand):
                        card_to_play = random.choice(current_player.hand)
                    else:
                        card_to_play = current_player.best_card(self.trump_suit, self.playing_suit) if current_player.best_card(self.trump_suit, self.playing_suit) else current_player.worst_card(self.trump_suit, self.playing_suit)
            else:
                card_to_play = current_player.hand[0]

            table.append((current_player, current_player.play_card(card_to_play)))
            print(f"{current_player.name} plays {card_to_play}.")

        # Determine winner
        winner = self.determine_winner(table)
        print(f"{winner.name} wins the turn.")
        return winner

    def next_player(self, current_player):
        """Returns the next player in the rotation."""
        index = self.players.index(current_player)
        return self.players[(index + 1) % len(self.players)]

    def determine_winner(self, table):
        """Determines the winner of a turn based on the table."""
        trump_cards = [entry for entry in table if entry[1].is_trump(self.trump_suit)]
        if trump_cards:
            return max(trump_cards, key=lambda x: self.card_rank_static(x[1], self.trump_suit, self.playing_suit))[0]
        playing_suit_cards = [entry for entry in table if entry[1].suit == self.playing_suit]
        return max(playing_suit_cards, key=lambda x: self.card_rank_static(x[1], self.trump_suit, self.playing_suit))[0]

    @staticmethod
    def card_rank_static(card, trump_suit, playing_suit):
        """Static method to calculate card rank for sorting."""
        if card.rank == "Joker":
            return 100
        if card.rank == "5" and card.suit == trump_suit:
            return 99
        if card.rank == "Jack" and card.suit == trump_suit:
            return 98
        if card.rank == "Ace" and card.suit == "Hearts":
            return 97
        if card.rank == "Ace" and card.suit == trump_suit:
            return 96

        # Trump cards
        if card.suit == trump_suit:
            if trump_suit in ["Clubs", "Spades"]:
                return 11 - int(card.rank) if card.rank.isdigit() else 95 - ["King", "Queen"].index(card.rank)
            if trump_suit in ["Hearts", "Diamonds"]:
                return int(card.rank) if card.rank.isdigit() else 95 - ["King", "Queen"].index(card.rank)

        # Non-trump cards
        if card.suit:
            if card.suit in ["Clubs", "Spades"]:
                return 11 - int(card.rank) if card.rank.isdigit() else 80 - ["King", "Queen", "Jack"].index(card.rank)
            if card.suit in ["Hearts", "Diamonds"]:
                return int(card.rank) if card.rank.isdigit() else 80 - ["King", "Queen", "Jack"].index(card.rank)

        return 0  # Catch-all

# Example Game Setup
players = ["Alice", "Bob", "Charlie", "Diana"]
game = Game(players)
game.start_round()

starting_player = game.players[0]
for _ in range(5):  # Simulate 5 turns
    starting_player = game.play_turn(starting_player)
