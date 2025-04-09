<template>
  <div class="login-page">
    <h2>Login</h2>
    <form @submit.prevent="handleLogin">
      <div>
        <label for="username">Username:</label>
        <input type="text" v-model="username" required />
      </div>
      <div>
        <label for="password">Password:</label>
        <input type="password" v-model="password" required />
      </div>
      <button type="submit">Login</button>
    </form>
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useChatStore } from '@/store';
import { useRouter } from 'vue-router';

const store = useChatStore();
const router = useRouter();

const username = ref('');
const password = ref('');
const errorMessage = ref('');

const handleLogin = async () => {
  const success = await store.login(username.value, password.value);
  if (success) {
    router.push('/chat'); // Перенаправление на страницу чатов
  } else {
    errorMessage.value = "Login failed. Please check your credentials.";
  }
};
</script>

<style scoped>
.login-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background-color: #36393f;
  color: white;
}

form {
  display: flex;
  flex-direction: column;
  width: 300px;
}

form div {
  margin-bottom: 10px;
}

label {
  margin-bottom: 5px;
}

input {
  padding: 8px;
  border: 1px solid #484c52;
  border-radius: 4px;
  background-color: #484c52;
  color: white;
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

.error {
  color: #ff6b6b;
  margin-top: 10px;
}
</style>