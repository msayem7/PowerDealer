import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const business = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => !!user.value)

  const signup = async (signupData) => {
    loading.value = true
    error.value = null
    try {
      const response = await authApi.signup(signupData)
      const { user: userData, business: businessData, tokens } = response.data

      localStorage.setItem('access_token', tokens.access)
      localStorage.setItem('refresh_token', tokens.refresh)

      user.value = userData
      business.value = businessData

      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Signup failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  const login = async (username, password) => {
    loading.value = true
    error.value = null
    try {
      const response = await authApi.login(username, password)
      const { user: userData, business: businessData, tokens } = response.data

      localStorage.setItem('access_token', tokens.access)
      localStorage.setItem('refresh_token', tokens.refresh)

      user.value = userData
      business.value = businessData

      return response.data
    } catch (err) {
      error.value = err.response?.data?.error || 'Login failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  const logout = () => {
    user.value = null
    business.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  const restoreSession = () => {
    const token = localStorage.getItem('access_token')
    if (token) {
      // Optional: Validate token with backend
      return true
    }
    return false
  }

  return {
    user,
    business,
    loading,
    error,
    isAuthenticated,
    signup,
    login,
    logout,
    restoreSession,
  }
})
