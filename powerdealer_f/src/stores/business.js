import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi } from '../api/auth'
import { getErrorMessage } from '../api/client'

export const useBusinessStore = defineStore('business', () => {
  const business = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const fetchBusiness = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await authApi.getBusiness()
      business.value = response.data.data
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateBusiness = async (data) => {
    loading.value = true
    error.value = null
    try {
      const response = await authApi.updateBusiness(data)
      business.value = response.data.data
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const setBusiness = (businessData) => {
    business.value = businessData
  }

  return {
    business,
    loading,
    error,
    fetchBusiness,
    updateBusiness,
    setBusiness,
  }
})
