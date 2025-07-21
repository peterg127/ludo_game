<!-- Authors: Mário Perecz, Peter Gvozdják -->
<template>
  <BaseLayout>      
    <div class="cards">
      <div class="card-options" v-if="isSpecialGameMode">
        <h2>Cards</h2>
        <button @click="clickCard('blessed')" :disabled="cardsDisabled_b">Blessed</button>
        <button @click="clickCard('cursed')" :disabled='cardsDisabled_c'>Cursed</button>
      </div>
    </div>
      <div class="ludo-board">
        <div class="return-button-container">
        <ReturnButton to="LudoMenu"></ReturnButton>
      </div>
        <div class="current-player">
          <h2>Current Player: {{ currentPlayer }}</h2>
        </div>
        <div class="boardContainer">
          <template v-for="(colorGroup, color) in home" :key="color">
            <div v-for="(piece, index) in colorGroup" :key="`${color}-${index}`" :class="`cell cell-${color}-${index}`">
              <div v-if="piece && piece.id != null" class="piece" :style="getPieceStyle(piece)" @click.stop="selectPiece(piece)">
              </div>
            </div>
            <div :class="`cell cell-${color}-player-name`">
              <span v-for="player in getPlayersByColor(color)" :key="player.name" class="player-name">
                {{ player.name }}
                <div v-if="currentPlayerColor === color" 
                     class="dice-result" 
                     :class="{ 'disabled_dice': !canRollDice }"
                     :style="positionDiceByPlayerColor(color)"
                     @click="rollDice">
                  <img v-if="diceValue !== null && diceValue >= 1 && diceValue <= 6" :src="require(`@/assets/dice-six-faces-${diceValue}.png`)" :alt="diceValue" class="dice-value-img" />
                  <img v-else :src="require('@/assets/dice-six-faces-0.png')" alt="1" class="dice-value-img" />
                </div>
              </span>
            </div>
          </template>
          <template v-for="color in ['red', 'yellow', 'green', 'blue']" :key="color">
          <div v-for="index in 4" :key="`${color}-${index}`" :class="`cell cell-${color}-safe-${index-1}`">
            <div v-if="safe_zone[color] && safe_zone[color][index-1] && safe_zone[color][index-1].id != null" class="piece" :style="getPieceStyle(safe_zone[color][index-1])" @click.stop="selectPiece(safe_zone[color][index-1])">
            </div>
          </div>
        </template>
          <div v-for="(cell, index) in cells"
            :key="index"
            :class="[
              `cell cell${index}`, 
              specialSquares.includes(index) ? '' : ''
            ]"
            :style="specialSquares.includes(index) ? getSpecialsquareStyle() : {}" 
          >
            <div v-if="cell && cell.piece" class="piece" :style="getPieceStyle(cell.piece)" @click.stop="selectPiece(cell.piece)">
            </div>
          </div>
        </div>
        <div v-if="showCardPopup" class="card-popup">
          <div class="card-details">
            <h2>{{ this.cardDetails }}</h2>
            <button @click="ConfirmCard">Confirm</button>
          </div>
        </div>
        
        <LudoStatistics
          :show="showStatistics"
          :winner="winner"
          :players="players"
          @close="handleRestart"
        />
        <button @click="simulateGameOver">Simulate Game Over</button>
        <button @click="setupTestState">Setup Test State</button>
      </div>
      <ChatBox />
  </BaseLayout>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';
import ChatBox from './ChatBox.vue';
import LudoStatistics from './LudoStatistics.vue';
import BaseLayout from './BaseLayout.vue';
import ReturnButton from './ReturnButton.vue';
import io from 'socket.io-client';

