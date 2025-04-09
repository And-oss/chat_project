<template>
  <div class="chat-page">
    <div class="chat-header">
      <h2>Chat</h2>
      <button @click="logout" class="logout-button">Logout</button>
    </div>
    <div class="chat-container">
      <!-- Левая панель: профиль, поиск пользователей и список чатов -->
      <div class="left-panel">
        <!-- Вкладка "Profile" -->
        <div class="profile-container">
          <h3>Profile</h3>
          <div class="profile-info">
            <p><strong>Username:</strong> {{ userProfile.username }}</p>
            <p><strong>Email:</strong> {{ userProfile.email }}</p>
          </div>
        </div>

        <!-- Поиск пользователей -->
        <div class="search-users-container">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search users..."
            @input="searchUsers"
            class="search-users-input"
          />
          <ul v-if="searchResults.length > 0" class="search-results">
            <li v-for="user in searchResults" :key="user.id" @click="createPersonalChat(user)">
              {{ user.username }}
            </li>
          </ul>
        </div>

        <!-- Список чатов -->
        <div class="chat-list">
          <h3>Your Chats</h3>
          <ul>
            <li v-for="chat in chats" :key="chat.id" @click="openChat(chat)" :class="{ active: currentChat?.id === chat.id }">
              {{ chat.name }}
            </li>
          </ul>
        </div>
      </div>

      <!-- Окно чата -->
      <div v-if="currentChat" class="chat-window">
        <div class="messages">
          <div v-for="message in messages" :key="message.id" class="message">
            <span class="username">{{ message.username }}:</span>
            <span class="text">{{ message.content }}</span>
            <span class="timestamp">{{ new Date(message.timestamp).toLocaleTimeString() }}</span>
          </div>
        </div>
        <div class="message-input-container">
          <input
            v-model="newMessage"
            type="text"
            placeholder="Type a message..."
            @keyup.enter="sendMessage"
            class="message-input"
          />
          <button @click="sendMessage" class="send-button">Send</button>
        </div>
      </div>

      <!-- Сообщение, если чат не выбран -->
      <div v-else class="no-chat">
        <p>Select a chat to start messaging.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useChatStore } from '@/store';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { io } from 'socket.io-client';

const store = useChatStore();
const router = useRouter();

const chats = ref([]);
const currentChat = ref(null);
const messages = ref([]);
const newMessage = ref('');
const searchQuery = ref('');
const searchResults = ref([]);
const userProfile = ref({ username: '', email: '' }); // Данные профиля
const socket = io('http://127.0.0.1:5000');

// Загрузка данных профиля
const fetchUserProfile = async () => {
  try {
    const response = await axios.get(`http://127.0.0.1:5000/get_user_profile/${store.userId}`);
    userProfile.value = response.data;
  } catch (error) {
    console.error("Error fetching user profile", error);
  }
};

const fetchChats = async () => {
  try {
    const response = await axios.get(`http://127.0.0.1:5000/get_chats/${store.userId}`);
    chats.value = response.data;
  } catch (error) {
    console.error("Error fetching chats", error);
  }
};

const searchUsers = async () => {
  if (searchQuery.value.trim() === '') {
    searchResults.value = [];
    return;
  }

  try {
    const response = await axios.get(`http://127.0.0.1:5000/search_users?username=${searchQuery.value}`);
    searchResults.value = response.data;
  } catch (error) {
    console.error("Error searching users", error);
  }
};

const createPersonalChat = async (user) => {
  try {
    const response = await axios.post('http://127.0.0.1:5000/create_personal_chat', {
      user_id: store.userId,
      participant_id: user.id,
    });

    console.log("Create chat response:", response.data);

    if (response.data.chat && response.data.chat.id) {
      // Option 1: Open the chat directly from the response data
      openChat(response.data.chat);
      
      // Option 2: Also refresh the chat list to ensure it's up to date
      await fetchChats();
    }
  } catch (error) {
    console.error("Error creating personal chat", error);
  }
};

