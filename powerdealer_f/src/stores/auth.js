import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api/auth'
import { getErrorMessage } from '../api/client'

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
      const { data } = response.data

      localStorage.setItem('access_token', data.tokens.access)
      localStorage.setItem('refresh_token', data.tokens.refresh)

      user.value = data.user
      business.value = data.business

      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
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
      const { data } = response.data

      localStorage.setItem('access_token', data.tokens.access)
      localStorage.setItem('refresh_token', data.tokens.refresh)

      user.value = data.user
      business.value = data.business

      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
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

  const restoreSession = async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      return false
    }
    
    try {
      loading.value = true
      const response = await authApi.getMe()
      const { data } = response.data
      
      user.value = data.user
      business.value = data.business
      
      return true
    } catch (err) {
      // Token invalid or expired - clear storage
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      user.value = null
      business.value = null
      return false
    } finally {
      loading.value = false
    }
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