export default {
  name: 'LudoBoard',
  components: {
    ChatBox,
    LudoStatistics,
    BaseLayout,
    ReturnButton
  },
  data() {
    return {
      cells: Array(40).fill({ piece: null }), // Initialize 121 cells with no pieces
      
      home: {
        red: Array(4).fill({ piece: null }), // Initialize 4 home squares for red pieces
        blue: Array(4).fill({ piece: null }), // Initialize 4 home squares for blue pieces
        green: Array(4).fill({ piece: null }), // Initialize 4 home squares for green pieces
        yellow: Array(4).fill({ piece: null }), // Initialize 4 home squares for yellow pieces
      },

      safe_zone: {
        red: Array(4).fill({ piece: null }), // Initialize 4 home squares for red pieces
        blue: Array(4).fill({ piece: null }), // Initialize 4 home squares for blue pieces
        green: Array(4).fill({ piece: null }), // Initialize 4 home squares for green pieces
        yellow: Array(4).fill({ piece: null }), // Initialize 4 home squares for yellow pieces
      },

      diceValue: null, // Store the dice value
      diceRolled: false, // Flag to track if the dice has been rolled
      isFirstRoll: true, // Flag to track if it's the first roll
      selectedPieceId: -1, // Track selected piece ID
      currentPlayer: '', // Track the current player
      currentPlayerIndex: 0, // Track the current player index
      specialSquares: [], // Example indices for special squares
      showCardPopup: false, // Flag to control popup visibility
      selectedCard: null,
      cardsDisabled_b: true,    //blessed
      cardsDisabled_c: true,     //cursed
      effect: 0,      // effect of card
      moveForwardActivated: false, 
      cardDetails: '',
      // Statistics 
      showStatistics: false, // Flag to control the visibility of the game over modal
      canRollDice: true,
      winner: '', // Store the winner's name
      players: [], // Initialize the players array
    };
  },
  created() {
    // Initialize socket connection
    this.socket = io('http://localhost:5000');

    // Listen for updated game state
    
  },
  computed: {
    ...mapGetters(['getGameState']),
    isSpecialGameMode() {
      return this.getGameState?.game_mode === 'special';
    },
    getPlayersByColor() {
      return (color) => {
        return this.players.filter(player => player.color === color);
      };
    },
    currentPlayerColor() {
      return this.players[this.currentPlayerIndex]?.color;
    }
  },
  methods: {
    ...mapActions(['fetchGameState']),
    getPieceStyle(piece) {
      const imageUrl = require(`@/assets/${piece.piece_color}piece.png`);
      return {
        backgroundImage: `url(${imageUrl})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        };
    },
    getSpecialsquareStyle(){
    const imageUrl = require(`@/assets/star.png`);
      return {
        backgroundImage: `url(${imageUrl})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        };
    },
    async clickCard(cardType) {
      this.selectedCard = cardType;
      try {
        // Fetch card details from backend
        const response = await fetch("http://localhost:5000/get_random_card", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ card_type: cardType }),
        });
        const data = await response.json();
        this.cardDetails = data.name; // Save card details (name, description, etc.)
        this.effect = data.effect;
        this.diceValue = data.dice_value;
        this.cells = data.board_state; // Update cells based on the new board state
        this.home = data.home_state; // Update home squares based on home state
        this.currentPlayer = data.current_player; // Update the current player
        this.currentPlayerIndex = data.current_turn;
        this.showCardPopup = true; // Show popup with fetched data
        this.selectedCard = cardType;
        console.log("CArd details: ", this.effect);
      } catch (error) {
        console.error("Error fetching card details:", error);
      }
    },
    ConfirmCard() {
    this.showCardPopup = false; // Hide the popup
    this.cardsDisabled_b = true; // Re-disable the cards after using
    this.cardsDisabled_c = true;
    this.moveForwardActivated = true; // Activate the "move forward" effect
    if (this.effect == 'skip'){
      console.log("Aktualne novy: ", this.currentPlayer);
      console.log("SKIPUJEME a rolujeme", this.effect);
      this.moveForwardActivated = false;            // dont do extra move
      //this.rollDice();
    }
    console.log("Move forward effect activated");
    
    // Add logic based on selected card, e.g., granting extra turn, skipping opponent, etc.
  },
  async rollDice() {
    try {
      const response = await fetch('http://localhost:5000/roll', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          player_index: this.currentPlayerIndex,
        }),
      });
      const data = await response.json();
      this.diceValue = data.dice_value; // Set the dice value from the response
      this.cells = data.board_state; // Update cells based on the new board state
      this.home = data.home_state; // Update home squares based on home state
      this.currentPlayer = data.current_player; // Update the current player
      this.currentPlayerIndex = data.current_turn; // Update the current player index
      this.all_pieces_at_home = data.all_pieces_at_home;
      this.canRollDice = false;
      this.diceRolled = true; // Set the diceRolled flag to true
      console.log("data after roll before change turn", data);
      if (data.change_turn) {
        this.isFirstRoll = true;
      }
      
      if (this.isFirstRoll) {
          this.canRollDice = true;
          this.isFirstRoll = false;
        } else {
          // Check if the player can move a piece
          if (data.can_move_piece) {
            this.canRollDice = false;
          } else if (data.can_roll_again || this.all_pieces_at_home) {
            this.canRollDice = true;
          }
        }
      

    } catch (error) {
      console.error('Error rolling dice:', error);
    }
  },
  async move_piece_after_card(pieceId) {
    try {
      // Implement the forward move logic
      console.log("V move after card effect", this.effect);
      const response = await fetch('http://localhost:5000/move_piece_after_card', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          piece_id: pieceId,
          card_effect: this.effect,
          player_index: this.currentPlayerIndex,
        }),
      });
      const data = await response.json();
      this.cells = data.board_state;
      this.home = data.home_state;
      this.currentPlayer = data.current_player;
      this.currentPlayerIndex = data.current_turn;
      console.log(this.cells);
      // Reset the "move forward" effect after use
      this.moveForwardActivated = false; 
      console.log(`Piece ${pieceId} moved forward by  steps`);
    } catch (error) {
      console.error('Error moving piece forward:', error);
    }
      },

