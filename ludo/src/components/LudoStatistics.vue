<!-- Author: Lukáš Selický -->
<template>
  <div class="statistics-overlay" v-if="show">
    <div class="statistics-content">
      <h2>Game Over</h2>
      <p v-if="winner" class="winner-message">Congratulations, {{ winner }}! You won the game.</p>
      <p v-else class="no-winner-message">No winner yet.</p>
      <h3>Player positions in game:</h3>
      <ul class="player-list">
        <li
          v-for="(player, index) in sortedPlayers"
          :key="player.name"
          class="player-item"
        >
          <span class="player-placement">{{ index + 1 }}.</span>
          <span class="player-name">{{ player.name }} ({{ player.color }})</span>
          <span class="player-moves">made {{ player.total_moves }} moves.</span>
        </li>
      </ul>
      <div class="button-group">
        <button @click="returnToMenu" class="btn btn-primary">Return to Menu</button>
        <button @click="restartGame" class="btn btn-secondary">Restart Game</button>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex';

export default {
  name: 'LudoStatistics',
  props: {
    show: Boolean,
    winner: String,
    players: Array
  },
  computed: {
    sortedPlayers() {
      const playersCopy = [...this.players]; // copy the array to not change the original array
      
      // Sort the array by finished_order
      playersCopy.sort((a, b) => {
        if (a.finished_order === null) return 1;
        if (b.finished_order === null) return -1;
        return a.finished_order - b.finished_order;
      });
      
      return playersCopy;
    },
  },
  methods: {
    ...mapActions(['initGame', 'updateGameState']),
    async returnToMenu() {
      this.$router.push({ name: 'LudoMenu' });
    },
    async restartGame() {
      try {
        await this.initGame(); // Initialize the game state using Vuex action
        const gameState = this.$store.getters.getGameState;
        this.updateGameState(gameState); // Update the game state with new data
        console.log('Game restarted:', gameState);
        this.$emit('close', gameState); // Pass the game state data to the close event
      } catch (error) {
        console.error('Error restarting game:', error);
      }
    },
  },
};
</script>

<style scoped>
.statistics-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.statistics-content {
  background: white;
  padding: 30px;
  border-radius: 10px;
  text-align: center;
  max-width: 600px;
  width: 100%;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

h2 {
  font-size: 24px;
  margin-bottom: 20px;
}

.winner-message {
  font-size: 18px;
  color: #28a745;
  margin-bottom: 20px;
}

.no-winner-message {
  font-size: 18px;
  color: #dc3545;
  margin-bottom: 20px;
}

h3 {
  font-size: 20px;
  margin-bottom: 15px;
}

.player-list {
  list-style-type: none;
  padding: 0;
  text-align: left;
  margin-bottom: 20px;
}

.player-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #ddd;
}

.player-placement {
  font-weight: bold;
  margin-right: 10px;
}

.player-name {
  flex-grow: 1;
}

.player-moves {
  font-style: italic;
}

.button-group {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.btn {
  padding: 10px 20px;
  font-size: 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.btn-secondary {
  background-color: #28a745; 
  color: white;
}

.btn-secondary:hover {
  background-color: #218838; 
}
</style>
