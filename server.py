import socket
import json
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 12345))
server.listen(2)

board = {i: 0 for i in range(24)}  # 24 positions
players = {}
pieces = {1: 9, 2: 9}
phase = "placement"
turn = 1
mills = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8), (9, 10, 11), (12, 13, 14),
    (15, 16, 17), (18, 19, 20), (21, 22, 23),
    (0, 9, 21), (3, 10, 18), (6, 11, 15), (1, 4, 7),
    (16, 19, 22), (8, 12, 17), (5, 13, 20), (2, 14, 23)
]

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
    (3, 11),  # Extérieur -> Moyen (gauche)
    (9, 17), (12, 20), (14, 22),  # Moyen -> Intérieur (haut, droite, bas)
    (11, 19)  # Moyen -> Intérieur (gauche) - (15, 23) supprimé
]

def check_mill(player, pos):
    for mill in mills:
        if pos in mill and all(board[i] == player for i in mill):
            return True
    return False

def broadcast(state):
    # Ensure board keys are integers before sending
    state["board"] = {int(k): v for k, v in state["board"].items()}
    for client in players:
        client.send(json.dumps(state).encode())

def handle_client(client, player_id):
    client.send(str(player_id).encode())
    while True:
        try:
            data = client.recv(1024).decode()
            if not data:
                break
            action = json.loads(data)
            global board, phase, turn, pieces

            if player_id == turn:
                if action["action"] == "place" and phase == "placement":
                    pos = action["position"]
                    if board[pos] == 0:
                        board[pos] = player_id
                        pieces[player_id] -= 1
                        if check_mill(player_id, pos):
                            print(f"Joueur {player_id} a formé un moulin !")
                        turn = 3 - player_id
                        if all(p == 0 for p in pieces.values()):
                            phase = "movement"
                elif action["action"] == "move" and phase == "movement":
                    from_pos = action["from"]
                    to_pos = action["to"]
                    if board[from_pos] == player_id and board[to_pos] == 0:
                        if (from_pos, to_pos) in CONNECTIONS or (to_pos, from_pos) in CONNECTIONS:
                            board[from_pos] = 0
                            board[to_pos] = player_id
                            if check_mill(player_id, to_pos):
                                print(f"Joueur {player_id} a formé un moulin !")
                            turn = 3 - player_id

                winner = None
                opponent = 3 - player_id
                if phase == "movement":
                    opponent_pieces = sum(1 for v in board.values() if v == opponent)
                    if opponent_pieces < 3:
                        winner = player_id
                    moves = False
                    for i in range(24):
                        if board[i] == opponent:
                            for j in range(24):
                                if board[j] == 0 and ((i, j) in CONNECTIONS or (j, i) in CONNECTIONS):
                                    moves = True
                                    break
                            if moves:
                                break
                    if not moves:
                        winner = player_id

                state = {"board": board, "phase": phase, "turn": turn}
                if winner:
                    state["winner"] = winner
                broadcast(state)

        except:
            break
    client.close()

def main():
    print("Serveur démarré...")
    client_id = 1
    while len(players) < 2:
        client, addr = server.accept()
        players[client] = client_id
        threading.Thread(target=handle_client, args=(client, client_id)).start()
        client_id += 1

if __name__ == "__main__":
    main()
