import pygame
import socket
import json
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import PPO

# Définir l'environnement pour l'IA
class NineMensMorrisEnv(gym.Env):
    def __init__(self):
        super(NineMensMorrisEnv, self).__init__()
        self.observation_space = spaces.MultiDiscrete([3] * 24)  # 24 positions
        self.action_space = spaces.Discrete(24 * 24)  # Actions possibles
        self.board = np.zeros(24, dtype=int)
        self.phase = "placement"
        self.player = 1
        self.pieces = {1: 9, 2: 9}
        self.mills = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8), (9, 10, 11), (12, 13, 14),
            (15, 16, 17), (18, 19, 20), (21, 22, 23),
            (0, 9, 21), (3, 10, 18), (6, 11, 15), (1, 4, 7),
            (16, 19, 22), (8, 12, 17), (5, 13, 20), (2, 14, 23)
        ]

    def reset(self, seed=None, options=None):
        self.board = np.zeros(24, dtype=int)
        self.phase = "placement"
        self.player = 1
        self.pieces = {1: 9, 2: 9}
        return self.board, {}

    def step(self, action):
        if self.phase == "placement":
            pos = action % 24
            if self.board[pos] == 0:
                self.board[pos] = self.player
                self.pieces[self.player] -= 1
                reward = 1 if self._check_mill(pos) else 0
            else:
                reward = -1
        else:
            from_pos = action // 24
            to_pos = action % 24
            if self.board[from_pos] == self.player and self.board[to_pos] == 0:
                self.board[from_pos] = 0
                self.board[to_pos] = self.player
                reward = 1 if self._check_mill(to_pos) else 0
            else:
                reward = -1

        done = self._check_game_over()
        self.player = 3 - self.player
        if self.pieces[1] == 0 and self.pieces[2] == 0:
            self.phase = "movement"
        return self.board, reward, done, False, {}

    def _check_mill(self, pos):
        for mill in self.mills:
            if pos in mill and all(self.board[i] == self.player for i in mill):
                return True
        return False

    def _check_game_over(self):
        opponent = 3 - self.player
        if self.phase == "movement":
            pieces = sum(1 for v in self.board if v == opponent)
            if pieces < 3:
                return True
            moves = False
            for i in range(24):
                if self.board[i] == opponent:
                    for j in range(24):
                        if self.board[j] == 0 and ((i, j) in CONNECTIONS or (j, i) in CONNECTIONS):
                            moves = True
                            break
                    if moves:
                        break
            if not moves:
                return True
        return False

    def render(self):
        print(self.board)

# Initialisation de Pygame
pygame.init()
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jeu du Moulin")

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Positions (24 points)
POSITIONS = {
    # Carré extérieur
    0: (100, 100), 1: (300, 100), 2: (500, 100),  # Haut
    3: (100, 300), 4: (500, 300),  # Milieu
    5: (100, 500), 6: (300, 500), 7: (500, 500),  # Bas
    # Carré moyen
    8: (150, 150), 9: (300, 150), 10: (450, 150),  # Haut
    11: (150, 300), 12: (450, 300),  # Milieu
    13: (150, 450), 14: (300, 450), 15: (450, 450),  # Bas
    # Carré intérieur
    16: (200, 200), 17: (300, 200), 18: (400, 200),  # Haut
    19: (200, 300), 20: (400, 300),  # Milieu
    21: (200, 400), 22: (300, 400), 23: (400, 400)  # Bas
}

