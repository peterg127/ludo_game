<!-- Author: Peter Gvozdják -->
<template>
  <div class="chat-box">
    <h2>Game Chat</h2>
    <div class="chat-messages">
      <div v-for="(message, index) in chatHistory" :key="index" class="message">
        <strong>{{ message.user }}:</strong> {{ message.message }}
      </div>
    </div>
    <div class="input-container"> <!-- Wrap input and button in a container -->
      <input v-model="newMessage" placeholder="Type a message..." @keyup.enter="sendMessage" />
      <button @click="sendMessage">Send</button>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      chatHistory: [],       // Holds chat history
      newMessage: '',        // Holds the current message to be sent
      userName: 'Player',   // This could be dynamically assigned per player
    };
  },
  methods: {
    async fetchChatHistory() {
      try {
        const response = await fetch('http://localhost:5000/chat/history');
        if (!response.ok) throw new Error('Failed to fetch chat history');
        const data = await response.json();
        this.chatHistory = data;
      } catch (error) {
        console.error('Error fetching chat history:', error);
      }
    },
    async sendMessage() {
      if (this.newMessage.trim() === '') return; // Skip if empty
      const response = await fetch('http://localhost:5000/state');
      const data = await response.json();
      this.userName = data.players[data.current_turn].name;
      try {
        const response = await fetch('http://localhost:5000/chat/send', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user: this.userName,
            message: this.newMessage
          })
        });

        if (!response.ok) throw new Error('Failed to send message');
        this.newMessage = '';       // Clear input
        this.fetchChatHistory();    // Fetch updated chat history after sending
      } catch (error) {
        console.error('Error sending message:', error);
      }
    }
  },
  mounted() {
    this.fetchChatHistory();       // Fetch chat history when component is mounted
    setInterval(this.fetchChatHistory, 3000); // Periodically fetch new messages
  }
};
</script>

<style scoped>
.chat-box {
  border: 1px solid #ccc;
  padding: 10px;
  width: 100%; /* Allow it to scale within the parent container */
  max-width: 300px;
  height: 100%;
  display: flex;
  flex-direction: column; /* Stack messages and input vertically */
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 5px;
}

.message {
  margin-bottom: 5px;
}

.input-container {
  display: flex;
  gap: 5px; /* Add spacing between input and button */
}

input {
  flex: 1;
  padding: 5px;
}

button {
  padding: 5px;
}
</style>
