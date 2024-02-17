from User import User
import pickle


class AccountHandler:
    """Manages actions with accounts, tracks logged-in users"""
    def __init__(self, file_db):
        # self.logged_in_users = []
        self.file_db = file_db
        self.user_db = self.load_users()
        self.connected_users = {}

    def register_user(self, username, password, client_socket):
        """Registers a new account and adds it to the tracked users"""
        if username not in self.user_db:
            self.user_db[username] = User(username, password)
            self.connected_users[username] = client_socket
            self.save_users()
            return True
        return False

    def login_user(self, username, password, client_socket):
        """Check if username and password match with registered account and tracks the new user"""
        if username in self.user_db and password == self.user_db[username].password:
            self.connected_users[username] = client_socket
            return True
        return False

    def load_users(self):
        """Reads users from the file given in the __init__() and returns them"""
        try:
            with open(self.file_db, "rb") as file:
                return pickle.load(file)
        except FileNotFoundError:
            return {}

    def save_users(self):
        """Saves state of users in memory to the save file"""
        with open(self.file_db, "wb") as file:
            pickle.dump(self.user_db, file)

    def disconnect_user(self, username):
        if username in self.connected_users:
            self.connected_users.pop(username)
