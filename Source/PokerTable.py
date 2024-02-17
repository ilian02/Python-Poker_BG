import random

from Source.CardDeck import CardDeck


class PokerTable:
    """Poker table struct"""
    def __init__(self, table_name):
        self.table_name = table_name + "'s table"
        self.players = []  # List to store connected players
        self.players_money = {}
        self.chat_history = []
        self.deck = list(CardDeck.cards_img.keys())
        self.table_cards = []
        self.player_cards = {}
        self.pot = 0
        self.starting = 25
        self.cards_shown = 0

    def draw_cards(self):

        self.deck = list(CardDeck.cards_img.keys())
        self.table_cards = random.sample(self.deck, 5)
        self.deck = [card for card in self.deck if card not in self.table_cards]

        for player in self.players:
            self.player_cards[player] = random.sample(self.deck, 2)
            self.deck = [card for card in self.deck if card not in self.player_cards[player]]
