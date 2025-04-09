<template>
  <div class="chat-page">
    <div class="chat-header">
      <h2>Chat</h2>
      <button @click="logout" class="logout-button">Logout</button>
    </div>
    
    <div class="chat-container">
      <!-- Левая панель с вкладками -->
      <div class="left-panel">
        <div class="tabs">
          <button 
            @click="activeTab = 'chats'" 
            :class="{ 'active-tab': activeTab === 'chats' }"
          >
            Chats
          </button>
          <button 
            @click="activeTab = 'profile'" 
            :class="{ 'active-tab': activeTab === 'profile' }"
          >
            Profile
          </button>
        </div>

        <!-- Содержимое вкладки профиля -->
        <div v-if="activeTab === 'profile'" class="profile-container">
          <h3>My Profile</h3>
          <div class="profile-info">
            <p><strong>Username:</strong> {{ userProfile.username }}</p>
            <p><strong>Email:</strong> {{ userProfile.email }}</p>
          </div>
        </div>

        <!-- Содержимое вкладки чатов -->
        <div v-else class="chats-tab">
          <div class="search-users-container">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search users..."
              @input="searchUsers"
              class="search-users-input"
            />
            <ul v-if="searchResults.length > 0" class="search-results">
              <li 
                v-for="user in searchResults" 
                :key="user.id" 
                @click="createPersonalChat(user)"
              >
                {{ user.username }}
              </li>
            </ul>
          </div>

          <div class="chat-list">
            <h3>Your Chats</h3>
            <ul>
              <li 
                v-for="chat in chats" 
                :key="chat.id" 
                @click="openChat(chat)" 
                :class="{ active: currentChat?.id === chat.id }"
              >
                {{ getChatDisplayName(chat.name) }}
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Окно чата с профилем пользователя -->
      <div v-if="currentChat" class="chat-window">
        <div class="chat-header" @click="toggleUserProfile">
          <div class="chat-partner">
            {{ getChatDisplayName(currentChat.name) }}
          </div>
        </div>

        <!-- Сообщения -->
        <div class="messages-container">
          <div class="messages">
            <div v-for="message in messages" :key="message.id" class="message" 
                :class="{ 'my-message': message.sender_id === store.userId, 'their-message': message.sender_id !== store.userId }">
              <span class="username">{{ message.username }}:</span>
              <span class="text">{{ message.content }}</span>
              <span class="timestamp">{{ new Date(message.timestamp).toLocaleTimeString() }}</span>
            </div>
          </div>
        </div>

        <!-- Боковая панель профиля пользователя -->
        <div v-if="showUserProfile" class="user-profile-sidebar">
          <div class="profile-info">
            <h3>User Profile</h3>
            <p><strong>Username:</strong> {{ selectedUserProfile?.username }}</p>
            <p><strong>Email:</strong> {{ selectedUserProfile?.email }}</p>
          </div>
          <button @click="showUserProfile = false" class="close-button">×</button>
        </div>

        <!-- Поле ввода сообщения -->
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

      <div v-else class="no-chat">
        <p>Select a chat to start messaging.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useChatStore } from '@/store';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { io } from 'socket.io-client';

const store = useChatStore();
const router = useRouter();

// Состояния интерфейса
const activeTab = ref('chats');
const showUserProfile = ref(false);
const selectedUserProfile = ref(null);

// Состояния данных
const chats = ref([]);
const currentChat = ref(null);
const messages = ref([]);
const newMessage = ref('');
const searchQuery = ref('');
const searchResults = ref([]);
const userProfile = ref({ 
  username: '', 
  email: '' 
});

const socket = io('http://127.0.0.1:5000');

// Методы
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
  if (!searchQuery.value.trim()) {
    searchResults.value = [];
    return;
  }

  try {
    const response = await axios.get(
      `http://127.0.0.1:5000/search_users?username=${searchQuery.value}`
    );
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

    if (response.data.chat?.id) {
      await openChat(response.data.chat);
      await fetchChats();
    }
  } catch (error) {
    console.error("Error creating personal chat", error);
  }
};

const getChatParticipant = async (chat) => {
  if (chat.is_group) return null;
  const participantId = chat.participants?.find(id => id !== store.userId);
  if (!participantId) return null;

  try {
    const response = await axios.get(
      `http://127.0.0.1:5000/get_user_profile/${participantId}`
    );
    return response.data;
  } catch (error) {
    console.error("Error fetching participant profile", error);
    return null;
  }
};

const openChat = async (chat) => {
  currentChat.value = chat;
  selectedUserProfile.value = await getChatParticipant(chat);
  fetchMessages(chat.id);
};

