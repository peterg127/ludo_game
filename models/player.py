from .piece import Piece


class Player:
    def __init__(self, color, turn_order, name):
        self.color = color
        self.turn_order = turn_order
        self.name = name
        self.pieces = [Piece(color=color, id=i, location='home', position=None) for i in range(4)]
        self.total_moves = 0  
        self.finished_order = None

    def increment_moves(self):
        self.total_moves += 1