import pygame


class CardDeck:
    """Loads images of cards and creates a playable card deck for other classes"""
    def __init__(self):
        self.cards_img = {}

        suits = ['C', 'D', 'S', 'H']
        for suit in suits:
            for num in range(2, 14):
                card_name = suit + str(num)
                file_name = str(num) + suit
                self.cards_img[card_name] = pygame.image.load(f"../img/cards/{file_name}.png")