const fetchMessages = async (chatId) => {
  try {
    const response = await axios.get(`http://127.0.0.1:5000/get_messages/${chatId}`);
    const messagesWithUsernames = await Promise.all(
      response.data.map(async message => ({
        ...message,
        username: await getUsernameById(message.sender_id)
      }))
    );
    messages.value = messagesWithUsernames;
    socket.emit('join_chat', { chat_id: chatId });
  } catch (error) {
    console.error("Error fetching messages", error);
  }
};

const getUsernameById = async (userId) => {
  try {
    const response = await axios.get(
      `http://127.0.0.1:5000/search_user_by_id/${userId}`
    );
    return response.data.username;
  } catch (error) {
    console.error("Error fetching username", error);
    return "Unknown";
  }
};

const getChatDisplayName = computed(() => (chatName) => {
  return chatName.split(' ')
    .filter(name => name !== userProfile.value.username)
    .join(' ');
});

const sendMessage = () => {
  if (!newMessage.value.trim()) return;

  socket.emit('send_message', {
    chat_id: currentChat.value.id,
    user_id: store.userId,
    text: newMessage.value
  });
  newMessage.value = '';
};

const toggleUserProfile = () => {
  showUserProfile.value = !showUserProfile.value;
};

const logout = () => {
  store.clearUser();
  router.push('/');
};

// Хуки жизненного цикла
onMounted(() => {
  if (!store.isLoggedIn) {
    router.push('/');
  } else {
    fetchUserProfile();
    fetchChats();
  }
});

// Socket handlers
socket.on('receive_message', async (data) => {
  if (currentChat.value?.id === data.chat_id) {
    messages.value.push({
      ...data,
      content: data.text,
      username: await getUsernameById(data.sender_id)
    });
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
  position: relative;
  flex: 1;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 80px); /* Учитываем высоту шапки */
}

.messages {
  min-height: min-content;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.message {
  margin-bottom: 15px;
  padding: 12px 16px;
  border-radius: 15px;
  max-width: 70%;
  position: relative;
  animation: fadeIn 0.3s ease;
}

.my-message {
  background-color: #007aff; /* Синий цвет для своих сообщений */
  color: white;
  margin-left: auto; /* Выравнивание справа */
  border-bottom-right-radius: 4px; /* Скругление угла */
}

.their-message {
  background-color: #3d3d3d; /* Темный цвет для чужих сообщений */
  color: white;
  margin-right: auto; /* Выравнивание слева */
  border-bottom-left-radius: 4px; /* Скругление угла */
}

/* Корректируем цвет текста для своих сообщений */
.my-message .username,
.my-message .text,
.my-message .timestamp {
  color: white !important;
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

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.username {
  display: block;
  font-size: 0.9em;
  margin-bottom: 4px;
}

.text {
  color: #ffffff; /* Белый текст */
}

.timestamp {
  display: block;
  font-size: 0.75em;
  margin-top: 6px;
  opacity: 0.8;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  scroll-behavior: smooth; /* Плавная прокрутка */
}

/* Поле ввода сообщений */
.message-input-container {
  position: sticky;
  bottom: 0;
  background: #2d2d2d;
  padding: 16px;
  border-top: 1px solid #444;
  z-index: 10;
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
  color: #ffffff;
}

.profile-info h3 {
  margin-top: 0;
  color: #007aff;
}

.profile-info p {
  margin: 8px 0;
}

.profile-info strong {
  color: #007aff; /* Синий цвет для выделения */
}

.tabs button {
  flex: 1;
  padding: 10px;
  border: none;
  background: #3d3d3d; /* Темный фон */
  color: #ffffff;       /* Белый текст */
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: background-color 0.2s ease, border-bottom 0.2s ease;
}

.tabs button:hover {
  background: #4d4d4d; /* Немного темнее при наведении */
}

.tabs button.active-tab {
  background: #2d2d2d;         /* Чуть темнее для активной */
  border-bottom: 2px solid #007aff; /* Синяя линия внизу */
  font-weight: 600;
}

.user-profile-sidebar {
  position: absolute;
  right: 0;
  top: 0;
  width: 280px;
  height: 100%;
  background-color: #3d3d3d; /* Темный фон как у чата */
  border-left: 1px solid #444; /* Граница как между панелями */
  padding: 20px;
  z-index: 100;
  box-shadow: -4px 0 8px rgba(0, 0, 0, 0.1);
  animation: slideIn 0.3s ease-out;
}

.close-button {
  position: absolute;
  top: 15px;
  right: 15px;
  background: none;
  border: none;
  color: #8e8e93;
  font-size: 24px;
  cursor: pointer;
  transition: color 0.2s ease;
}

.close-button:hover {
  color: #007aff;
}


.chat-header {
  cursor: pointer;
  padding: 10px;
  border-bottom: 1px solid #ddd;
}
</style>