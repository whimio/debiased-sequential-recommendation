// src/stores/user.js


import { defineStore } from 'pinia'
import axios from 'axios'
import { jwtDecode } from 'jwt-decode'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('access_token') || null,
    user: null
  }),
  actions: {
    async login(username, password) {
      const { data } = await axios.post('/api/token/', { username, password })
      this.token = data.access
      localStorage.setItem('access_token', data.access)
      axios.defaults.headers.common['Authorization'] = `Bearer ${data.access}`
      this.user = jwtDecode(data.access)
    },
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('access_token')
      delete axios.defaults.headers.common['Authorization']
    },
    hydrate() {
      if (this.token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
        try {
          this.user = jwtDecode(this.token)
        } catch {
          this.logout()
        }
      }
    }
  }
})