async movePiece(piece) {
  if (!this.diceRolled) {
    console.log("Roll the dice first");
    return;
  }

  try {
    let pieceId = piece.id;
    const oldIndex = piece.position; // Store the current index of the piece
    console.log("Old Position Index: ", oldIndex);

    // Define the callback function for handling game state updates
    const handleGameStateUpdate = (data) => {
      // Update the client's game state based on the server response
      this.cells = data.board_state;
      this.home = data.home_state;
      this.specialSquares = data.special_squares;
      this.safe_zone = data.safe_zone;
      this.players = data.players;
      this.showStatistics = data.game_over;
      this.winner = data.winner;
      this.diceRolled = false;
      this.diceValue = null;
      this.cardsDisabled_b = true;
      this.cardsDisabled_c = true;
      let specialSquareOccupied = false;
      for (let square of this.specialSquares) {
        const cell = this.cells[square];
        if (cell && cell.piece !== null) {
          const piece = cell.piece;
          console.log("CURRENT PLAYER", this.currentPlayer);
          console.log("PIECE: ", piece);
          if (piece.piece_color === this.currentPlayer && piece.id === pieceId) {
            specialSquareOccupied = true;
            break;
          }
        }
      }

      if (specialSquareOccupied) {
        console.log("Special square occupied. Current player's turn is not updated.");
        const randomChoice = Math.random() < 0.5;
        this.cardsDisabled_b = randomChoice;
        this.cardsDisabled_c = !randomChoice;
      } else {
        this.currentPlayer = data.current_player; // Update the current player
        this.currentPlayerIndex = data.current_turn;
      }

      this.players = data.players; // Update the players array
      this.showStatistics = data.game_over; // Update the showStatistics flag
      this.winner = data.winner;

      this.canRollDice = true; // After piece is moved, you can roll again

      console.log("Board state after move:", this.cells);
      console.log("Player after move:", data.players);
      console.log("Home state after move:", this.home);
      console.log("Safe zone after move:", this.safe_zone);
      console.log("Current player after move:", this.currentPlayer);
      console.log("Dice roll after move:", this.diceValue);

      // Unregister the listener once the update is processed
      //this.socket.off('update_game_state_after_move', handleGameStateUpdate);
    };

    // Register the listener for this move
    this.socket.on('update_game_state_after_move', handleGameStateUpdate);

    // Emit the move_piece event to the server
    this.socket.emit('move_piece', {
      piece_id: pieceId,
      dice_value: this.diceValue,
      card_effect: 3, // Pass any relevant card effects
      player_index: this.currentPlayerIndex,
    });
  } catch (error) {
    console.error("Error during movePiece:", error);
  }
},
    selectPiece(piece) {
      console.log("SOMTU po seleckte piecu" , piece);
      console.log("Flag: ",this.moveForwardActivated);
      console.log("Current player: ", this.players);
      console.log("Curent player: ", this.currentPlayer);
      console.log("Piece color:  ",piece.color);
      if (this.moveForwardActivated && piece.piece_color == this.currentPlayer){
        console.log("Volam move_piece_after_card");

        this.move_piece_after_card(piece.id);
      }
      else if (piece.piece_color == this.currentPlayer) {
        this.movePiece(piece);
      }
    },
    async simulateGameOver() {
      try {
        const response = await fetch('http://localhost:5000/simulate_game_over', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        const data = await response.json();
        // Update your component state based on the response
        this.fetchActualState(data);
        console.log('Game state after simulation:', data);
      } catch (error) {
        console.error('Error simulating game over:', error);
      }
    },
    async setupTestState() {
      try {
        const response = await fetch('http://localhost:5000/setup_test_state', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            player_color: this.currentPlayerColor,
          }),
        });
        const data = await response.json();
        this.fetchActualState(data, true);
        console.log('Game state after setting up test state:', data);
      } catch (error) {
        console.error('Error setting up test state:', error);
      }
    },
    fetchActualState(gameState) {
      this.cells = gameState.board_state;
      this.home = gameState.home_state;
      this.safe_zone = gameState.safe_zone;
      this.currentPlayer = gameState.current_player;
      this.currentPlayerIndex = gameState.current_turn;
      this.specialSquares = gameState.special_squares;
      this.players = gameState.players;
      this.showStatistics = gameState.game_over;
      this.winner = gameState.winner;
    },
    handleRestart(gameState) {
        this.showStatistics = false;
        this.fetchActualState(gameState);
    },
    positionDiceByPlayerColor(color) {
      switch (color) {
        case 'red':
          return { bottom: '25%', left: '115%' };
        case 'green':
          return { top: '25%', left: '115%' };
        case 'yellow':
          return { top: '25%', right: '115%' };
        case 'blue':
          return { bottom: '25%', right: '115%' };
        default:
          return { top: '50%', left: '50%' };
      }
    }
  },
    async mounted() {
      await this.fetchGameState(); // Fetch the game state when the component is mounted
      this.fetchActualState(this.getGameState); // Update the component state with the fetched game state
    }
};
</script>

