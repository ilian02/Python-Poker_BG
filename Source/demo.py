import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Login Screen")

# Set up font
font = pygame.font.Font(None, 36)

# Input fields
username = ""
password = ""
active_input = None  # To track which input field is active

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if active_input == "username":
                    active_input = "password"
                else:
                    active_input = "username"
            elif active_input == "password":
                if event.key == pygame.K_BACKSPACE:
                    password = password[:-1]  # Remove the last character
                else:
                    password += event.unicode  # Add the pressed character to the password
            elif active_input == "username":
                if event.key == pygame.K_BACKSPACE:
                    username = username[:-1]  # Remove the last character
                else:
                    username += event.unicode  # Add the pressed character to the username

    # Clear the screen
    screen.fill((0, 0, 0))  # Black

    # Render username input field
    username_text = font.render("Username: " + username, True, (255, 255, 255))
    username_rect = username_text.get_rect(center=(width // 2, height // 2 - 20))
    screen.blit(username_text, username_rect)

    # Render password input field
    password_text = font.render("Password: " + "*" * len(password), True, (255, 255, 255))
    password_rect = password_text.get_rect(center=(width // 2, height // 2 + 20))
    screen.blit(password_text, password_rect)

    # Update the display
    pygame.display.flip()
