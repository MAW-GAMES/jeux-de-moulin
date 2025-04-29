from constants import CONNECTIONS

class JeuDuMoulinEnv:
    def __init__(self):
        self.board = {i: 0 for i in range(24)}  # 0=empty, 1=player1, 2=player2
        self.current_player = None
        self.player1 = None
        self.player2 = None
        self.phase = "placement"
        self.pieces = {1: 9, 2: 9}  # Pieces to place
        self.game_over = False
        self.winner = None
        self.awaiting_removal = None
        self.mills = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8), (9, 10, 11), (12, 13, 14),
            (15, 16, 17), (18, 19, 20), (21, 22, 23),
            (0, 9, 21), (3, 10, 18), (6, 11, 15), (1, 4, 7),
            (16, 19, 22), (8, 12, 17), (5, 13, 20), (2, 14, 23)
        ]
        self.connections = CONNECTIONS

    def reset_game(self):
        self.board = {i: 0 for i in range(24)}
        self.phase = "placement"
        self.pieces = {1: 9, 2: 9}
        self.current_player = self.player1
        self.game_over = False
        self.winner = None
        self.awaiting_removal = None

    def is_valid_place(self, pos):
        return 0 <= pos < 24 and self.board[pos] == 0

    def is_valid_move(self, from_pos, to_pos):
        return (self.board[from_pos] == self.current_player.player_id and
                self.board[to_pos] == 0 and
                ((from_pos, to_pos) in self.connections or (to_pos, from_pos) in self.connections))

    def can_remove(self, pos):
        opponent = 3 - self.current_player.player_id
        if self.board[pos] != opponent:
            return False
        if not self.check_mill(opponent, pos):
            return True
        opponent_pieces = [i for i in range(24) if self.board[i] == opponent]
        for p in opponent_pieces:
            if not any(p in mill and all(self.board[i] == opponent for i in mill) for mill in self.mills):
                return False
        return True

    def check_mill(self, player, pos):
        for mill in self.mills:
            if pos in mill and all(self.board[i] == player for i in mill):
                return True
        return False

    def make_place(self, pos):
        if self.phase != "placement" or self.awaiting_removal:
            return False
        if self.is_valid_place(pos):
            self.board[pos] = self.current_player.player_id
            self.pieces[self.current_player.player_id] -= 1
            if self.check_mill(self.current_player.player_id, pos):
                self.awaiting_removal = self.current_player
            else:
                self.switch_player()
            if all(p == 0 for p in self.pieces.values()):
                self.phase = "movement"
            self.check_game_over()
            return True
        return False

    def make_move(self, from_pos, to_pos):
        if self.phase != "movement" or self.awaiting_removal:
            return False
        if self.is_valid_move(from_pos, to_pos):
            self.board[from_pos] = 0
            self.board[to_pos] = self.current_player.player_id
            if self.check_mill(self.current_player.player_id, to_pos):
                self.awaiting_removal = self.current_player
            else:
                self.switch_player()
            self.check_game_over()
            return True
        return False

    def remove_piece(self, pos):
        if not self.awaiting_removal:
            return False
        if self.can_remove(pos):
            self.board[pos] = 0
            self.awaiting_removal = None
            self.switch_player()
            self.check_game_over()
            return True
        return False

    def switch_player(self):
        self.current_player = self.player2 if self.current_player == self.player1 else self.player1

    def check_game_over(self):
        if self.phase == "movement":
            for player_id in [1, 2]:
                opponent = 3 - player_id
                pieces_left = sum(1 for v in self.board.values() if v == opponent)
                if pieces_left < 3:
                    self.game_over = True
                    self.winner = player_id
                    return
                moves = False
                for i in range(24):
                    if self.board[i] == opponent:
                        for j in range(24):
                            if self.board[j] == 0 and ((i, j) in self.connections or (j, i) in self.connections):
                                moves = True
                                break
                        if moves:
                            break
                if not moves:
                    self.game_over = True
                    self.winner = player_id
                    return