<style scoped>
.ludo-board-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  width: 100%;
  padding: 1rem;
  box-sizing: border-box;
}

.ludo-board {
  width: 100%; /* Take the available column width */
  max-width: 700px; /* Optional: Limit the width of the board */
  text-align: center; /* Center text alignment (optional) */
  display: flex;
  flex-direction: column; /* Stack children vertically */
  align-items: center; /* Center children horizontally */
  margin: auto; /* Ensure it's centered within its grid area */
}

.cards {
  display: flex;
  justify-content: center;  /* Center the content horizontally */
  align-items: center;      /* Center the content vertically */
  text-align: center;       /* Ensure the text is centered */
  height: 100%;             /* Make the div take full height of the grid cell */
}

.current-player {
  display: inline-block; /* Keeps the element inline while respecting dimensions */
  background-color: #eee0b6; /* Matches the light yellow background */
  padding: 1px 10px; /* Adds more consistent spacing around the text */
  border-radius: 5px; /* Smoothens the corners */
  font-family: Arial, sans-serif; /* Matches the font in the desired look */
  font-size: 16px; /* Adjusts the text size to be more visible */
  font-weight: bold; /* Makes the text bold */
  color: black; /* Ensures text color is readable */
  text-align: center; /* Centers the text within the block */
}

