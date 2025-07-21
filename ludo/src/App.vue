<!-- Authors: Mário Perecz, Peter Gvozdják, Lukáš Selický -->
<template>
  <div id="app">
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'App'
};
</script>

<style>
html, body, #app {
  height: 100%;
  width: 100%;
  margin: 0;
  padding: 0;
}

#app {
  display: flex;
  flex-direction: column;
  justify-content: space-between; /* Distribute header, main, and footer */
  align-items: center;
  box-sizing: border-box; /* Avoid extra padding causing scroll issues */
}

.game-container {
  display: flex;
  max-width: 800px;
  border: 1px solid #ddd;
  padding: 20px;
}

.left-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.right-panel {
  width: 300px;
  margin-left: 20px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

button {
  margin-bottom: 10px; /* Add spacing between the button and chat box */
}
</style>
