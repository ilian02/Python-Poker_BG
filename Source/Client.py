import socket
import pickle  # For serializing Python objects for network communication
import sys

import pygame

from Source.MessageType import MessageType

SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 900

pygame.init()
pygame.display.set_caption("Poker with friends")

BACKGROUND_IMG = pygame.image.load('../img/pokerBG2.jpg')
FONT = pygame.font.Font(None, 48)
TEXT_COLOUR = (255, 255, 255)
BACKGROUND_COLOR = (1, 50, 32)

LOGIN_BUTTON_IMG = pygame.image.load('../img/button_login.png')
REGISTER_BUTTON_IMG = pygame.image.load('../img/button_register.png')
GO_BACK_BUTTON_IMG = pygame.image.load('../img/button_go-back.png')


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

    def draw_text(self, text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        self.screen.blit(img, (x, y))

    def menu(self):
        # self.screen.blit(BACKGROUND_IMG, [0, 0])   # Background image
        self.screen.fill(BACKGROUND_COLOR)  # Temporary background
        self.draw_text("Poker with friends", FONT, TEXT_COLOUR, 450, 150)

        login_button = Button(LOGIN_BUTTON_IMG, 250, 300, 268, 66)
        register_button = Button(REGISTER_BUTTON_IMG, 250, 450, 268, 66)

        self.screen.blit(login_button.image, (login_button.x, login_button.y))
        self.screen.blit(register_button.image, (register_button.x, register_button.y))

        run = True
        while run:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if login_button.check_if_clicked(pygame.mouse.get_pos()):
                        print("Loading logging page")
                        self.login_page()
                    if register_button.check_if_clicked(pygame.mouse.get_pos()):
                        print("Loading registering page")
                        self.register_page()

            pygame.display.update()

    def register_page(self):
        username = ""
        password = ""
        active_input = 'username'
        self.screen.fill((1, 50, 32))
        login_button = Button(REGISTER_BUTTON_IMG, 250, 600, 268, 66)
        back_button = Button(GO_BACK_BUTTON_IMG, 250, 300, 268, 66)
        invalid_message = False

        while True:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.check_if_clicked(pygame.mouse.get_pos()):
                        print("Loading menu page")
                        self.menu()
                    if login_button.check_if_clicked(pygame.mouse.get_pos()):
                        print(f"Registering with {username} and {password}")
                        if self.register(username, password):
                            # registered corectly
                            pass
                        else:
                            invalid_message = True

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if active_input == 'username':
                            active_input = 'password'
                        else:
                            active_input = 'username'
                    elif active_input == "username":
                        if event.key == pygame.K_BACKSPACE:
                            username = username[:-1]
                        else:
                            username += event.unicode
                    elif active_input == "password":
                        if event.key == pygame.K_BACKSPACE:
                            password = password[:-1]
                        else:
                            password += event.unicode

            self.screen.fill((1, 50, 32))

            self.draw_text("Register", FONT, TEXT_COLOUR, 450, 150)

            if invalid_message:
                self.draw_text("Name already exists", FONT, TEXT_COLOUR, 450, 800)

            self.screen.blit(back_button.image, (back_button.x, back_button.y))
            self.screen.blit(login_button.image, (login_button.x, login_button.y))


            # Render username input field
            username_text = pygame.font.Font(None, 38).render("Username: " + username, True, (255, 255, 255))
            username_rect = username_text.get_rect(center=(350, 450))
            self.screen.blit(username_text, username_rect)

            # Render password input field
            password_text = pygame.font.Font(None, 38).render("Password: " + "*" * len(password), True, (255, 255, 255))
            password_rect = password_text.get_rect(center=(350, 550))
            self.screen.blit(password_text, password_rect)

            pygame.display.update()

    def login_page(self):
        username = ""
        password = ""
        active_input = 'username'
        self.screen.fill((1, 50, 32))
        login_button = Button(LOGIN_BUTTON_IMG, 250, 600, 268, 66)
        back_button = Button(GO_BACK_BUTTON_IMG, 250, 300, 268, 66)
        invalid_message = False

        while True:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.check_if_clicked(pygame.mouse.get_pos()):
                        print("Loading menu page")
                        self.menu()
                    if login_button.check_if_clicked(pygame.mouse.get_pos()):
                        print(f"Logging with {username} and {password}")
                        if self.login(username, password):
                            # logged in correctly

                            pass
                        else:
                            invalid_message = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if active_input == 'username':
                            active_input = 'password'
                        else:
                            active_input = 'username'
                    elif active_input == "username":
                        if event.key == pygame.K_BACKSPACE:
                            username = username[:-1]
                        else:
                            username += event.unicode
                    elif active_input == "password":
                        if event.key == pygame.K_BACKSPACE:
                            password = password[:-1]
                        else:
                            password += event.unicode

            self.screen.fill((1, 50, 32))

            self.draw_text("Log-in page", FONT, TEXT_COLOUR, 450, 150)
            if invalid_message:
                self.draw_text("Invalid login info", FONT, TEXT_COLOUR, 450, 800)
            self.screen.blit(back_button.image, (back_button.x, back_button.y))
            self.screen.blit(login_button.image, (login_button.x, login_button.y))

            # Render username input field
            username_text = pygame.font.Font(None, 38).render("Username: " + username, True, (255, 255, 255))
            username_rect = username_text.get_rect(center=(350, 450))
            self.screen.blit(username_text, username_rect)

            # Render password input field
            password_text = pygame.font.Font(None, 38).render("Password: " + "*" * len(password), True, (255, 255, 255))
            password_rect = password_text.get_rect(center=(350, 550))
            self.screen.blit(password_text, password_rect)

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

    def login(self, username, password):
        self.send_message({"action": MessageType.Login, "username": username, "password": password})

        response = self.receive_message()
        if response['action'] == MessageType.Login and response['status'] == 'successful':
            print(f"You are loggen in as {username}")
            self.logged_in = True
            return True
        else:
            print("Login was unsuccessful.")
            return False

    def register(self, username, password):
        self.send_message({"action": MessageType.Register, "username": username, "password": password})

        response = self.receive_message()
        print(response)
        if response['action'] == MessageType.Register and response['status'] == 'successful':
            print(f"You are registered in as {username}")
            self.logged_in = True
            return True
        else:
            print("Register was unsuccessful.")
            return False

    def close_connection(self):
        self.client_socket.close()

    def load_lobbies(self):
        self.send_message({'action': MessageType.GetLobbies})

        response = self.receive_message()
        print(response)


class Button:
    def __init__(self, image, x, y, width, height):
        self.image = image
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def check_if_clicked(self, mouse_pos):
        return self.x <= mouse_pos[0] <= self.x + self.width and self.y <= mouse_pos[1] <= self.y + self.height


if __name__ == "__main__":
    # Set your server's host and port
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = 5555

    # Create a PokerClient instance
    poker_client = PokerClient(SERVER_HOST, SERVER_PORT)

    try:
        poker_client.connect_to_server()

        # Implement the game loop or user interface here
        poker_client.menu()

    except KeyboardInterrupt:
        print("Client shutting down.")
    finally:
        poker_client.close_connection()
