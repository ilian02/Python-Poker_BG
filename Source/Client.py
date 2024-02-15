import socket
import pickle  # For serializing Python objects for network communication
import pygame

from Source.MessageType import MessageType

SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 900

BACKGROUND_IMG = pygame.image.load('../img/pokerBG2.jpg')


class PokerClient:
    def __init__(self, server_host, server_port):
        self.logged_in = False
        self.table_name = None
        self.player_password = None
        self.server_host = server_host
        self.server_port = server_port
        self.player_name = None
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    def menu(self):
        pygame.init()

        # self.screen.blit(BACKGROUND_IMG, [0, 0])   # Background image
        self.screen.fill((1, 50, 32)) # Temporary background

        run = True
        while run:
            pygame.draw.rect(self.screen, (255, 0, 0), pygame.Rect((50, 50, 50, 50)))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            pygame.display.update()

    def connect_to_server(self):
        self.client_socket.connect((self.server_host, self.server_port))

    def send_message(self, message):
        # Send a message to the server
        serialized_message = pickle.dumps(message)
        self.client_socket.send(serialized_message)

    def receive_message(self):
        # Receive a message from the server
        serialized_message = self.client_socket.recv(1024)
        return pickle.loads(serialized_message)

    def play_game(self):
        # Implement game logic, user input, and communication with the server
        pass

    def login(self):
        self._get_profile_info_and_send_message(MessageType.Login)

        response = self.receive_message()
        if response['action'] == MessageType.Login and response['status'] == 'successful':
            print(f"You are loggen in as {self.player_name}")
            self.logged_in = True
            return True
        else:
            print("Login was unsuccessful.")
            return False

    def register(self):
        self._get_profile_info_and_send_message(MessageType.Register)

        response = self.receive_message()
        print(response)
        if response['action'] == MessageType.Register and response['status'] == 'successful':
            print(f"You are registered in as {self.player_name}")
            self.logged_in = True
            return True
        else:
            print("Register was unsuccessful.")
            return False

    def _get_profile_info_and_send_message(self, action):
        self.player_name = input("Enter your name: ")
        self.player_password = input("Enter your password: ")

        # Join the poker table
        self.send_message({"action": action, "username": self.player_name, "password": self.player_password})

    def close_connection(self):
        self.client_socket.close()

    def load_lobbies(self):
        self.send_message({'action': MessageType.GetLobbies})

        response = self.receive_message()
        print(response)


if __name__ == "__main__":
    # Set your server's host and port
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = 5555

    # Create a PokerClient instance
    poker_client = PokerClient(SERVER_HOST, SERVER_PORT)

    try:
        poker_client.connect_to_server()

        # Get the table_id and player_name from the user and try to login or register

        '''
        print("login or register")

        command = input()
        if command == "login":
            poker_client.login()
            print("hello")
        elif command == "register":
            poker_client.register()
            print("welcome")
        else:
            print("Unknown command")

        if poker_client.logged_in:
            poker_client.load_lobbies()
        '''

        # Implement the game loop or user interface here
        poker_client.menu()

    except KeyboardInterrupt:
        print("Client shutting down.")
    finally:
        poker_client.close_connection()
