import random

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __repr__(self):
        return f"{self.rank} of {self.suit}" if self.suit else self.rank

class Deck:
    def __init__(self):
        self.suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
        self.ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"]
        self.cards = [Card(suit, rank) for suit in self.suits for rank in self.ranks]
        self.cards.append(Card(None, "Joker"))  # Add a single Joker
        self.discarded = []  # Tracks dealt cards

    def shuffle(self):
        """Shuffles the deck."""
        self.cards += self.discarded
        self.discarded = []
        random.shuffle(self.cards)

    def deal(self, num_cards):
        """Deals a specific number of cards, removing them from the deck."""
        if num_cards > len(self.cards):
            raise ValueError("Not enough cards in the deck to deal.")
        dealt_cards = [self.cards.pop() for _ in range(num_cards)]
        self.discarded.extend(dealt_cards)
        return dealt_cards

    def reset(self):
        """Resets the deck to its original state."""
        self.__init__()

class Hand:
    def __init__(self, cards=None):
        self.cards = cards if cards else []

    def add_cards(self, new_cards):
        """Adds cards to the hand."""
        self.cards.extend(new_cards)

    def remove_card(self, card):
        """Removes a specific card from the hand."""
        self.cards.remove(card)

    def __repr__(self):
        return f"Hand({self.cards})"

# Example Usage
deck = Deck()
deck.shuffle()

# Create hands
hand1 = Hand(deck.deal(5))
hand2 = Hand(deck.deal(5))
hand3 = Hand(deck.deal(5))
hand4 = Hand(deck.deal(5))
hand5 = Hand(deck.deal(5))
hand6 = Hand(deck.deal(5))

print("Hand 1:", hand1)
print("Hand 2:", hand2)
print("Hand 3:", hand3)
print("Hand 4:", hand4)
print("Hand 5:", hand5)
print("Hand 6:", hand6)
print("Remaining cards in deck:", len(deck.cards))