.roll-dice {
  margin-top: 20px; /* Adds space between the current player and the button */
}

.boardContainer {
  display: grid;
  grid-template-columns: repeat(11, 50px); /* Create a grid of 11 columns */
  grid-template-rows: repeat(11, 50px); /* Create a grid of 11 rows */
  border: 1px solid #000;
  position: relative; /* Add relative positioning to the board container */
}

.boardContainer > div {
  position: relative;
  outline: 1px solid #000; /* Optional: Add borders to cells */
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--cell-bg-color, white); /* Default is white */
}
.dice-result {
  margin: 0; 
  outline: none !important;
  border-radius: 50%;
  position: absolute; /* Use absolute positioning */
}
.dice-value-img {
  height: 70px;

}

.cell0 { grid-column: 5; grid-row: 11;}
.cell1 { grid-column: 5; grid-row: 10;}
.cell2 { grid-column: 5; grid-row: 9; }
.cell3 { grid-column: 5; grid-row: 8; }
.cell4 { grid-column: 5; grid-row: 7; }
.cell5 { grid-column: 4; grid-row: 7; }
.cell6 { grid-column: 3; grid-row: 7; }
.cell7 { grid-column: 2; grid-row: 7; }
.cell8 { grid-column: 1; grid-row: 7; }
.cell9 { grid-column: 1; grid-row: 6; }
.cell10 { grid-column: 1; grid-row: 5;}
.cell11 { grid-column: 2; grid-row: 5; }
.cell12 { grid-column: 3; grid-row: 5; }
.cell13 { grid-column: 4; grid-row: 5; }
.cell14 { grid-column: 5; grid-row: 5; }
.cell15 { grid-column: 5; grid-row: 4; }
.cell16 { grid-column: 5; grid-row: 3; }
.cell17 { grid-column: 5; grid-row: 2; }
.cell18 { grid-column: 5; grid-row: 1; }
.cell19 { grid-column: 6; grid-row: 1; }
.cell20 { grid-column: 7; grid-row: 1; }
.cell21 { grid-column: 7; grid-row: 2; }
.cell22 { grid-column: 7; grid-row: 3; }
.cell23 { grid-column: 7; grid-row: 4; }
.cell24 { grid-column: 7; grid-row: 5; }
.cell25 { grid-column: 8; grid-row: 5; }
.cell26 { grid-column: 9; grid-row: 5; }
.cell27 { grid-column: 10; grid-row: 5; }
.cell28 { grid-column: 11; grid-row: 5; }
.cell29 { grid-column: 11; grid-row: 6; }
.cell30 { grid-column: 11; grid-row: 7; }
.cell31 { grid-column: 10; grid-row: 7; }
.cell32 { grid-column: 9; grid-row: 7; }
.cell33 { grid-column: 8; grid-row: 7; }
.cell34 { grid-column: 7; grid-row: 7; }
.cell35 { grid-column: 7; grid-row: 8; }
.cell36 { grid-column: 7; grid-row: 9; }
.cell37 { grid-column: 7; grid-row: 10; }
.cell38 { grid-column: 7; grid-row: 11; }
.cell39 { grid-column: 6; grid-row: 11; } 

.cell0::before {
  content: '';
  position: absolute;
  width: 20px;
  height: 10px;
  background-color: red;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) rotate(90deg); /* Center the rectangle */
  z-index: 1;
}

.cell0::after {
  content: '';
  position: absolute;
  width: 0;
  height: 0;
  border-left: 10px solid transparent;
  border-right: 10px solid transparent;
  border-top: 10px solid red;
  top: calc(50% - 5px); /* Adjust the position to align with the rectangle */
  left: 50%;
  transform: translate(-50%, -100%) rotate(180deg); /* Center the triangle and position it above the rectangle */
  z-index: 1;
}

.cell10::before {
  content: '';
  position: absolute;
  width: 20px;
  height: 10px;
  background-color: green;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%); /* Center the rectangle */
  z-index: 1;
}

