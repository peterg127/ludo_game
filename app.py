# Authors: Mário Perecz, Peter Gvozdják, Lukáš Selický
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from controllers.game_controller import GameController
from flask_socketio import SocketIO, emit
import time


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="http://localhost:8080") 
CORS(app)

players = []  # List to store players
game_controller = GameController(players)

@app.route('/update_game_mode', methods=['POST'])
def update_game_mode():
    data = request.json
    game_mode = data.get('game_mode')
    try:
        game_state = game_controller.update_game_mode(game_mode)
        return jsonify({'game_state': game_state}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/add_player', methods=['POST'])
def add_player():
    data = request.json
    player_name = data.get('name')
    player_color = data.get('color')
    try:
        if len(game_controller.game.players) >= 4:  # Check if there are already 4 players
            raise ValueError("Cannot add more than 4 players")
        game_controller.add_player(player_name, player_color)
        return jsonify({'message': 'Player added successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    
@app.route('/get_game_state', methods=['GET'])
def get_game_state():
    game_state = game_controller.get_game_state()
    return jsonify({'game_state': game_state})

@app.route('/remove_player', methods=['POST'])
def remove_player():
    data = request.json
    player_name = data.get('name')
    try:
        game_controller.remove_player(player_name)
        return jsonify({'message': 'Player removed successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    
# Initialize the game
@app.route('/init', methods=['POST'])
def init_game():
    try:
        data = request.json
        game_mode = data.get('game_mode')
        game_state = game_controller.init_game(game_mode)
        return jsonify(game_state)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/roll', methods=['POST'])
def roll_dice():
    data = request.json
    player_index = data.get('player_index')
    roll_result = game_controller.roll_dice(player_index)
    dice_value = roll_result['dice_value']
    change_turn = roll_result['change_turn']
    can_roll_again = roll_result['can_roll_again']
    can_move_piece = roll_result['can_move_piece']
    game_state = game_controller.get_game_state()
    return jsonify({'dice_value': dice_value, 'change_turn': change_turn, 'can_roll_again': can_roll_again, 'can_move_piece': can_move_piece, **game_state})


@socketio.on('move_piece')  # Listen for 'move_piece' event
def move_piece(data):
    piece_id = data.get('piece_id')
    dice_value = data.get('dice_value')
    player_index = data.get('player_index')
    val = -1
    # Perform the game logic
    update_player = False
    for i in range(1, dice_value+1):
        val = game_controller.move_piece(player_index, piece_id, dice_value, i)
        if val == False:
            update_player = True
        elif val == 2:
            game_state = game_controller.get_game_state()
            emit('update_game_state_after_move', game_state, broadcast=True)
            break
        game_state = game_controller.get_game_state()
        # Broadcast updated game state to all connected clients
        emit('update_game_state_after_move', game_state, broadcast=True)
        time.sleep(0.2)
    if update_player == True and val != 3:
        game_controller.next_turn()
        game_state = game_controller.get_game_state()
        emit('update_game_state_after_move', game_state, broadcast=True)


@app.route('/update_game_state', methods=['POST'])  # New endpoint for moving a piece
def update_game_state():
    data = request.json
    print(game_controller.game.board.state)
    updated_cells = data.get('cells')
    updated_home = data.get('home')
    current_player_index = data.get('currentPlayerIndex')
    game_controller.game.board.state = [[cell['piece']] for cell in updated_cells]
    print(updated_cells)
    print(game_controller.game.board.state)
    return jsonify({"status": "success"}), 200

@app.route('/get_random_card', methods=['POST'])
def get_random_card():
    data = request.json
    card_type = data.get('card_type')
    card_data = game_controller.get_random_card(card_type)
    return jsonify(card_data), 200
    
@app.route('/game', methods=['GET'])
def game():
    return send_from_directory(app.static_folder, 'index.html')



@app.route('/move_piece_after_card', methods=['POST'])  # New endpoint for moving a piece
def move_piece_after_card():
    data = request.json
    piece_id = data.get('piece_id')
    card_effect = data.get('card_effect')
    player_index = data.get('player_index')
    print(card_effect)
    game_controller.move_piece_after_card(player_index, piece_id, card_effect)
    game_state = game_controller.get_game_state()
    return jsonify(game_state)


chat_history = []  # In-memory store for chat messages

@app.route('/chat/history', methods=['GET'])
def get_chat_history():
    return jsonify(chat_history)

@app.route('/chat/send', methods=['POST'])
def send_chat_message():
    data = request.get_json()
    user = data.get('user')
    message = data.get('message')
    if user and message:
        chat_history.append({'user': user, 'message': message})  # Store the message
        return jsonify({'status': 'success'}), 200
    return jsonify({'status': 'error', 'message': 'Invalid input'}), 400


@app.route('/simulate_game_over', methods=['POST'])
def simulate_game_over():
    try:
        # Set all pieces of all but one player to the safe_zone position
        for player in game_controller.game.players[:-1]:
            for i, piece in enumerate(player.pieces):
                if piece.location == 'board':
                    game_controller.game.board.remove_piece_from_board(piece.position, piece)
                elif piece.location == 'home':
                    game_controller.game.board.remove_piece_from_home(piece)
                piece.location = 'safe_zone'
                piece.position = i  # Set position to a value between 0 and 3
                game_controller.game.board.move_piece_to_safe_zone(piece, i)

        game_state = game_controller.get_game_state()
        return jsonify(game_state)
    except Exception as e:
        print(f"Error in simulate_game_over: {e}")
        return jsonify({'error': str(e)}), 400



#  TEST RED
@app.route('/setup_test_state', methods=['POST'])
def setup_test_state():
    try:
        player_color = request.json.get('player_color')
        game_controller.setup_test_state(player_color)
        game_state = game_controller.get_game_state()
        return jsonify(game_state)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
if __name__ == '__main__':
    app.run(debug=True)
