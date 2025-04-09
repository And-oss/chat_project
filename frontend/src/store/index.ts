import { defineStore } from "pinia";
import axios from "axios";

export const useChatStore = defineStore("chat", {
  state: () => ({
    userId: null, // ID пользователя
    username: "", // Имя пользователя
    isLoggedIn: false, // Флаг авторизации
    chats: [], // Список чатов
    messages: [], // Сообщения
  }),
  actions: {
    // Вход в систему
    async login(username: string, password: string) {
      try {
        const res = await axios.post("http://127.0.0.1:5000/login", { username, password });
        if (res.status === 200) {
          this.userId = res.data.user_id; // Сохраняем ID пользователя
          this.username = username; // Сохраняем имя пользователя
          this.isLoggedIn = true; // Устанавливаем флаг авторизации
          await this.fetchChats(); // Загружаем чаты пользователя
          return true; // Успешный вход
        }
      } catch (error) {
        console.error("Ошибка логина", error);
        return false; // Ошибка входа
      }
    },

    // Загрузка чатов пользователя
    async fetchChats() {
      try {
        const res = await axios.get(`http://127.0.0.1:5000/get_chats/${this.userId}`);
        this.chats = res.data; // Сохраняем чаты в состоянии
      } catch (error) {
        console.error("Ошибка загрузки чатов", error);
      }
    },

    // Регистрация пользователя
    async registerUser(email: string, username: string, password: string) {
      try {
        await axios.post("http://127.0.0.1:5000/register", { email, username, password });
      } catch (error) {
        throw new Error("Ошибка регистрации");
      }
    },

    // Выход из системы
    logout() {
      this.userId = null;
      this.username = "";
      this.isLoggedIn = false;
      this.chats = [];
      this.messages = [];
    },
  },
});