import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api/auth'
import { getErrorMessage } from '../api/client'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const userType = ref(null) // 'administrator' or 'customer'
  const customer = ref(null) // Customer object for customer users
  const business = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => !!user.value)
  const isAdministrator = computed(() => userType.value === 'administrator')
  const isCustomer = computed(() => userType.value === 'customer')

  const signup = async (signupData) => {
    loading.value = true
    error.value = null
    try {
      const response = await authApi.signup(signupData)
      const { data } = response.data

      localStorage.setItem('access_token', data.tokens.access)
      localStorage.setItem('refresh_token', data.tokens.refresh)

      user.value = data.user
      userType.value = 'administrator' // Signup always creates a business owner
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
      userType.value = data.user_type
      business.value = data.business
      
      // Store customer data if user is a customer
      if (data.user_type === 'customer' && data.customer) {
        customer.value = data.customer
      } else {
        customer.value = null
      }

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
    userType.value = null
    customer.value = null
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
      userType.value = data.user_type || 'administrator' // Default to admin if not set
      business.value = data.business
      
      // Store customer data if user is a customer
      if (data.user_type === 'customer' && data.customer) {
        customer.value = data.customer
      } else {
        customer.value = null
      }
      
      return true
    } catch (err) {
      // Token invalid or expired - clear storage
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      user.value = null
      userType.value = null
      customer.value = null
      business.value = null
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    user,
    userType,
    customer,
    business,
    loading,
    error,
    isAuthenticated,
    isAdministrator,
    isCustomer,
    signup,
    login,
    logout,
    restoreSession,
  }
})
