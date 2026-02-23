import { defineStore } from 'pinia'
import { ref } from 'vue'
import { customerApi } from '../api/customer'
import { getErrorMessage } from '../api/client'

export const useCustomerStore = defineStore('customer', () => {
  const customers = ref([])
  const customer = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const fetchCustomers = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await customerApi.list()
      customers.value = response.data.data
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchCustomer = async (mprn) => {
    loading.value = true
    error.value = null
    try {
      const response = await customerApi.get(mprn)
      customer.value = response.data.data
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const createCustomer = async (data) => {
    loading.value = true
    error.value = null
    try {
      const response = await customerApi.create(data)
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateCustomer = async (mprn, data) => {
    loading.value = true
    error.value = null
    try {
      const response = await customerApi.update(mprn, data)
      customer.value = response.data.data
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    customers,
    customer,
    loading,
    error,
    fetchCustomers,
    fetchCustomer,
    createCustomer,
    updateCustomer,
  }
})
