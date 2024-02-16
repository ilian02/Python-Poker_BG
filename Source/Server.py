import socket
import threading
import pickle  # For serializing Python objects for network communication
from PokerTable import PokerTable
from Source.AccountHandler import AccountHandler
from Source.MessageType import MessageType
from Source.User import User

# File to store player accounts (username:password:balance)
ACCOUNTS_FILE = 'player_accounts.txt'
FINISHED_GAMES = 'finished_games.txt'


class PokerServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.playing_tables = []
        self.waiting_tables = []  # Dictionary to store PokerTable instances
        self.waiting_tables.append(PokerTable('Table 1'))
        self.waiting_tables.append(PokerTable('Table 2'))
        self.waiting_tables.append(PokerTable('Table 3'))
        self.waiting_tables.append(PokerTable('Table 4'))
        self.waiting_tables.append(PokerTable('Table 5'))
        self.waiting_tables.append(PokerTable('Table 6'))
        self.waiting_tables.append(PokerTable('Table 7'))
        self.waiting_tables.append(PokerTable('Table 8'))
        # self.accounts = self.load_players()
        # self.connected_users = {}
        self.accountHandler = AccountHandler(ACCOUNTS_FILE)
        # self.previous_games = self.load_previous_games()

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen()

        print(f"Player accounts loaded.")

        print(f"Server listening on {self.host}:{self.port}")

        try:
            while True:
                client_socket, address = server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.start()
        except KeyboardInterrupt:
            print("Server shutting down.")
        finally:
            server_socket.close()

    def handle_client(self, client_socket):
        # Handle a new client connection

        try:
            # Receive client_name from the client
            while True:
                message = pickle.loads(client_socket.recv(1024))

                match message['action']:
                    case MessageType.Login:
                        if self.accountHandler.login_user(message['username'], message['password'], client_socket):
                            client_socket.send(pickle.dumps({"action": MessageType.Login, "status": "successful"}))
                        else:
                            client_socket.send(pickle.dumps({"action": MessageType.Login, "status": "unsuccessful",
                                                             "message": "Username and password do not match or do not exist"}))
                    case MessageType.Register:
                        if self.accountHandler.register_user(message['username'], message['password'], client_socket):
                            client_socket.send(pickle.dumps({"action": MessageType.Register, "status": "successful"}))
                        else:
                            client_socket.send(pickle.dumps({"action": MessageType.Register, "status": "unsuccessful",
                                                             "message": "User with this name already exists"}))
                    case MessageType.GetLobbies:
                        client_socket.send(pickle.dumps({"lobbies": self.waiting_tables}))
                    case MessageType.Join:
                        pass
                    case MessageType.Create:
                        pass
                    case MessageType.Quit:
                        break
                    case _:
                        pass

        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()


if __name__ == "__main__":
    # Set your server's host and port
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = 5555

    poker_server = PokerServer(SERVER_HOST, SERVER_PORT)

    poker_server.start()
