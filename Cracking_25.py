def create_deck():
    suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
    ranks = ["A", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    
    # Generate the full deck of standard cards
    deck = [(rank, suit) for suit in suits for rank in ranks]
    
    # Add a single Joker
    joker = ("Joker", "Special")
    deck.append(joker)
    
    # Ensure all cards are unique
    assert len(deck) == len(set(deck)), "Duplicate cards found in the deck!"
    
    return deck

# Test the deck creation
deck = create_deck()

# Check if Joker is included
if ("Joker", "Special") in deck:
    print("Joker successfully added to the deck!")
else:
    print("Joker is missing from the deck.")

# Check for duplicates
assert len(deck) == len(set(deck)), "Duplicates found in the deck!"