.cell10::after {
  content: '';
  position: absolute;
  width: 0;
  height: 0;
  border-top: 10px solid transparent;
  border-bottom: 10px solid transparent;
  border-left: 10px solid green;
  top: 50%; /* Position the triangle relative to the rectangle */
  left: calc(50% + 10px); /* Position it right of the rectangle */
  transform: translate(-50%, -50%); /* Rotate the triangle to point right */
  z-index: 1;
}

.cell20::before {
  content: '';
  position: absolute;
  width: 20px;
  height: 10px;
  background-color: yellow;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) rotate(90deg); /* Center the rectangle */
  z-index: 1;
}

.cell20::after {
  content: '';
  position: absolute;
  width: 0;
  height: 0;
  border-left: 10px solid transparent;
  border-right: 10px solid transparent;
  border-top: 0;
  border-bottom: 10px solid yellow;
  top: calc(50% + 5px); /* Position the triangle below the rectangle */
  left: 50%;
  transform: translateX(-50%) rotate(180deg); /* Center the triangle and rotate it to point down */
  z-index: 1;
}

.cell30::before {
  content: '';
  position: absolute;
  width: 20px;
  height: 10px;
  background-color: blue;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%); /* Center the rectangle */
  z-index: 1;
}

.cell30::after {
  content: '';
  position: absolute;
  width: 0;
  height: 0;
  border-left: 10px solid transparent;
  border-right: 10px solid transparent;
  border-top: 10px solid blue;
  left: calc(50% - 10px);
  top: calc(50% + 5px); 
  transform: translate(-50%, -100%) rotate(90deg); /* Center the triangle and position it above the rectangle */
  z-index: 1;
}

/* Green home cells */
.cell-green-0 { 
  grid-column: 1; 
  grid-row: 1;
  --cell-bg-color: green;
}
.cell-green-1 { 
  grid-column: 2; 
  grid-row: 1; 
  --cell-bg-color: green;
}
.cell-green-2 { 
  grid-column: 1; 
  grid-row: 2; 
  --cell-bg-color: green;
}
.cell-green-3 { 
  grid-column: 2; 
  grid-row: 2; 
  --cell-bg-color: green;
}

.cell-green-player-name { 
  grid-column: 1 / span 2; 
  grid-row: 3; 
  --cell-bg-color: #fdf293;
  outline: none !important;
  border-top: 1px solid black;
}

/* Yellow home cells */
.cell-yellow-0 { 
  grid-column: 10; 
  grid-row: 1; 
  --cell-bg-color: yellow;
}
.cell-yellow-1 { 
  grid-column: 11; 
  grid-row: 1; 
  --cell-bg-color: yellow;
}
.cell-yellow-2 { 
  grid-column: 10; 
  grid-row: 2; 
  --cell-bg-color: yellow;
}
.cell-yellow-3 { 
  grid-column: 11; 
  grid-row: 2; 
  --cell-bg-color: yellow;
}

.cell-yellow-player-name { 
  grid-column: 10 / span 2; 
  grid-row: 3; 
  --cell-bg-color: #fdf293;
  outline: none !important;
  border-top: 1px solid black;
}

/* Red home cells */
.cell-red-0 { 
  grid-column: 1; 
  grid-row: 10; 
  --cell-bg-color: red;
}
.cell-red-1 { 
  grid-column: 2; 
  grid-row: 10; 
  --cell-bg-color: red;
}
.cell-red-2 { 
  grid-column: 1; 
  grid-row: 11;
  --cell-bg-color: red; 
}
.cell-red-3 { 
  grid-column: 2; 
  grid-row: 11; 
  --cell-bg-color: red;
}

.cell-red-player-name { 
  grid-column: 1 / span 2; 
  grid-row: 9; 
  --cell-bg-color: #fdf293;
  outline: none !important;
  border-bottom: 1px solid black;
}

