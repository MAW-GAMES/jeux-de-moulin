import pygame
import asyncio
import platform
from game_env import JeuDuMoulinEnv
from player.human_player import HumanPlayer
from player.ai_player import AIPlayer
from constants import POSITIONS, CONNECTIONS

# Constants
WIDTH, HEIGHT = 600, 600
BUTTON_WIDTH, BUTTON_HEIGHT = 250, 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
FPS = 60

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Nine Men's Morris")
font = pygame.font.Font(None, 36)

def draw_button(text, x, y, color, text_color=WHITE):
    pygame.draw.rect(screen, color, (x, y, BUTTON_WIDTH, BUTTON_HEIGHT), border_radius=10)
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(x + BUTTON_WIDTH // 2, y + BUTTON_HEIGHT // 2))
    screen.blit(text_surface, text_rect)

def draw_board():
    screen.fill(WHITE)
    for start, end in CONNECTIONS:
        pygame.draw.line(screen, BLACK, POSITIONS[start], POSITIONS[end], 2)
    for pos in POSITIONS.values():
        pygame.draw.circle(screen, BLACK, pos, 10)

def draw_pieces(board):
    for idx, player in board.items():
        if player == 1:
            pygame.draw.circle(screen, RED, POSITIONS[idx], 8)
        elif player == 2:
            pygame.draw.circle(screen, BLUE, POSITIONS[idx], 8)

def draw_status(env):
    status = f"Phase: {env.phase.capitalize()} | Turn: Player {env.current_player.player_id}"
    if env.awaiting_removal:
        status += " | Select piece to remove"
    text_surface = font.render(status, True, BLACK)
    screen.blit(text_surface, (10, 10))
    if env.game_over:
        winner_text = f"Player {env.winner} wins!"
        text_surface = font.render(winner_text, True, BLACK)
        screen.blit(text_surface, (WIDTH // 2 - 100, HEIGHT // 2))

async def main_menu():
    running = True
    game_mode = None
    player1_color = None
    player2_color = None

    while running:
        screen.fill(WHITE)
        title_surface = font.render("Nine Men's Morris", True, BLACK)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 8))
        screen.blit(title_surface, title_rect)

        draw_button("Play vs Player", WIDTH // 2 - BUTTON_WIDTH // 2, HEIGHT // 4, GRAY)
        draw_button("Play vs AI", WIDTH // 2 - BUTTON_WIDTH // 2, HEIGHT // 4 + 100, GRAY)
        draw_button("Red", WIDTH // 4 - BUTTON_WIDTH // 2, HEIGHT // 2 + 100, RED)
        draw_button("Blue", WIDTH // 4 * 3 - BUTTON_WIDTH // 2, HEIGHT // 2 + 100, BLUE)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None, None, None
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if WIDTH // 2 - BUTTON_WIDTH // 2 <= x <= WIDTH // 2 + BUTTON_WIDTH // 2:
                    if HEIGHT // 4 <= y <= HEIGHT // 4 + BUTTON_HEIGHT:
                        game_mode = "player_vs_player"
                    elif HEIGHT // 4 + 100 <= y <= HEIGHT // 4 + 100 + BUTTON_HEIGHT:
                        game_mode = "player_vs_ai"
                if WIDTH // 4 - BUTTON_WIDTH // 2 <= x <= WIDTH // 4 + BUTTON_WIDTH // 2 and HEIGHT // 2 + 100 <= y <= HEIGHT // 2 + 100 + BUTTON_HEIGHT:
                    player1_color = "red"
                    player2_color = "blue"
                elif WIDTH // 4 * 3 - BUTTON_WIDTH // 2 <= x <= WIDTH // 4 * 3 + BUTTON_WIDTH // 2 and HEIGHT // 2 + 100 <= y <= HEIGHT // 2 + 100 + BUTTON_HEIGHT:
                    player1_color = "blue"
                    player2_color = "red"
                if game_mode and player1_color and player2_color:
                    running = False

        await asyncio.sleep(0.01)
    return game_mode, player1_color, player2_color

async def game_loop(game_mode, player1_color, player2_color):
    env = JeuDuMoulinEnv()
    player1 = HumanPlayer(1, player1_color)
    player2 = HumanPlayer(2, player2_color) if game_mode == "player_vs_player" else AIPlayer(2, player2_color)
    env.player1 = player1
    env.player2 = player2
    env.current_player = player1

    clock = pygame.time.Clock()
    running = True
    while running:
        screen.fill(WHITE)
        draw_board()
        draw_pieces(env.board)
        draw_status(env)
        pygame.display.flip()
        clock.tick(FPS)

        mouse_pos = None
        clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                clicked = True

        action = env.current_player.choose_action(env, mouse_pos, clicked)
        if action:
            if action[0] == "place":
                env.make_place(action[1])
            elif action[0] == "move":
                env.make_move(action[1], action[2])
            elif action[0] == "remove":
                env.remove_piece(action[1])

        if env.game_over:
            await asyncio.sleep(3)  # Show winner for 3 seconds
            running = False

        await asyncio.sleep(1.0 / FPS)

async def main():
    game_mode, player1_color, player2_color = await main_menu()
    if game_mode and player1_color and player2_color:
        await game_loop(game_mode, player1_color, player2_color)
    pygame.quit()

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())