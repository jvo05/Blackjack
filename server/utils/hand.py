import random

class Hand:
    def __init__(self, deck=None) -> None:
        if deck is None:
            deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4  # Standard-Deck mit 4 Sets
        self.hand = []
        self.deck = deck
        self.add_random_card()
        self.add_random_card()

    def add_random_card(self):
        # in future this should be limited, so the deck cant be empty. But currently with one player ist cant be empty
        card = random.choice(self.deck)
        self.hand.append(card)
        self.deck.remove(card)

    def calculate_score(self):
        score = sum(self.hand)
        ace_count = self.hand.count(11)
        while score > 21 and ace_count > 0:
            score -= 10
            ace_count -= 1
        return score