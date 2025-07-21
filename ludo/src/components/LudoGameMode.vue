<!-- Author: Lukáš Selický -->
<template>
  <BaseLayout>
    <div class="game-mode-selection">
      <h2>Select Game Mode</h2>
      <div class="game-mode-buttons">
        <button @click="selectGameMode('classic')" class="btn btn-primary">Classic</button>
        <button @click="selectGameMode('special')" class="btn btn-secondary">Special</button>
      </div>
    </div>
  </BaseLayout>
</template>

<script>
import { mapActions } from 'vuex';
import BaseLayout from './BaseLayout.vue';

export default {
  name: 'GameModeSelection',
  components: {
    BaseLayout
  },
  methods: {
    ...mapActions(['fetchGameState', 'updateGameState']),
    // Select game mode, update the game state, and navigate to the LudoMenu
    async selectGameMode(mode) { 
      try {
        const response = await fetch('http://localhost:5000/update_game_mode', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ game_mode: mode }) // 
        });
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error);
        }
        const data = await response.json();
        await this.updateGameState(data.game_state);
        this.$router.push({ name: 'LudoMenu' });
      } catch (err) {
        console.error('Error updating game mode:', err);
      }
    }
  },
};
</script>

<style scoped>
.game-mode-selection {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  grid-column: 2;
}

.game-mode-buttons {
  display: flex;
  gap: 20px;
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