<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-header">
        <h2>Welcome to Chat Application</h2>
        <p>Connect with your colleagues and friends</p>
      </div>

      <div class="auth-content">
        <form class="auth-form" @submit.prevent="handleLogin">
          <div class="form-row">
            <div class="form-group">
              <label for="username">Username</label>
              <input
                type="text"
                id="username"
                v-model="username"
                class="form-input"
                placeholder="Enter your username"
                required
              />
            </div>

            <div class="form-group">
              <label for="password">Password</label>
              <input
                type="password"
                id="password"
                v-model="password"
                class="form-input"
                placeholder="Enter your password"
                required
              />
            </div>
          </div>

          <div class="actions">
            <button type="submit" class="submit-button">
              Sign In
              <span class="icon">→</span>
            </button>
            <router-link to="/forgot-password" class="link">Forgot password?</router-link>
          </div>

          <p v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </p>
        </form>
      </div>

      <div class="auth-footer">
        <span>New to our platform? </span>
        <router-link to="/register" class="link">Create account</router-link>
      </div>
    </div>
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
  try {
    const success = await store.login(username.value, password.value);
    if (success) {
      router.push('/chat');
    } else {
      errorMessage.value = "Invalid credentials. Please try again.";
    }
  } catch (error) {
    errorMessage.value = "An error occurred. Please try again later.";
  }
};
</script>

<style scoped>
.auth-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: #1a1a1a;
  background-image: linear-gradient(
    to bottom right,
    #2d2d2d 0%,
    #1e1e1e 100%
  );
}

.auth-container {
  width: 560px;
  padding: 48px;
  background-color: #2d2d2d;
  border-radius: 16px;
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3);
  border: 1px solid #444;
}

.auth-header {
  text-align: center;
  margin-bottom: 40px;
}

.auth-header h2 {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 8px;
  letter-spacing: -0.5px;
}

.auth-header p {
  color: #8e8e93;
  font-size: 16px;
  margin: 0;
}

.form-row {
  display: grid;
  gap: 24px;
  margin-bottom: 32px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  color: #8e8e93;
  font-weight: 500;
}

.form-input {
  padding: 14px 16px;
  border: 1px solid #444;
  border-radius: 10px;
  background-color: #3d3d3d;
  color: #ffffff;
  font-size: 15px;
  transition: all 0.2s ease;
}

.form-input:focus {
  border-color: #007aff;
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
  outline: none;
}

.actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 32px;
}

.submit-button {
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: #007aff;
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.submit-button:hover {
  background-color: #0063cc;
  transform: translateY(-1px);
}

.submit-button .icon {
  font-weight: 700;
  margin-left: 4px;
}

.link {
  color: #007aff;
  text-decoration: none;
  font-size: 14px;
  transition: color 0.2s ease;
}

.link:hover {
  color: #0063cc;
  text-decoration: underline;
}

.error-message {
  color: #ff453a;
  font-size: 14px;
  margin: 20px 0;
  padding: 12px;
  background-color: rgba(255, 69, 58, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(255, 69, 58, 0.2);
  display: flex;
  align-items: center;
  gap: 8px;
}

.social-auth {
  margin-top: 40px;
  padding-top: 40px;
  border-top: 1px solid #444;
}

.divider {
  color: #8e8e93;
  font-size: 14px;
  text-align: center;
  margin-bottom: 24px;
  position: relative;
}

.social-buttons {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.social-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  border: 1px solid #444;
  border-radius: 10px;
  background: none;
  color: #ffffff;
  cursor: pointer;
  transition: all 0.2s ease;
}

.social-button:hover {
  background-color: rgba(255, 255, 255, 0.05);
  transform: translateY(-1px);
}

.social-button img {
  width: 18px;
  height: 18px;
}

.auth-footer {
  text-align: center;
  margin-top: 40px;
  padding-top: 40px;
  border-top: 1px solid #444;
  color: #8e8e93;
  font-size: 14px;
}
</style>