

class PokerTable:
    def __init__(self, table_name):
        self.table_name = table_name
        self.players = []  # List to store connected players
        self.chat_history = []