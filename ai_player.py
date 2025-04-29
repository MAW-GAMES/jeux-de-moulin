import random

class AIPlayer:
    def __init__(self, player_id, color):
        self.player_id = player_id  # 1 or 2
        self.color = color  # "red" or "blue"

    def choose_action(self, env, mouse_pos=None, clicked=False):
        if env.awaiting_removal == self:
            removable = [i for i in range(24) if env.can_remove(i)]
            if removable:
                return ("remove", random.choice(removable))
        elif env.phase == "placement":
            valid_places = [i for i in range(24) if env.is_valid_place(i)]
            if valid_places:
                return ("place", random.choice(valid_places))
        elif env.phase == "movement":
            valid_moves = []
            for from_pos in range(24):
                if env.board[from_pos] == self.player_id:
                    for to_pos in range(24):
                        if env.is_valid_move(from_pos, to_pos):
                            valid_moves.append((from_pos, to_pos))
            if valid_moves:
                from_pos, to_pos = random.choice(valid_moves)
                return ("move", from_pos, to_pos)
        return None