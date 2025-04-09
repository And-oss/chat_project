import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import ChatPage from '@/views/ChatPage.vue';
import Register from '../views/Register.vue';
import {useChatStore} from "@/store/index.ts";

const routes = [
  { path: '/', component: Home },
  { path: '/register', component: Register },
  { path: '/chat', component: ChatPage, meta: { requiresAuth: true } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !useChatStore().isLoggedIn) {
    next('/');  // Redirect to home if not logged in
  } else {
    next();
  }
});

export default router;