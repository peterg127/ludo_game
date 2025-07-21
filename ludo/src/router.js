// Author: Mário Perecz
import { createRouter, createWebHistory } from 'vue-router';
import LudoGameMode from './components/LudoGameMode.vue';
import LudoMenu from './components/LudoMenu.vue';
import LudoBoard from './components/LudoBoard.vue';

const routes = [
  {
    path: '/',
    name: 'LudoGameMode',
    component: LudoGameMode
  },
  {
    path: '/menu',
    name: 'LudoMenu',
    component: LudoMenu
  },
  {
    path: '/board',
    name: 'LudoBoard',
    component: LudoBoard
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

export default router;