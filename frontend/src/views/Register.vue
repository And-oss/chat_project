<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-header">
        <h2>Create New Account</h2>
        <p>Join our community to start chatting</p>
      </div>

      <form class="auth-form" @submit.prevent="register" v-if="!isCodeSent">
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
            <label for="email">Email</label>
            <input
              type="email"
              id="email"
              v-model="email"
              class="form-input"
              placeholder="Enter your email"
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
              placeholder="Create password"
              required
            />
          </div>

          <div class="form-group">
            <label for="confirmPassword">Confirm Password</label>
            <input
              type="password"
              id="confirmPassword"
              v-model="confirmPassword"
              class="form-input"
              placeholder="Repeat password"
              required
            />
          </div>
        </div>

        <button type="submit" class="submit-button">
          Create Account
          <span class="icon">→</span>
        </button>

        <p v-if="errorMessage" class="error-message">
          ⚠️ {{ errorMessage }}
        </p>
      </form>

      <div class="verification-section" v-if="isCodeSent">
        <div class="divider">Email Verification</div>
        
        <form class="auth-form" @submit.prevent="verifyEmail">
          <div class="form-group">
            <label for="verificationCode">Verification Code</label>
            <input
              type="text"
              id="verificationCode"
              v-model="verificationCode"
              class="form-input"
              placeholder="Enter code from email"
              required
            />
          </div>

          <button type="submit" class="submit-button">
            Verify Email
            <span class="icon">✓</span>
          </button>
        </form>
      </div>

      <div class="auth-footer">
        <span>Already have an account? </span>
        <router-link to="/" class="link">Sign In</router-link>
      </div>
    </div>
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
    errorMessage.value = "Passwords do not match";
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
    errorMessage.value = error.response?.data?.error || "Registration failed";
  }
};

const verifyEmail = async () => {
  try {
    await axios.post("http://127.0.0.1:5000/verify_email", {
      email: email.value,
      verification_code: verificationCode.value,
    });
    router.push("/login");
  } catch (error) {
    errorMessage.value = error.response?.data?.error || "Verification failed";
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
  width: 100%;
  justify-content: center;
  margin-top: 20px;
}

.submit-button:hover {
  background-color: #0063cc;
  transform: translateY(-1px);
}

.verification-section {
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

.error-message {
  color: #ff453a;
  font-size: 14px;
  margin: 20px 0;
  padding: 12px;
  background-color: rgba(255, 69, 58, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(255, 69, 58, 0.2);
  text-align: center;
}

.auth-footer {
  text-align: center;
  margin-top: 40px;
  padding-top: 40px;
  border-top: 1px solid #444;
  color: #8e8e93;
  font-size: 14px;
}

.link {
  color: #007aff;
  text-decoration: none;
  transition: color 0.2s ease;
}

.link:hover {
  color: #0063cc;
  text-decoration: underline;
}
</style>