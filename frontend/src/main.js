// frontend/src/main.js
import './assets/main.css'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { useUserStore } from '@/stores/user.js'

import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
} from 'chart.js'
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

// ———————— Axios 全局配置 ————————
// 开发环境下，如果前端和后端不同域，把下面留空，然后在 vite.config.js 里配置代理。
// 若后端直接同域（例如同一个域名 + Django 静态文件部署），可以写成：
// axios.defaults.baseURL = 'http://localhost:8000'
axios.defaults.baseURL = ''

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)
app.use(ElementPlus)

const userStore = useUserStore()
const savedToken = userStore.token || localStorage.getItem('access_token')
if (savedToken) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`
}

// —— 全局请求拦截器 ——
// 每次请求都从 Pinia 或 localStorage 重新取最新 token 并注入
axios.interceptors.request.use(config => {
  const store = useUserStore()
  const tk = store.token || localStorage.getItem('access_token')
  if (tk) {
    config.headers.Authorization = `Bearer ${tk}`
  }
  return config
}, error => {
  return Promise.reject(error)
})

app.config.globalProperties.$axios = axios
app.mount('#app')
