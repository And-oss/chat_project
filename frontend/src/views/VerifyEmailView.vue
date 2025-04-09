<template>
  <div class="verify-email-page">
    <h2>Verify Email</h2>
    <input v-model="code" placeholder="Enter code" />
    <button @click="verifyEmail">Verify</button>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';

const code = ref('');

const verifyEmail = async () => {
  await axios.post('/verify-email', { code: code.value });
};
</script>

<style scoped>
.verify-email-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background-color: #36393f;
  color: white;
}

input {
  padding: 8px;
  border: 1px solid #484c52;
  border-radius: 4px;
  background-color: #484c52;
  color: white;
  margin-bottom: 10px;
}

button {
  padding: 10px;
  background-color: #7289da;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #677bc4;
}
</style>