# Connexions (lignes entre les positions) ajustées
CONNECTIONS = [
    # Carré extérieur
    (0, 1), (1, 2),  # Haut
    (0, 3), (3, 5),  # Gauche
    (2, 4), (4, 7),  # Droite
    (5, 6), (6, 7),  # Bas
    # Carré moyen
    (8, 9), (9, 10),  # Haut
    (8, 11), (11, 13),  # Gauche
    (10, 12), (12, 15),  # Droite
    (13, 14), (14, 15),  # Bas
    # Carré intérieur
    (16, 17), (17, 18),  # Haut
    (16, 19), (19, 21),  # Gauche
    (18, 20), (20, 23),  # Droite
    (21, 22), (22, 23),  # Bas
    # Lignes transversales
    (1, 9), (4, 12), (6, 14),  # Extérieur -> Moyen (haut, droite, bas)
    (3, 11),  # Extérieur -> Moyen (gauche)
    (9, 17), (12, 20), (14, 22),  # Moyen -> Intérieur (haut, droite, bas)
    (11, 19)  # Moyen -> Intérieur (gauche) - (15, 23) supprimé
]

# Connexion au serveur
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 12345))
player_id = int(client.recv(1024).decode())

# Charger l'agent DRL si joueur 2
if player_id == 2:
    env = NineMensMorrisEnv()
    model = PPO.load("ppo_ninemensmorris")

def draw_board():
    screen.fill(WHITE)
    for start, end in CONNECTIONS:
        pygame.draw.line(screen, BLACK, POSITIONS[start], POSITIONS[end], 2)
    for pos in POSITIONS.values():
        pygame.draw.circle(screen, BLACK, pos, 10)
    pygame.display.flip()

def get_clicked_position(mouse_pos):
    for idx, pos in POSITIONS.items():
        if ((mouse_pos[0] - pos[0]) ** 2 + (mouse_pos[1] - pos[1]) ** 2) < 15 ** 2:
            return idx
    return None

def main():
    running = True
    board = {i: 0 for i in range(24)}  # 24 positions
    phase = "placement"
    selected_piece = None
    turn = 1

    try:
        while running:
            draw_board()
            for idx, player in board.items():
                if player == 1:
                    pygame.draw.circle(screen, RED, POSITIONS[idx], 8)
                elif player == 2:
                    pygame.draw.circle(screen, BLUE, POSITIONS[idx], 8)
            pygame.display.flip()

            # Tour du joueur humain (joueur 1)
            if player_id == turn and player_id == 1:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        pos = get_clicked_position(pygame.mouse.get_pos())
                        if pos is not None:
                            if phase == "placement" and board[pos] == 0:
                                client.send(json.dumps({"action": "place", "position": pos}).encode())
                            elif phase == "movement" and selected_piece is None and board[pos] == player_id:
                                selected_piece = pos
                            elif phase == "movement" and selected_piece is not None and board[pos] == 0:
                                if (selected_piece, pos) in CONNECTIONS or (pos, selected_piece) in CONNECTIONS:
                                    client.send(json.dumps({"action": "move", "from": selected_piece, "to": pos}).encode())
                                    selected_piece = None

            # Tour de l'IA (joueur 2)
            elif player_id == turn and player_id == 2:
                env.board = np.array([board[i] for i in range(24)])
                env.phase = phase
                env.player = 2
                env.pieces = {1: sum(1 for v in board.values() if v == 1), 2: sum(1 for v in board.values() if v == 2)}

                action, _ = model.predict(env.board)
                if phase == "placement":
                    pos = action % 24
                    if board[pos] == 0:
                        client.send(json.dumps({"action": "place", "position": pos}).encode())
                else:
                    from_pos = action // 24
                    to_pos = action % 24
                    if board[from_pos] == 2 and board[to_pos] == 0 and ((from_pos, to_pos) in CONNECTIONS or (to_pos, from_pos) in CONNECTIONS):
                        client.send(json.dumps({"action": "move", "from": from_pos, "to": to_pos}).encode())

            # Recevoir les mises à jour du serveur
            try:
                client.settimeout(0.1)
                data = client.recv(1024).decode()
                if data:
                    update = json.loads(data)
                    # Ensure board keys are integers
                    board = {int(k): v for k, v in update["board"].items()}
                    phase = update["phase"]
                    turn = update["turn"]
                    if "winner" in update:
                        print(f"Joueur {update['winner']} gagne !")
                        running = False
            except socket.timeout:
                pass
    finally:
        client.close()
        pygame.quit()

if __name__ == "__main__":
    main()