const getUsernameById = async (userId) => {
  if (!userId) {
    console.error("User ID is undefined!");
    return "Unknown";
  }

  try {
    const response = await axios.get(`http://127.0.0.1:5000/search_user_by_id/${userId}`);
    return response.data.username;
  } catch (error) {
    console.error(`Error fetching username for user ${userId}`, error);
    return "Unknown";
  }
};

const openChat = (chat) => {
  console.log("Открываем чат:", chat);
  currentChat.value = chat;
  fetchMessages(chat.id);
};

const fetchMessages = async (chatId) => {
  try {
    const response = await axios.get(`http://127.0.0.1:5000/get_messages/${chatId}`);
    let fetchedMessages = response.data;

    for (let message of fetchedMessages) {
      message.username = await getUsernameById(message.sender_id);
    }

    messages.value = fetchedMessages;
    socket.emit('join_chat', { chat_id: chatId });
  } catch (error) {
    console.error("Error fetching messages", error);
  }
};

const sendMessage = () => {
  if (newMessage.value.trim() === '') return;

  const messageData = {
    chat_id: currentChat.value.id,
    user_id: store.userId,
    text: newMessage.value,
  };

  socket.emit('send_message', messageData);
  newMessage.value = '';
};

const logout = () => {
  store.clearUser();
  router.push('/');
};

socket.on('receive_message', async (data) => {
  if (currentChat.value && currentChat.value.id === data.chat_id) {
    console.log("Получено сообщение:", data);
    data.username = await getUsernameById(data.sender_id);
    console.log(`Имя пользователя: ${data.username}`);
    messages.value.push({
      ...data,
      content: data.text,
    });
  }
});

onMounted(() => {
  if (!store.isLoggedIn) {
    router.push('/');
  } else {
    fetchUserProfile(); // Загружаем данные профиля
    fetchChats();
  }
});
</script>

<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #1e1e1e; /* Темный фон */
  color: #ffffff; /* Белый текст */
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; /* Шрифт Apple */
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background-color: #2d2d2d; /* Темный фон для заголовка */
  border-bottom: 1px solid #444; /* Темная граница */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* Тень для глубины */
}

.chat-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600; /* Полужирный шрифт */
}

.logout-button {
  background-color: #007aff; /* Синий цвет, как в iOS */
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px; /* Скругленные углы */
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s ease; /* Плавное изменение цвета */
}

.logout-button:hover {
  background-color: #0063cc; /* Темнее при наведении */
}

.chat-container {
  display: flex;
  flex: 1;
  overflow: hidden;
  max-width: 1200px; /* Ограничиваем ширину для центрирования */
  margin: 0 auto; /* Центрируем контейнер */
  background-color: #2d2d2d; /* Темный фон для контейнера */
  border-radius: 12px; /* Скругленные углы */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); /* Тень для глубины */
  margin-top: 20px; /* Отступ сверху */
}

/* Левая панель: поиск пользователей и список чатов */
.left-panel {
  width: 300px; /* Фиксированная ширина */
  background-color: #2d2d2d; /* Темный фон */
  padding: 16px;
  border-right: 1px solid #444; /* Темная граница */
}

/* Поиск пользователей */
.search-users-container {
  margin-bottom: 16px;
}

.search-users-input {
  width: 100%;
  padding: 8px;
  border: 1px solid #444; /* Темная граница */
  border-radius: 8px; /* Скругленные углы */
  background-color: #3d3d3d; /* Темный фон для поля ввода */
  color: #ffffff; /* Белый текст */
  font-size: 14px;
  transition: border-color 0.2s ease; /* Плавное изменение цвета границы */
}

.search-users-input:focus {
  border-color: #007aff; /* Синяя граница при фокусе */
  outline: none;
}

