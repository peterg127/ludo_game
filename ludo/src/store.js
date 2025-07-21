// Author: Mário Perecz
import { createStore } from 'vuex';

export default createStore({
  state: {
    gameState: null,
    players: [],
    availableColors: ['red', 'yellow', 'green', 'blue'],
    selectedColor: 'red'
  },
  mutations: {
    setGameState(state, gameState) {
      state.gameState = gameState;
    },
    setPlayers(state, players) {
      state.players = players;
    },
    setAvailableColors(state, availableColors) {
      state.availableColors = availableColors;
    },
    setSelectedColor(state, color) {
      state.selectedColor = color;
    }
  },
  actions: {
    async fetchGameState({ commit, state }) {
      try {
        const response = await fetch('http://localhost:5000/get_game_state', {
          method: 'GET',
        });
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.Error);
        }
        const data = await response.json();
        const players = data.game_state.players;
        const takenColors = players.map(player => player.color);
        const availableColors = ['red', 'yellow', 'green', 'blue'].filter(color => !takenColors.includes(color));

        commit('setGameState', data.game_state);
        commit('setPlayers', players);
        commit('setAvailableColors', availableColors);

        // Ensure the selected color is still available
        if (!availableColors.includes(state.selectedColor)) {
          commit('setSelectedColor', availableColors[0] || '');
        }

        console.log("GET GAME STATE", data);
      } catch (error) {
        console.error("Error fetching game state", error);
      }
    },
    async updateGameState({ commit }, gameState) {
      commit('setGameState', gameState);
    },
    selectColor({ commit }, color) {
      commit('setSelectedColor', color);
    },
    async initGame({ commit }, gameMode) {
      try {
        const response = await fetch('http://127.0.0.1:5000/init', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ game_mode: gameMode }),
        });
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error);
        }
        const data = await response.json();
        commit('setGameState', data);
        console.log("INIT GAME", data);
      } catch (error) {
        console.error('Error initializing game:', error);
      }
    }
  },
  getters: {
    getGameState: (state) => state.gameState,
    getPlayers: (state) => state.players,
    getAvailableColors: (state) => state.availableColors,
    getSelectedColor: (state) => state.selectedColor
  }
});