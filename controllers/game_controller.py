from models.game import Game

pos_to_be = 0
class GameController:
    def __init__(self, players):
        self.game = Game(players)
        self.num_of_rolls = 0
        self.max_dice_rolls = 1  # Default value
        self.players_added = len(players)

    def update_game_mode(self, game_mode):
        self.game.game_mode = game_mode
        return self.get_game_state()

    def add_player(self, name, color):
        if self.players_added >= 4:
            raise ValueError("Cannot add more than 4 players")
        if color not in ['red', 'yellow', 'green', 'blue']:
            raise ValueError(f"Invalid color: {color}")
        if any(player.color == color for player in self.game.players):
            raise ValueError(f"Color {color} is already taken.")
        self.game.add_player(name, color)
        self.players_added += 1

    def remove_player(self, name):
        player = next((player for player in self.game.players if player.name == name), None)
        if not player:
            raise ValueError(f"Player {name} not found.")
        self.game.players.remove(player)
        self.players_added -= 1
        
        # Update player indexes
        for index, player in enumerate(self.game.players):
            player.index = index

    def init_game(self, game_mode):
        if self.players_added < 2:
            raise ValueError("At least 2 players are required to start the game")
        self.game.init_board(game_mode)
        for player in self.game.players:
            player.total_moves = 0  # Reset total moves for each player
            for piece in player.pieces:
                piece.location = 'home'
                piece.position = piece.id
                self.game.board.home[player.color][piece.id] = piece
                piece.move_counter = 0
        self.current_turn = 0
        self.game.dice.value = 0
        self.game.game_mode = game_mode  # Set the game mode
        return self.get_game_state()

    def move_piece(self, player_index, piece_id, dice_roll, i):
        global pos_to_be
        if dice_roll is None:   # If dice_roll is None, it means the player has not rolled the dice
            return True

        if player_index != self.game.current_turn:
            return True
        player = self.game.players[player_index] # Get the current player
        piece = player.pieces[piece_id] # Get the piece to move
        current_location = piece.location
        current_position = piece.position
        if i == 1:
            pos_to_be = current_position + dice_roll
            if current_location != 'safe_zone':
                if piece.can_move_to_safe_zone(dice_roll):
                    pos_to_be %= 10
                else:
                    pos_to_be %= 40
        # moving piece to start
        if current_location == 'home':
            if dice_roll == 6:
                self.game.board.move_piece_to_start(piece)
                self.game.board.remove_piece_from_home(piece)
                self.num_of_rolls = 0
                player.increment_moves()  # Increment the total moves
                return 2
            else:
                return True

        # calculating new position
        new_position = current_position + 1

        if current_location == 'board':
            if piece.can_move_to_safe_zone(1):
                new_position %= 10
                if pos_to_be > 3: # can move to safe zone but would be out of bounds
                    if dice_roll == 6:
                        self.num_of_rolls = 0
                    return True
                if self.game.board.safe_zone[piece.color][pos_to_be] is not None:
                    return True
                self.game.board.remove_piece_from_board(current_position, piece)
                self.game.board.move_piece_to_safe_zone(piece, new_position)
            else:
                new_position %= 40
                # Check if there is already a piece with another color at the new position
                occupying_pieces = self.game.board.state[pos_to_be]
                for occupying_piece in occupying_pieces:
                    if occupying_piece and occupying_piece.color != piece.color:
                        if new_position == pos_to_be:
                            self.game.board.remove_piece_from_board(new_position, occupying_piece)
                            occupying_piece.move_counter = 0
                            self.game.board.move_piece_to_home(occupying_piece)
                self.game.board.remove_piece_from_board(current_position, piece)
                self.game.board.move_piece_on_board(piece, new_position)
        elif current_location == 'safe_zone':
            if pos_to_be >= 4:
                return True
            if self.game.board.safe_zone[piece.color][pos_to_be] is not None:
                return True
            self.game.board.remove_piece_from_safe_zone(piece)
            self.game.board.move_piece_on_safe_zone(piece, new_position)

        # update the piece
        piece.increment_move_counter(1)
        player.increment_moves()  # Increment the total moves

        # Check if the player has finished the game
        if self.game.has_all_pieces_at_safe_zone(player) and player.finished_order is None:
            player.finished_order = len([player for player in self.game.players if player.finished_order is not None]) + 1

        if dice_roll == 6:
            self.num_of_rolls = 0
            return True
        if (piece.position in self.game.board.special_squares_blesed):
            return 3
        return False
        #self.next_turn()

    def next_turn(self):
        self.num_of_rolls = 0  # Reset the dice rolls count for the next player
        self.game.next_turn()
        self.update_current_player()

    def roll_dice(self, player_index):
        all_pieces_home = False
        can_roll_again = False
        can_move_piece = False

        # if player_index != self.game.current_turn:
        #     print('Not your turn')
        #     return None

        dice_value = self.game.roll_dice()
        if self.has_all_pieces_home(player_index):
            print('All pieces are home')
            all_pieces_home = True
            self.max_dice_rolls = 3
        else:
            self.max_dice_rolls = 1
            all_pieces_home = False

        if dice_value == 6:
            self.num_of_rolls = 0
            can_roll_again = True
            can_move_piece = self.can_move_piece(player_index)
            return {'dice_value': dice_value, 'change_turn': False,'can_roll_again': can_roll_again, 'can_move_piece': can_move_piece}
            
        if all_pieces_home:
            self.num_of_rolls += 1
        
        print('hodil som')
        print(self.num_of_rolls, self.max_dice_rolls)
        if self.num_of_rolls >= self.max_dice_rolls:
            print('Next turn')
            print('hodil som vela krat')
            self.next_turn()
            return {'dice_value': 0, 'change_turn': True,'can_roll_again': can_roll_again, 'can_move_piece': can_move_piece}
            
        if not all_pieces_home:
            self.num_of_rolls += 1

        can_move_piece = self.can_move_piece(player_index)
        return {'dice_value': dice_value, 'change_turn': False,'can_roll_again': can_roll_again, 'can_move_piece': can_move_piece}

    def get_game_state(self):
        game_state = self.game.get_game_state()
        game_over = any(self.game.has_all_pieces_at_safe_zone(player) for player in self.game.players)
        game_state['game_over'] = game_over
        if game_over:
            game_state['winner'] = next(player.name for player in self.game.players if self.game.has_all_pieces_at_safe_zone(player))
        return game_state

    def has_all_pieces_home(self, player_index):
        for piece in self.game.players[player_index].pieces:
            if piece.location != 'home':
                return False
        return True
    
    def update_current_player(self):
        self.current_player = self.game.get_current_player().color


    def move_piece_after_card(self,player_index, piece_id, card_effect):
        player = self.game.players[player_index]
        piece = player.pieces[piece_id]
        current_position = piece.position
        new_position = current_position + card_effect
        piece.increment_move_counter(card_effect)
        self.game.board.move_piece_on_board(piece, new_position)

    def get_random_card(self, card_type):
        return self.game.get_random_card(card_type)

    #  TEST Works for red only change piece move counter for others
    def setup_test_state(self, player_color):
        player = next(player for player in self.game.players if player.color == player_color)
        
        # Clear the board state for the player
        for piece in player.pieces:
            if piece.location == 'board':
                self.game.board.remove_piece_from_board(piece.position, piece)
            elif piece.location == 'home':
                self.game.board.remove_piece_from_home(piece)
            elif piece.location == 'safe_zone':
                self.game.board.remove_piece_from_safe_zone(piece)
        
        # Place three pieces in the safe zone
        for i in range(3):
            piece = player.pieces[i]
            piece.location = 'safe_zone'
            piece.position = i
            piece.move_counter = 40 + i  # Update move counter to reflect the position in the safe zone
            self.game.board.move_piece_to_safe_zone(piece, i)
        
        # Place one piece near the safe zone
        piece = player.pieces[3]
        self.game.board.move_piece_to_start(piece)
        self.game.board.move_piece_on_board(piece, 39)
        piece.move_counter = 39  # Update move counter to reflect the position in the home cell
        
        # Update the game state
        self.update_current_player()
        return self.get_game_state()

    def can_move_piece(self, player_index):
        player = self.game.players[player_index]
        for piece in player.pieces:
            if piece.location != 'home':
                return True
        return False
