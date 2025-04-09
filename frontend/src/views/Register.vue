<template>
  <div class="register-page">
    <h2>Регистрация</h2>
    <form @submit.prevent="register">
      <div>
        <label for="username">Имя пользователя</label>
        <input type="text" v-model="username" required />
      </div>
      <div>
        <label for="email">Email</label>
        <input type="email" v-model="email" required />
      </div>
      <div>
        <label for="password">Пароль</label>
        <input type="password" v-model="password" required />
      </div>
      <div>
        <label for="confirmPassword">Подтвердите пароль</label>
        <input type="password" v-model="confirmPassword" required />
      </div>
      <button type="submit">Зарегистрироваться</button>
    </form>

    <div v-if="isCodeSent">
      <h3>Подтвердите свою почту</h3>
      <form @submit.prevent="verifyEmail">
        <div>
          <label for="verificationCode">Введите код из письма</label>
          <input type="text" v-model="verificationCode" required />
        </div>
        <button type="submit">Подтвердить</button>
      </form>
    </div>

    <div v-if="errorMessage" class="error">{{ errorMessage }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";

const email = ref("");
const username = ref("");
const password = ref("");
const confirmPassword = ref("");
const verificationCode = ref("");
const isCodeSent = ref(false);
const errorMessage = ref<string | null>(null);
const router = useRouter();

const register = async () => {
  if (password.value !== confirmPassword.value) {
    errorMessage.value = "Пароли не совпадают";
    return;
  }

  try {
    await axios.post("http://127.0.0.1:5000/register", {
      email: email.value,
      username: username.value,
      password: password.value,
    });

    isCodeSent.value = true;
    errorMessage.value = null;
  } catch (error) {
    errorMessage.value = error.response?.data?.error || "Ошибка регистрации";
  }
};

const verifyEmail = async () => {
  try {
    await axios.post("http://127.0.0.1:5000/verify_email", {
      email: email.value,
      verification_code: verificationCode.value,
    });
    router.push("/");
  } catch (error) {
    errorMessage.value = error.response?.data?.error || "Ошибка подтверждения почты";
  }
};
</script>

<style scoped>
.register-page {
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