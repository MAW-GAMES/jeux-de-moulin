import gymnasium as gym
from gymnasium import spaces
import numpy as np
from stable_baselines3 import PPO

# Connexions (identiques à celles de client.py)
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
    (3, 11), (7, 15),  # Extérieur -> Moyen (gauche) - 5-13 supprimé
    (9, 17), (12, 20), (14, 22),  # Moyen -> Intérieur (haut, droite, bas)
    (11, 19), (13, 21), (15, 23)  # Moyen -> Intérieur (gauche)
]

class NineMensMorrisEnv(gym.Env):
    def __init__(self):
        super(NineMensMorrisEnv, self).__init__()
        self.observation_space = spaces.MultiDiscrete([3] * 24)  # 24 positions
        self.action_space = spaces.Discrete(24 * 24)
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

env = NineMensMorrisEnv()
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=10000)
model.save("ppo_ninemensmorris")