.search-results {
  list-style-type: none;
  padding: 0;
  margin: 0;
  margin-top: 8px;
  background-color: #3d3d3d; /* Темный фон */
  border-radius: 8px; /* Скругленные углы */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* Тень для глубины */
  max-height: 150px;
  overflow-y: auto;
}

.search-results li {
  padding: 8px 12px;
  cursor: pointer;
  transition: background-color 0.2s ease; /* Плавное изменение цвета */
}

.search-results li:hover {
  background-color: #4d4d4d; /* Темнее при наведении */
}

/* Список чатов */
.chat-list {
  margin-top: 16px;
}

.chat-list h3 {
  margin: 0 0 12px 0;
  font-size: 18px;
  font-weight: 600; /* Полужирный шрифт */
}

.chat-list ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.chat-list li {
  padding: 10px;
  cursor: pointer;
  border-radius: 8px; /* Скругленные углы */
  margin-bottom: 8px;
  transition: background-color 0.2s ease; /* Плавное изменение цвета */
}

.chat-list li:hover {
  background-color: #4d4d4d; /* Темнее при наведении */
}

.chat-list li.active {
  background-color: #007aff; /* Синий цвет для активного чата */
  color: white;
}

/* Окно чата */
.chat-window {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #2d2d2d; /* Темный фон */
  border-radius: 0 12px 12px 0; /* Скругленные углы справа */
}

.messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  scroll-behavior: smooth; /* Плавная прокрутка */
}

.message {
  margin-bottom: 15px;
  padding: 10px;
  border-radius: 8px; /* Скругленные углы */
  background-color: #3d3d3d; /* Темный фон для сообщений */
  max-width: 70%; /* Ограничиваем ширину сообщений */
  animation: fadeIn 0.3s ease; /* Анимация появления */
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.username {
  font-weight: 600; /* Полужирный шрифт */
  color: #007aff; /* Синий цвет для имени */
  margin-right: 5px;
}

.text {
  color: #ffffff; /* Белый текст */
}

.timestamp {
  font-size: 0.8em;
  color: #8e8e93; /* Серый цвет для времени */
  margin-left: 10px;
}

/* Поле ввода сообщений */
.message-input-container {
  display: flex;
  padding: 16px;
  background-color: #2d2d2d; /* Темный фон */
  border-top: 1px solid #444; /* Темная граница */
  position: sticky; /* Фиксируем внизу */
  bottom: 0;
}

.message-input {
  flex: 1;
  padding: 10px;
  border: 1px solid #444; /* Темная граница */
  border-radius: 8px; /* Скругленные углы */
  background-color: #3d3d3d; /* Темный фон для поля ввода */
  color: #ffffff; /* Белый текст */
  margin-right: 10px;
  font-size: 14px;
  transition: border-color 0.2s ease; /* Плавное изменение цвета границы */
}

.message-input:focus {
  border-color: #007aff; /* Синяя граница при фокусе */
  outline: none;
}

.message-input::placeholder {
  color: #8e8e93; /* Серый цвет для плейсхолдера */
}

.send-button {
  background-color: #007aff; /* Синий цвет */
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px; /* Скругленные углы */
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s ease; /* Плавное изменение цвета */
}

.send-button:hover {
  background-color: #0063cc; /* Темнее при наведении */
}

/* Сообщение, если чат не выбран */
.no-chat {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #8e8e93; /* Серый цвет */
  font-size: 16px;
}

.profile-container {
  margin-bottom: 16px;
  padding: 16px;
  background-color: #3d3d3d; /* Темный фон */
  border-radius: 8px; /* Скругленные углы */
}

.profile-container h3 {
  margin: 0 0 12px 0;
  font-size: 18px;
  font-weight: 600; /* Полужирный шрифт */
}

.profile-info {
  color: #ffffff; /* Белый текст */
}

.profile-info p {
  margin: 8px 0;
}

.profile-info strong {
  color: #007aff; /* Синий цвет для выделения */
}
</style>