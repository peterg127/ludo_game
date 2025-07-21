from .piece import Piece
from .player import Player


class Board:
    def __init__(self, player_colors):
        self.state = [[None] for _ in range(40)]  # Initialize the board state
        
        # Initialize the start, safe_zone, and home locations for each player
        self.safe_zone = {color: [None] * 4 for color in player_colors} # when fills, player wins
        
        self.home = {color: [None] * 4 for color in player_colors}
        self.special_squares_blesed = [1, 2,3,4,5,6]
        # Initialize the start positions for each player
        self.start_positions = self.get_start_positions(player_colors)

    # Initialize the start locations for each player
    
    def get_start_positions(self, player_colors):
        base_positions = {
            'red' : 0,
            'green' : 10,
            'yellow' : 20,
            'blue' : 30
        }
        start_positions = {}
        for color in player_colors:
            start_positions[color] = base_positions[color]
        return start_positions
    
    def move_piece_to_start(self, piece):
        start_position = self.start_positions[piece.color]
        piece.location = 'board'
        piece.position = start_position
        self.state[start_position].append(piece)
    
    def move_piece_to_home(self, piece):
        piece.location = 'home'
        piece.position = piece.id
        self.home[piece.color][piece.id] = piece

    def move_piece_to_safe_zone(self, piece, position):
        piece.location = 'safe_zone'
        piece.position = position
        self.safe_zone[piece.color][position] = piece

    def move_piece_on_board(self, piece, new_position):        
        old_position = piece.position
        if piece in self.state[old_position]:
            self.state[old_position].remove(piece)
        else:
            print(f"Piece {piece.id} not found in position {old_position}")
        
        new_position %= 40

        piece.position = new_position
        self.state[new_position].append(piece)

    def move_piece_on_safe_zone(self, piece, new_position):
        piece.position = new_position
        self.safe_zone[piece.color][piece.position] = piece

    def remove_piece_from_safe_zone(self, piece):
        self.safe_zone[piece.color][piece.position] = None
        
    def remove_piece_from_home(self, piece):
        self.home[piece.color][piece.id] = None
    
    def remove_piece_from_board(self, position, piece):
        self.state[position].remove(piece)
        