/* Blue home cells */
.cell-blue-0 { 
  grid-column: 10; 
  grid-row: 10; 
  --cell-bg-color: blue;
}
.cell-blue-1 { 
  grid-column: 11; 
  grid-row: 10; 
  --cell-bg-color: blue;
}
.cell-blue-2 { 
  grid-column: 10; 
  grid-row: 11; 
  --cell-bg-color: blue;
}
.cell-blue-3 { 
  grid-column: 11; 
  grid-row: 11; 
  --cell-bg-color: blue;
}

.cell-blue-player-name { 
  grid-column: 10 / span 2; 
  grid-row: 9; 
  --cell-bg-color: #fdf293;
  outline: none !important;
  border-bottom: 1px solid black;
}

/* Safe zone cells */
.cell-red-safe-0 {
  grid-column: 6;
  grid-row: 10;
  --cell-bg-color: red;
}

.cell-red-safe-1 {
  grid-column: 6;
  grid-row: 9;
  --cell-bg-color: red; 
}

.cell-red-safe-2 {
  grid-column: 6;
  grid-row: 8;
  --cell-bg-color: red;
}

.cell-red-safe-3 {
  grid-column: 6;
  grid-row: 7;
  --cell-bg-color: red;
}

.cell-blue-safe-0 {
  grid-column: 10;
  grid-row: 6;
  --cell-bg-color: blue;
}

.cell-blue-safe-1 {
  grid-column: 9;
  grid-row: 6;
  --cell-bg-color: blue;
}

.cell-blue-safe-2 {
  grid-column: 8;
  grid-row: 6;
  --cell-bg-color: blue;
}

.cell-blue-safe-3 {
  grid-column: 7;
  grid-row: 6;
  --cell-bg-color: blue;
}

.cell-yellow-safe-0 {
  grid-column: 6;
  grid-row: 2;
  --cell-bg-color: yellow;
}

.cell-yellow-safe-1 {
  grid-column: 6;
  grid-row: 3;
  --cell-bg-color: yellow;
}

.cell-yellow-safe-2 {
  grid-column: 6;
  grid-row: 4;
  --cell-bg-color: yellow;
}

.cell-yellow-safe-3 {
  grid-column: 6;
  grid-row: 5;
  --cell-bg-color: yellow;
}

.cell-green-safe-0 {
  grid-column: 2;
  grid-row: 6;
  --cell-bg-color: green;
}

.cell-green-safe-1 {
  grid-column: 3;
  grid-row: 6;
  --cell-bg-color: green;
}

.cell-green-safe-2 {
  grid-column: 4;
  grid-row: 6;
  --cell-bg-color: green;
}

.cell-green-safe-3 {
  grid-column: 5;
  grid-row: 6;
  --cell-bg-color: green;
}

.piece {
  width: 35px; /* Width of the piece */
  height: 35px; /* Height of the piece */
  border-radius: 50%; /* Make the piece a circle */
  z-index: 2;
}

.player-name {
  font-family: Arial, sans-serif; /* Set the font family */
  font-size: 20px; /* Set the font size */
  font-weight: bold; /* Set the font weight */
  color: black; /* Set the text color */
}

.card-popup {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: white;
  border: 2px solid black;
  padding: 20px;
  z-index: 10;
}

.card-options button {
  margin: 10px;
  padding: 20px 40px; /* Increase padding to make the button larger */
  cursor: pointer;
  font-size: 18px; /* Increase font size */
  font-weight: bold; /* Make text bolder */
  border-radius: 8px; /* Optional: rounded corners for the buttons */
  background-color: #dbe2e9; /* Optional: background color */
  color: rgb(5, 5, 5); /* Optional: text color */
  border: none; /* Remove the border */
  transition: background-color 0.3s ease, transform 0.2s ease; /* Smooth transitions for hover effect */
}

.card-options button:disabled {
  background-color: #ccc; /* Make disabled buttons appear grey */
  cursor: not-allowed; /* Change cursor to indicate the button is disabled */
}

.card-options button:hover:not(:disabled) {
  background-color: #0056b3; /* Darker background on hover */
  transform: scale(1.1); /* Slightly increase size on hover */
}

.disabled_dice {
  opacity: 0.5;
  pointer-events: none; /* Prevent clicking */
}
</style>