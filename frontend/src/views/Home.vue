<template>
  <div class="home-page">
    <LoginForm v-if="!store.isLoggedIn" />
    <div v-else class="already-logged-in">
      <p>You are already logged in!</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useChatStore } from "@/store";
import LoginForm from "@/views/LoginView.vue";
import { useRouter } from 'vue-router';

const store = useChatStore();
const router = useRouter();

if (store.isLoggedIn) {
  router.push('/chat'); // Перенаправление на страницу чатов, если пользователь авторизован
}
</script>

<style scoped>
.home-page {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #36393f;
  color: white;
}

.already-logged-in {
  text-align: center;
}
</style>