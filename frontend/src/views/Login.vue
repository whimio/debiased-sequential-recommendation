<template>
  <div class="login-wrapper">
    <el-card class="login-card" shadow="hover">
      <h2 class="login-title">用户登录</h2>
      <el-form :model="form" :rules="rules" ref="loginForm" label-width="0">
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            prefix-icon="el-icon-user"
            size="large"
            clearable
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            prefix-icon="el-icon-lock"
            show-password
            size="large"
            clearable
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            @click="handleLogin"
            class="login-button"
            size="large"
            round
          >
            登录
          </el-button>
        </el-form-item>
        <div v-if="error" class="error-msg">{{ error }}</div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { jwtDecode } from 'jwt-decode'
import { useUserStore } from '@/stores/user.js'

const form = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}
const loginForm = ref(null)
const loading = ref(false)
const error = ref('')
const router = useRouter()
const userStore = useUserStore()

async function handleLogin() {
  error.value = ''
  loginForm.value.validate(async valid => {
    if (!valid) return
    loading.value = true
    try {
      const { data } = await axios.post('/api/token/', {
        username: form.username,
        password: form.password
      })
      localStorage.setItem('access_token', data.access)
      localStorage.setItem('refresh_token', data.refresh)
      axios.defaults.headers.common['Authorization'] = `Bearer ${data.access}`
      userStore.$patch({
        token: data.access,
        user: jwtDecode(data.access)
      })
      await router.push({ name: 'home' })
    } catch (e) {
      error.value = e.response?.status === 401
        ? '用户名或密码错误'
        : '登录失败，请稍后重试'
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.login-wrapper {
  height: 100vh;
  width: 100vw;
  background: linear-gradient(to bottom right, #e6f0ff, #f0f9ff);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  box-sizing: border-box;
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: 30px;
  border-radius: 16px;
  background-color: #ffffff;
  box-shadow: 0 8px 24px rgba(0, 123, 255, 0.1);
  transition: all 0.3s ease;
}

.login-title {
  text-align: center;
  font-size: 24px;
  margin-bottom: 30px;
  color: #409eff;
  font-weight: 600;
}

.login-button {
  width: 100%;
}

.error-msg {
  margin-top: 0.5rem;
  color: #f56c6c;
  text-align: center;
}
</style>
