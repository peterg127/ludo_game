<!-- Author: Mário Perecz -->
<template>
  <div class="base-layout">
    <header>
      <h1>LUDO 2.0</h1>
    </header>
    <main>
      <slot></slot>
    </main>
    <footer>
      <p>&copy; 2024 LUDO 2.0</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'BaseLayout'
};
</script>

<style scoped>
.base-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100%;
  background: #fdf293;
  background-size: cover;
  overflow: auto;
}

header {
  background-color: rgba(0, 0, 0, 0.3);
  color: black;
  padding: 1rem;
  text-align: center;
  font-family: Arial, sans-serif;
}

main {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 2fr 1fr; /* Left, center, and right columns */
  gap: 1rem; /* Optional: spacing between columns */
  padding: 1rem;
  justify-content: center;
  align-items: start; /* Align items to the top of the grid */
}

footer {
  background-color: rgba(0, 0, 0, 0.3);
  color: black;
  text-align: center;
  padding: 1rem;
}
</style>