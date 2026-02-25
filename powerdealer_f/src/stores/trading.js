import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { tradingApi, extractTradingData, getErrorMessage, getFieldErrors } from '../api/trading'

export const useTradingStore = defineStore('trading', () => {
  // State
  const selectedCustomer = ref(null)
  const selectedYear = ref(new Date().getFullYear())
  const pivotData = ref(null)
  const trades = ref([])
  const loading = ref(false)
  const error = ref(null)
  const saveError = ref(null)
  const saveLoading = ref(false)

  // Getters
  const hasPivotData = computed(() => !!pivotData.value)
  
  const currentMonthData = computed(() => {
    if (!pivotData.value?.months) return []
    return pivotData.value.months
  })

  const totalBooked = computed(() => {
    if (!pivotData.value?.months) return {}
    const totals = {}
    pivotData.value.months.forEach(month => {
      totals[month.month] = month.total_percent
    })
    return totals
  })

  const averagePrice = computed(() => {
    if (!pivotData.value?.months) return {}
    const averages = {}
    pivotData.value.months.forEach(month => {
      averages[month.month] = month.average_price_achieved
    })
    return averages
  })

  const getMonthData = (month) => {
    if (!pivotData.value?.months) return null
    return pivotData.value.months.find(m => m.month === month)
  }

  // Actions
  const fetchPivotData = async (mprn, year) => {
    console.log('[Trading Store] fetchPivotData called with:', { mprn, year })
    
    if (!mprn || !year) {
      console.warn('[Trading Store] Missing mprn or year, skipping fetch')
      error.value = 'MPRN and year are required'
      return null
    }

    loading.value = true
    error.value = null
    
    try {
      console.log('[Trading Store] Making API call to /trading/pivot/')
      const response = await tradingApi.getTradingPivot(mprn, year)
      console.log('[Trading Store] API response received:', response.data)
      
      const data = extractTradingData(response)
      console.log('[Trading Store] Extracted data:', data)
      
      selectedCustomer.value = mprn
      selectedYear.value = year
      pivotData.value = data
      
      return data
    } catch (err) {
      console.error('[Trading Store] Failed to fetch pivot data:', err)
      error.value = getErrorMessage(err)
      console.error('Failed to fetch pivot data:', err)
      return null
    } finally {
      loading.value = false
    }
  }

  const fetchPivotDataByMprn = async (mprn, year) => {
    console.log('[Trading Store] fetchPivotDataByMprn called with:', { mprn, year })
    
    if (!mprn || !year) {
      console.warn('[Trading Store] Missing mprn or year, skipping fetch')
      error.value = 'MPRN and year are required'
      return null
    }

    loading.value = true
    error.value = null
    
    try {
      console.log('[Trading Store] Making API call to /trading/pivot/ by MPRN')
      const response = await tradingApi.getTradingPivotByMprn(mprn, year)
      console.log('[Trading Store] API response received:', response.data)
      
      const data = extractTradingData(response)
      console.log('[Trading Store] Extracted data:', data)
      
      selectedCustomer.value = mprn
      selectedYear.value = year
      pivotData.value = data
      
      return data
    } catch (err) {
      console.error('[Trading Store] Failed to fetch pivot data by MPRN:', err)
      error.value = getErrorMessage(err)
      console.error('Failed to fetch pivot data:', err)
      return null
    } finally {
      loading.value = false
    }
  }

  const fetchTrades = async (filters = {}) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await tradingApi.getTrades(filters)
      const data = extractTradingData(response)
      trades.value = data
      return data
    } catch (err) {
      error.value = getErrorMessage(err)
      console.error('Failed to fetch trades:', err)
      return []
    } finally {
      loading.value = false
    }
  }

  const createTrade = async (tradeData) => {
    saveLoading.value = true
    saveError.value = null
    
    try {
      const response = await tradingApi.createTrade(tradeData)
      const newTrade = extractTradingData(response)
      
      // Refresh pivot data after creating trade
      if (selectedCustomer.value && selectedYear.value) {
        await fetchPivotData(selectedCustomer.value, selectedYear.value)
      }
      
      return newTrade
    } catch (err) {
      saveError.value = getErrorMessage(err)
      const fieldErrors = getFieldErrors(err)
      console.error('Failed to create trade:', err)
      throw { message: saveError.value, fieldErrors }
    } finally {
      saveLoading.value = false
    }
  }

  const updateTrade = async (id, tradeData) => {
    saveLoading.value = true
    saveError.value = null
    
    try {
      const response = await tradingApi.updateTrade(id, tradeData)
      const updatedTrade = extractTradingData(response)
      
      // Refresh pivot data after updating trade
      if (selectedCustomer.value && selectedYear.value) {
        await fetchPivotData(selectedCustomer.value, selectedYear.value)
      }
      
      return updatedTrade
    } catch (err) {
      saveError.value = getErrorMessage(err)
      const fieldErrors = getFieldErrors(err)
      console.error('Failed to update trade:', err)
      throw { message: saveError.value, fieldErrors }
    } finally {
      saveLoading.value = false
    }
  }

  const patchTrade = async (id, tradeData) => {
    saveLoading.value = true
    saveError.value = null
    
    try {
      const response = await tradingApi.patchTrade(id, tradeData)
      const updatedTrade = extractTradingData(response)
      
      // Refresh pivot data after patching trade
      if (selectedCustomer.value && selectedYear.value) {
        await fetchPivotData(selectedCustomer.value, selectedYear.value)
      }
      
      return updatedTrade
    } catch (err) {
      saveError.value = getErrorMessage(err)
      const fieldErrors = getFieldErrors(err)
      console.error('Failed to patch trade:', err)
      throw { message: saveError.value, fieldErrors }
    } finally {
      saveLoading.value = false
    }
  }

  const deleteTrade = async (id) => {
    saveLoading.value = true
    saveError.value = null
    
    try {
      await tradingApi.deleteTrade(id)
      
      // Refresh pivot data after deleting trade
      if (selectedCustomer.value && selectedYear.value) {
        await fetchPivotData(selectedCustomer.value, selectedYear.value)
      }
      
      return true
    } catch (err) {
      saveError.value = getErrorMessage(err)
      console.error('Failed to delete trade:', err)
      throw err
    } finally {
      saveLoading.value = false
    }
  }

  const setSelectedCustomer = (customerId) => {
    selectedCustomer.value = customerId
  }

  const setSelectedYear = (year) => {
    selectedYear.value = year
  }

  const clearPivotData = () => {
    pivotData.value = null
    selectedCustomer.value = null
    selectedYear.value = new Date().getFullYear()
    error.value = null
  }

  return {
    // State
    selectedCustomer,
    selectedYear,
    pivotData,
    trades,
    loading,
    error,
    saveError,
    saveLoading,
    
    // Getters
    hasPivotData,
    currentMonthData,
    totalBooked,
    averagePrice,
    getMonthData,
    
    // Actions
    fetchPivotData,
    fetchPivotDataByMprn,
    fetchTrades,
    createTrade,
    updateTrade,
    patchTrade,
    deleteTrade,
    setSelectedCustomer,
    setSelectedYear,
    clearPivotData,
  }
})
