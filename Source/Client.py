import socket
import pickle  # For serializing Python objects for network communication
import sys
import threading
import time

import pygame

from Source.CardDeck import CardDeck
from Source.MessageType import MessageType
from Source.PokerTable import PokerTable

SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 700

pygame.init()
pygame.display.set_caption("Poker with friends")

BACKGROUND_IMG = pygame.image.load('../img/pokerBG2.jpg')
FONT = pygame.font.Font(None, 48)
FONT_LOBBIES = pygame.font.Font(None, 35)
TEXT_COLOUR = (255, 255, 255)
BACKGROUND_COLOR = (1, 50, 32)

active_color = (255, 255, 255)
inactive_color = (160, 160, 160)

LOGIN_BUTTON_IMG = pygame.image.load('../img/button_login.png')
REGISTER_BUTTON_IMG = pygame.image.load('../img/button_register.png')
GO_BACK_BUTTON_IMG = pygame.image.load('../img/button_go-back.png')
CREATE_NEW_TABLE_IMG = pygame.image.load('../img/button_create-new-table.png')
REFRESH_TABLES_IMG = pygame.image.load('../img/button_refresh-tables.png')
START_GAME_IMG = pygame.image.load('../img/button_start-game.png')
CARD_BACK_IMAGE = pygame.image.load('../img/cards/back.png')
BID_BUTTON_IMAGE = pygame.image.load('../img/button_bid.png')
FOLD_BUTTON_IMAGE = pygame.image.load('../img/button_fold.png')
PASS_BUTTON_IMAGE = pygame.image.load('../img/button_pass.png')


