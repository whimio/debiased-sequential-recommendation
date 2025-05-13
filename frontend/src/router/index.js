import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/Login.vue'
import Home from '@/views/Home.vue'
import Recommend from '@/views/Recommend.vue'
import BatchRecommend from '@/views/BatchRecommend.vue'
import Eval from '@/views/Eval.vue'
import { useUserStore } from '@/stores/user'

const routes = [
  { path: '/',     redirect: '/login' },       // ← 改这里
  { path: '/login', name: 'login', component: Login },
  {
    path: '/home',
    name: 'home',
    component: Home,
    meta: { requiresAuth: true },
    children: [
      { path: '',           redirect: { name: 'recommend' } },
      { path: 'recommend',  name: 'recommend',  component: Recommend },
      { path: 'batch',      name: 'batch',      component: BatchRecommend },
      { path: 'eval',       name: 'eval',       component: Eval },
    ],
  },
  { path: '/:catchAll(.*)', redirect: '/login' },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 全局导航守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  if (to.meta.requiresAuth && !userStore.token) {
    return next({ name: 'login' })
  }
  if (to.name === 'login' && userStore.token) {
    return next({ name: 'home' })
  }
  next()
})

export default router
