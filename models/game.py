import random

from .board import Board
from .cards import Card, blessed_cards, cursed_cards
from .dice import Dice
from .player import Player


class Game:
    def __init__(self, players):
        self.players = [Player(player['color'], i, player['name']) for i, player in enumerate(players)]
        self.board = Board([player['color'] for player in players])
        self.dice = Dice()
        self.current_turn = 0
        self.game_mode = None

    def add_player(self, name, color):
        if any(player.color == color for player in self.players):
            raise ValueError(f"Color {color} is already taken.")
        turn_order = len(self.players)
        player = Player(color, turn_order, name)
        self.players.append(player)

    def init_board(self, game_mode):
        player_colors = [player.color for player in self.players]
        self.board = Board(player_colors)
        self.game_mode = game_mode

    def next_turn(self):
        self.current_turn = (self.current_turn + 1) % len(self.players)

    def get_current_player(self):
        if not self.players:
            return None
        return self.players[self.current_turn]

    def roll_dice(self):
        return self.dice.roll()

    def has_all_pieces_at_safe_zone(self, player):
        return all(piece.location == 'safe_zone' for piece in player.pieces)

    def has_all_pieces_at_home(self, player):
        if player == None:
            return None
        return all(piece.location == 'home' for piece in player.pieces)

    def get_game_state(self):
        current_player = self.get_current_player()
        game_over = False
        winner = None
        all_pieces_at_home = self.has_all_pieces_at_home(current_player)
        if game_over:
            winner = next((player.name for player in self.players if self.has_all_pieces_at_safe_zone(player)), None)

        # Sort players by finished_order
        sorted_players = sorted(self.players, key=lambda player: (player.finished_order is None, player.finished_order))

        return {
            'current_turn': self.current_turn,
            'current_player': current_player.color if current_player else None,
            'special_squares': self.board.special_squares_blesed,
            'all_pieces_at_home': all_pieces_at_home,
            'board_state': [
                {
                    'piece': {
                        'id': piece.id,
                        'location': piece.location,
                        'position': piece.position,
                        'piece_color': piece.color,
                        'move_counter': piece.move_counter, 
                    } if piece else None  # If there’s a piece, include details; otherwise None
                    for piece in cell  # Loop over the pieces in the cell
                }
                for cell in self.board.state  # Loop over the 40 cells
            ],
            'home_state': {
                color: [
                    {
                        'id': piece.id,
                        'location': piece.location,
                        'position': piece.position,
                        'piece_color': piece.color,
                    } if piece else None
                    for piece in pieces
                ]
                for color, pieces in self.board.home.items()
            },
            'safe_zone': {
                color: [
                    {
                        'id': piece.id,
                        'location': piece.location,
                        'position': piece.position,
                        'piece_color': piece.color,
                    } if piece else None
                    for piece in pieces
                ]
                for color, pieces in self.board.safe_zone.items()
            },
            'players': [
                {
                    'color': player.color,
                    'turn_order': player.turn_order,
                    'name': player.name,
                    'total_moves': player.total_moves,
                    'finished_order': player.finished_order,  # Include finished_order
                    'pieces': [
                        {
                            'id': piece.id,
                            'location': piece.location,
                            'position': piece.position
                        }
                        for piece in player.pieces
                    ]
                }
                for player in sorted_players  
            ],
            'game_over': game_over,
            'winner': winner,
            'game_mode': self.game_mode,  
        }

    def get_random_card(self, card_type):
        game_state = self.get_game_state()
        if card_type == 'blessed':  # move forward by X squares
            random_card = random.choice(blessed_cards)
            random_card.effect = random.randint(1, 3)
            random_card.change_text()
        else:
            random_card = random.choice(cursed_cards)
            if random_card.id == 4:  # go back home
                random_card.effect = 'skip'
                previous_turn = (self.current_turn - 1) % len(self.players)
                previous_player_color = self.players[previous_turn].color
                for square in self.board.special_squares_blesed:
                    if len(self.board.state[square]) == 2 and self.board.state[square][1].color ==  self.players[self.current_turn].color:
                        piece = self.board.state[square][1]
                        print("Piece move color", piece.color)
                        self.board.move_piece_to_home(piece)
                        self.board.remove_piece_from_board(square, piece)
                game_state = self.get_game_state()
            elif random_card.id == 5:  # move back by X squares
                random_card.effect = random.randint(-3, -1)
                random_card.change_text()
        print(random_card.id)
        print(random_card.name)
        print(random_card.effect)
        return {
            "id": random_card.id,
            "name": random_card.name,
            "effect": random_card.effect,
            **game_state
        }