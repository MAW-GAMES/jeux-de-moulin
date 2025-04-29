from constants import POSITIONS

class HumanPlayer:
    def __init__(self, player_id, color):
        self.player_id = player_id  # 1 or 2
        self.color = color  # "red" or "blue"
        self.selected_piece = None

    def choose_action(self, env, mouse_pos, clicked):
        if not clicked or mouse_pos is None:
            return None
        # Convert mouse position to board position
        pos = None
        for idx, (x, y) in POSITIONS.items():
            if ((mouse_pos[0] - x) ** 2 + (mouse_pos[1] - y) ** 2) < 15 ** 2:
                pos = idx
                break
        if pos is None:
            return None

        if env.awaiting_removal == self:
            if env.can_remove(pos):
                return ("remove", pos)
        elif env.phase == "placement":
            if env.is_valid_place(pos):
                return ("place", pos)
        elif env.phase == "movement":
            if self.selected_piece is None and env.board[pos] == self.player_id:
                self.selected_piece = pos
                return None
            elif self.selected_piece is not None and env.is_valid_move(self.selected_piece, pos):
                action = ("move", self.selected_piece, pos)
                self.selected_piece = None
                return action
            self.selected_piece = None
        return None