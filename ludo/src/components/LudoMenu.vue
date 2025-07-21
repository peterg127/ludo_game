<!-- Author: Lukáš Selický -->
<template>
  <BaseLayout>
    <div class="menu container">
    <!-- Only show this form when there are less than 4 players -->  
      <form @submit.prevent="addPlayer" v-if="players.length < 4" class="mb-4 form-container">
        <div class="return-button-container">
          <ReturnButton to="LudoGameMode"></ReturnButton>
        </div>
        <div class="mb-3">
          <label for="name" class="form-label">Name:</label>
          <input type="text" id="name" v-model="name" class="form-control" required />
        </div>
        <div class="mb-3">
          <label class="form-label">Color:</label>
          <div class="color-options">
            <img
              v-for="color in availableColors"
              :key="color"
              :src="getPieceImage(color)"
              :alt="color"
              :class="['color-piece', { selected: color === selectedColor }]"
              @click="selectColor(color)"
            />
          </div>
        </div>
        <button type="submit" class="btn btn-primary btn-lg w-100">Add Player</button>
      </form>
      <!-- Added players in game -->
      <ul class="list-group mb-4">
        <li v-for="player in players" :key="player.name" class="list-group-item d-flex justify-content-between align-items-center">
          <div class="player-info">
            <img :src="getPieceImage(player.color)" :alt="player.color" class="player-piece-img" />
            {{ player.name }}
          </div>
          <img @click="removePlayer(player.name)" src="@/assets/close.png" alt="Remove" class="btn-close-img">
        </li>
      </ul>
      <!-- Start game button only when there are atleast 2 -->
      <button @click="startGame" :disabled="players.length < 2" class="btn btn-success btn-lg w-100">Start Game</button>
    </div>
  </BaseLayout>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';
import BaseLayout from './BaseLayout.vue';
import ReturnButton from './ReturnButton.vue';

export default {
  name: 'LudoMenu',
  components: {
    BaseLayout,
    ReturnButton
  },
  data() {
    return {
      name: ''
    };
  },
  computed: { // get the properties from the store
    ...mapGetters(['getGameState', 'getPlayers', 'getAvailableColors', 'getSelectedColor']),
    players() {
      return this.getPlayers;
    },
    availableColors() {
      return this.getAvailableColors;
    },
    selectedColor() {
      return this.getSelectedColor;
    }
  },
  methods: { // call the actions from the store
    ...mapActions(['fetchGameState', 'selectColor', 'initGame']),
    getPieceImage(color) {
      return require(`@/assets/${color}piece.png`);
    },
    async addPlayer() { 
      try {
        const response = await fetch('http://127.0.0.1:5000/add_player', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ name: this.name, color: this.selectedColor })
        });
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error);
        }
        await this.fetchGameState(); // Fetch the game state to update the players and available colors
        this.name = ''; // Reset the name input
        this.selectColor(this.availableColors[0] || ''); // Reset the color to the first available color or empty if none available
        console.log('Player added successfully');
      } catch (error) {
        console.error('Error adding player:', error);
      }
    },
    async removePlayer(playerName) {
      try {
        const response = await fetch('http://127.0.0.1:5000/remove_player', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ name: playerName }) // Send the player name to remove
        });
        if (!response.ok) { 
          const errorData = await response.json();
          throw new Error(errorData.error);
        }
        await this.fetchGameState(); // Fetch the game state to update the players and available colors after the remove
        console.log('Player removed successfully');
      } catch (error) {
        console.error('Error removing player:', error);
      }
    },
    async startGame() {
      try {
        const gameMode = this.getGameState.game_mode; // Get the current game mode from the state
        await this.initGame(gameMode); // Pass the game mode to the initGame action
        this.$router.push({ name: 'LudoBoard' }); // Navigate to the LudoBoard component
      } catch (error) {
        console.error('Error initializing game:', error);
      }
    },
  },
  created() {
    this.fetchGameState(); // Fetch game state when the component is created
  }
};
</script>

<style scoped>
.menu {
  max-width: 600px;
  margin: auto;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  grid-column: 2;
}

.form-container {
  margin-top: 40px;
  position: relative;
}

.return-button-container {
  position: absolute;
  top: -60px;
  left: -20px;
}

.color-options {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.color-piece {
  width: 60px;
  height: 60px;
  cursor: pointer;
  border-radius: 50%;
  opacity: 0.5; 
  transition: opacity 0.3s; 
}

.color-piece.selected {
  opacity: 1; 
}
.player-info {
  display: flex;
  align-items: center;
}

.player-piece-img {
  width: 30px;
  height: 30px;
  margin-right: 10px;
}

.btn-close-img {
  width: 20px;
  height: 20px;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.3s;
}

.btn-close-img:hover {
  opacity: 1;
}
</style>