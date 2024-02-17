import socket
import threading
import pickle  # For serializing Python objects for network communication
from PokerTable import PokerTable
from Source.AccountHandler import AccountHandler
from Source.CardDeck import CardDeck
from Source.MessageType import MessageType
from Source.User import User

# File to store player accounts (username:password:balance)
ACCOUNTS_FILE = 'player_accounts.txt'
FINISHED_GAMES = 'finished_games.txt'


class PokerServer:
    """Server that listens for connections and handles clients"""
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.playing_tables = []
        self.waiting_tables = []  # Array to store PokerTable instances
        # self.waiting_tables.append(PokerTable('temp1'))
        self.accountHandler = AccountHandler(ACCOUNTS_FILE)
        self.deck = CardDeck.cards_img.copy()
        # self.previous_games = self.load_previous_games()

    def start(self):
        """Creates server socket and listens for clients"""
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
        """Listens for messages from the client socket and answers them"""

        try:
            # Receive client_name from the client
            while True:
                message = pickle.loads(client_socket.recv(4000))

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
                        data = pickle.dumps({"lobbies": self.waiting_tables})
                        client_socket.send(data)

                    case MessageType.Join:
                        for table in self.waiting_tables:
                            if table.table_name == message['table_name']:
                                table.players.append(message['username'])
                                table.draw_cards()
                                client_socket.send(pickle.dumps({"action": MessageType.Join, "status": "successful"}))
                                break
                        pass

                    case MessageType.Create:
                        poker_table = PokerTable(message['username'])
                        poker_table.players.append(message['username'])
                        self.waiting_tables.append(poker_table)
                        client_socket.send(pickle.dumps({"action": MessageType.Create, "status": "successful"}))
                        print("Created new table")

                    case MessageType.StartTable:
                        players_to_start = {}
                        for table in self.waiting_tables:
                            if table.table_name == message['owner_name'] + "'s table":
                                for player in table.players:
                                    players_to_start[player] = self.accountHandler.connected_users[player]

                                self.start_poker_game(table, players_to_start)
                                break

                    case MessageType.RefreshTable:
                        self.broadcast_table_information(message['username'])

                    case MessageType.Quit:
                        self.delete_table_if_owner_quits(message['username'])
                        break

                    case MessageType.RefreshTableForOne:
                        self.send_table_information(message['table_name'], client_socket)

                    case MessageType.DeleteTable:
                        pass
                    case MessageType.TableForOwner:
                        for table in self.waiting_tables:
                            if table.table_name == message['table_name']:
                                client_socket.send(pickle.dumps({"table": table}))

                    case _:
                        pass

        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()

    def delete_table_if_owner_quits(self, owner):
        """Deletes a table from the waiting table list if the owner quits"""
        table_name = owner + "'s table"
        for table in self.waiting_tables:
            if table.table_name == table_name:

                for player_name in table.players:
                    if player_name != owner:
                        player_socket = self.accountHandler.connected_users[player_name]
                        player_socket.send(pickle.dumps({'action': MessageType.DeleteTable}))

                self.waiting_tables.remove(table)

    def broadcast_table_information(self, owner_name):
        """Sends table information to everyone on the table"""
        table_name = owner_name + "'s table"
        for table in self.waiting_tables:
            if table.table_name == table_name:
                for player_name in table.players:
                    player_socket = self.accountHandler.connected_users[player_name]
                    print(player_socket)
                    player_socket.send(pickle.dumps({'action': MessageType.RefreshTable, 'table': table}))

    def send_table_information(self, table_name, client_socket):
        """Sends table information only to the user that requested it"""
        for table in self.waiting_tables:
            if table.table_name == table_name:
                client_socket.send(pickle.dumps({"action": MessageType.RefreshTableForOne, 'table': table}))

    def start_poker_game(self, poker_table, player_sockets):
        for player in player_sockets:
            player_sockets[player].send(pickle.dumps({'action': MessageType.StartTable}))
            # print(f'sent start message to player {player}')
            player_sockets[player].send(pickle.dumps({'action': MessageType.RefreshTable, 'table': poker_table}))

        passed = []
        current_player = 0
        while len(passed) != len(player_sockets):
            pass

    def broadcast_to_table(self, table, action, message):
        for player_name in table.players:
            player_socket = self.accountHandler.connected_users[player_name]
            print(player_socket)
            player_socket.send(pickle.dumps({'action': action, 'message': message}))


if __name__ == "__main__":
    # Set your server's host and port
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = 5555

    poker_server = PokerServer(SERVER_HOST, SERVER_PORT)

    poker_server.start()
