

class PokerTable:
    def __init__(self, table_name, password=''):
        self.table_name = table_name
        self.players = []  # List to store connected players
        self.password = password
        self.chat_history = []