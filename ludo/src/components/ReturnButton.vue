<!-- Author: Lukáš Selický -->
<template>
  <button @click="navigate" :class="buttonClass">
    <img :src="returnImage" alt="Return" class="return-img" />
    <slot></slot>
  </button>
</template>

<script>
export default {
  name: 'NavigationButton',
  props: {
    to: {
      type: String,
      required: true
    },
    buttonClass: {
      type: String,
      default: 'btn btn-primary'
    },
    returnImage: {
      type: String,
      default: require('@/assets/return.png') 
    }
  },
  methods: {
    // Method to navigate back to the specified route
    navigate() {
      this.$router.push({ name: this.to });
    }
  }
};
</script>

<style scoped>
.btn {
  padding: 10px 20px;
  font-size: 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
  display: flex;
  align-items: center;
}

.return-img {
  width: 20px;
  height: 20px;
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