class PokerClient:
    """Client Thread that takes care of the client GUI and input"""
    def __init__(self, server_host, server_port):
        self.show_options = True
        self.game_started = False
        self.run = True
        self.tables = []
        self.logged_in = False
        self.table_name = None
        self.username = None
        self.password = None
        self.current_table = None
        self.server_host = server_host
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.current_bid = 0

    def draw_text(self, text, font, text_col, x, y):
        """Draw text to screen"""

        img = font.render(text, True, text_col)
        self.screen.blit(img, (x, y))

    def menu(self):
        """GUI for the main menu for login and register buttons"""

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
        """Register page GUI which lets user input username and password and sends register request to server"""

        username = ""
        password = ""
        active_input = 'username'
        self.screen.fill(BACKGROUND_COLOR)
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
                            self.lobby_menu()
                            pass
                        else:
                            invalid_message = True

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
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

            self.screen.fill(BACKGROUND_COLOR)

            self.draw_text("Register", FONT, TEXT_COLOUR, 450, 150)

            if invalid_message:
                self.draw_text("Name already exists", FONT, TEXT_COLOUR, 450, 800)

            self.screen.blit(back_button.image, (back_button.x, back_button.y))
            self.screen.blit(login_button.image, (login_button.x, login_button.y))

            if active_input == 'username':
                username_text_color = active_color
                password_text_color = inactive_color
            else:
                username_text_color = inactive_color
                password_text_color = active_color

            # Render username input field
            username_text = pygame.font.Font(None, 38).render("Username: " + username,
                                                              True, username_text_color)
            username_rect = username_text.get_rect(center=(350, 450))
            self.screen.blit(username_text, username_rect)

            # Render password input field
            password_text = pygame.font.Font(None, 38).render("Password: " + "*" * len(password),
                                                              True, password_text_color)
            password_rect = password_text.get_rect(center=(350, 550))
            self.screen.blit(password_text, password_rect)

            pygame.display.update()

    def login_page(self):
        """Login page GUI which lets user input username and password and sends login request to server"""
        username = ""
        password = ""
        active_input = 'username'
        self.screen.fill(BACKGROUND_COLOR)
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
                            self.lobby_menu()
                            pass
                        else:
                            invalid_message = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
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

            self.screen.fill(BACKGROUND_COLOR)

            self.draw_text("Log-in page", FONT, TEXT_COLOUR, 450, 150)
            if invalid_message:
                self.draw_text("Invalid login info", FONT, TEXT_COLOUR, 450, 800)
            self.screen.blit(back_button.image, (back_button.x, back_button.y))
            self.screen.blit(login_button.image, (login_button.x, login_button.y))

            if active_input == 'username':
                username_text_color = active_color
                password_text_color = inactive_color
            else:
                username_text_color = inactive_color
                password_text_color = active_color

            # Render username input field
            username_text = pygame.font.Font(None, 38).render("Username: " + username,
                                                              True, username_text_color)
            username_rect = username_text.get_rect(center=(350, 450))
            self.screen.blit(username_text, username_rect)

            # Render password input field
            password_text = pygame.font.Font(None, 38).render("Password: " + "*" * len(password),
                                                              True, password_text_color)
            password_rect = password_text.get_rect(center=(350, 550))
            self.screen.blit(password_text, password_rect)

            pygame.display.update()

    def lobby_menu(self):
        """Loads created tables and create new table button"""
        self.load_lobbies()

        create_table_button = Button(CREATE_NEW_TABLE_IMG, 650, 630, 391, 66)
        refresh_button = Button(REFRESH_TABLES_IMG, 650, 550, 391, 66)
        current_position = 0

        run = True
        while run:
            self.screen.fill(BACKGROUND_COLOR)  # Temporary background
            self.draw_text("Poker with friends", FONT, TEXT_COLOUR, 500, 150)
            self.screen.blit(create_table_button.image, (create_table_button.x, create_table_button.y))
            self.screen.blit(refresh_button.image, (refresh_button.x, refresh_button.y))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif (event.type == pygame.MOUSEWHEEL
                      and 50 < pygame.mouse.get_pos()[0] < 350
                      and 250 < pygame.mouse.get_pos()[1] < 450):
                    current_position = max(0, current_position + event.y)
                    current_position = min(current_position, len(self.tables) - 1)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_cords = pygame.mouse.get_pos()
                    if create_table_button.check_if_clicked(mouse_cords):
                        print("Trying to create new table")
                        self.create_table()
                    if refresh_button.check_if_clicked(mouse_cords):
                        print("Refreshing tables")
                        self.load_lobbies()
                    if 50 < mouse_cords[0] < 350 and 250 < mouse_cords[1] < 450:
                        # Pick clicked lobby
                        clickedY = mouse_cords[1] - 250
                        index = clickedY // 35
                        if index + current_position < len(self.tables):
                            self.join_table(current_position + index)
                            # print(f"Clicked table index is {current_position + index}")

            for i in range(current_position, current_position + 5):
                if i >= len(self.tables):
                    break
                text = ''.join([' ' + name for name in self.tables[i].players])
                self.draw_text(f"{self.tables[i].table_name} - {text}", FONT_LOBBIES, (255, 255, 255), 50,
                               250 + (i - current_position) * 35)

            pygame.display.update()

    def connect_to_server(self):
        self.client_socket.connect((self.server_host, self.server_port))

    def send_message(self, message):
        # Send a message to the server
        serialized_message = pickle.dumps(message)
        self.client_socket.send(serialized_message)

    def receive_message(self):
        # Receive a message from the server
        serialized_message = self.client_socket.recv(4000)
        return pickle.loads(serialized_message)

    def play_game(self):
        self.screen.fill(BACKGROUND_COLOR)
        time.sleep(1)

        all_cards_img = CardDeck.cards_img
        first_card = self.current_table.player_cards[self.username][0]
        second_card = self.current_table.player_cards[self.username][1]

        bid_button = Button(BID_BUTTON_IMAGE, 100, 530, 130, 67)
        pass_button = Button(PASS_BUTTON_IMAGE, 330, 530, 145, 67)
        fold_button = Button(FOLD_BUTTON_IMAGE, 100, 630, 145, 67)

        while True:
            self.screen.fill(BACKGROUND_COLOR)
            self.screen.blit(all_cards_img[first_card], (500, 500))
            self.screen.blit(all_cards_img[second_card], (570, 500))

            if self.show_options:
                self.screen.blit(bid_button.image, (bid_button.x, bid_button.y))
                self.screen.blit(pass_button.image, (pass_button.x, pass_button.y))
                self.screen.blit(fold_button.image, (fold_button.x, fold_button.y))

            for i in range(self.current_table.cards_shown, 5):
                self.screen.blit(CARD_BACK_IMAGE, (250+100*i, 250))

            self.screen.blit(CARD_BACK_IMAGE, (50, 350))
            self.screen.blit(CARD_BACK_IMAGE, (120, 350))

            if len(self.current_table.players) > 2:
                self.screen.blit(CARD_BACK_IMAGE, (350, 50))
                self.screen.blit(CARD_BACK_IMAGE, (420, 50))

            if len(self.current_table.players) > 3:
                self.screen.blit(CARD_BACK_IMAGE, (850, 350))
                self.screen.blit(CARD_BACK_IMAGE, (920, 350))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.send_message({"action": MessageType.Quit, 'username': self.username})
                    self.close_connection()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and self.show_options:
                    mouse_pos = pygame.mouse.get_pos()
                    if bid_button.check_if_clicked(mouse_pos):
                        self.send_message({"action": MessageType.Bid})
                        # self.show_options = False
                    if pass_button.check_if_clicked(mouse_pos):
                        self.send_message({"action": MessageType.Pass})
                        # self.show_options = False
                    if fold_button.check_if_clicked(mouse_pos):
                        self.send_message({"action": MessageType.Fold})
                        # self.show_options = False

            pygame.display.update()

    def login(self, username, password):
        """Sends login request to server"""
        self.send_message({"action": MessageType.Login, "username": username, "password": password})

        response = self.receive_message()
        if response['action'] == MessageType.Login and response['status'] == 'successful':
            print(f"You are loggen in as {username}")
            self.username = username
            self.logged_in = True
            return True
        else:
            print("Login was unsuccessful.")
            return False

    def register(self, username, password):
        """Sends register request to server"""
        self.send_message({"action": MessageType.Register, "username": username, "password": password})

        response = self.receive_message()
        print(response)
        if response['action'] == MessageType.Register and response['status'] == 'successful':
            print(f"You are registered in as {username}")
            self.username = username
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
        self.tables = response['lobbies']

    def create_table(self):
        """Sends create table request to server and makes the user join it"""
        # send message to server to create table and add user to it
        self.send_message({"action": MessageType.Create, 'username': self.username})
        response = self.receive_message()
        if response['action'] == MessageType.Create and response['status'] == 'successful':
            print(f"Created and joined table")
            self.current_table = PokerTable(self.username)
            self.current_table.players.append(self.username)
            self.host_table()
            return True
        else:
            print("Creating table was unsuccessful.")
            return False

    def join_table(self, index):
        """Joins the table picked from the scrolling menu based on the index"""
        self.send_message({"action": MessageType.Join, 'table_name': self.tables[index].table_name, 'username': self.username})
        response = self.receive_message()
        if response['action'] == MessageType.Join and response['status'] == 'successful':
            self.table_name = self.tables[index].table_name
            listening_thread = threading.Thread(target=self.listen_for_broadcasts)
            listening_thread.start()
            self.wait_for_table_to_start()
            return True
        else:
            print("Joining table was unsuccessful.")
            return False

    def host_table(self):
        """GUI for waiting table for the host"""

        refresh_button = Button(REFRESH_TABLES_IMG, 650, 500, 391, 66)
        start_button = Button(START_GAME_IMG, 650, 600, 391, 66)

        run = True
        while run:
            self.screen.fill(BACKGROUND_COLOR)  # Temporary background
            self.draw_text("Your table", FONT, TEXT_COLOUR, 500, 150)
            self.screen.blit(start_button.image, (start_button.x, start_button.y))
            self.screen.blit(refresh_button.image, (refresh_button.x, refresh_button.y))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.send_message({'action': MessageType.Quit, 'username': self.username})
                    # self.send_message({'action': MessageType.DeleteTable, 'username': self.username})
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_cords = pygame.mouse.get_pos()
                    if refresh_button.check_if_clicked(mouse_cords):
                        print("Trying to refresh table")
                        self.refresh_table()
                    if start_button.check_if_clicked(mouse_cords):
                        print("Trying to start table")
                        self.refresh_table()
                        self.send_message({'action': MessageType.StartTable, 'owner_name': self.username})
                        threading.Thread(target=self.receive_message)
                        self.play_game()

            for i in range(0, len(self.current_table.players)):
                self.draw_text(f"{self.current_table.players[i]}", FONT_LOBBIES, (255, 255, 255), 50,
                               250 + i * 35)

            pygame.display.update()

    def refresh_table(self):
        """Request updated information for the table"""
        self.send_message({'action': MessageType.RefreshTable, 'username': self.username})
        response = self.receive_message()
        if response['action'] == MessageType.RefreshTable:
            print(f"Table refreshed")
            self.current_table = response['table']

    def listen_for_broadcasts(self):
        """Listen for updates for the table the client has joined"""

        time.sleep(0.5)       # So it doesn't get the response of the wait_for_table_to_start function
        while True:
            response = self.receive_message()
            print(response)
            match response['action']:
                case MessageType.RefreshTable:
                    self.current_table = response['table']
                case MessageType.StartTable:
                    self.run = False
                    self.game_started = True
                case MessageType.YourTurn:
                    self.show_options = True
                    self.current_bid = response['current_bid']
                case MessageType.DeleteTable:
                    self.run = False
                case MessageType.Stop:
                    self.send_message({'action': MessageType.Stop})
                case MessageType.Quit:
                    self.close_connection()
                    pygame.quit()
                    sys.exit()

    def wait_for_table_to_start(self):
        """GUI for waiting for the table to start and updating connected users to table"""

        self.send_message({'action': MessageType.RefreshTableForOne, 'table_name': self.table_name})
        response = self.receive_message()
        self.current_table = response['table']
        while self.run:
            self.screen.fill(BACKGROUND_COLOR)  # Temporary background
            self.draw_text("Your table", FONT, TEXT_COLOUR, 500, 150)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            for i in range(0, len(self.current_table.players)):
                self.draw_text(f"{self.current_table.players[i]}", FONT_LOBBIES, (255, 255, 255), 50,
                               250 + i * 35)

            pygame.display.update()

        if self.game_started:
            self.play_game()

        self.close_connection()

        pygame.quit()
        sys.exit()


class Button:
    """Button class with image and coords"""
    def __init__(self, image, x, y, width, height):
        self.image = image
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def check_if_clicked(self, mouse_pos):
        return self.x <= mouse_pos[0] <= self.x + self.width and self.y <= mouse_pos[1] <= self.y + self.height


if __name__ == "__main__":
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = 5555

    poker_client = PokerClient(SERVER_HOST, SERVER_PORT)

    try:
        poker_client.connect_to_server()

        poker_client.menu()

    except KeyboardInterrupt:
        print("Client shutting down.")
    finally:
        poker_client.close_connection()
