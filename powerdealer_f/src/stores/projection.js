import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { projectionApi, extractProjectionData, getErrorMessage, getFieldErrors } from '../api/projection'

export const useProjectionStore = defineStore('projection', () => {
  // State
  const selectedMprn = ref(null)
  const selectedYear = ref(new Date().getFullYear())
  const projectionRows = ref([])
  const loading = ref(false)
  const error = ref(null)
  const saveError = ref(null)
  const saveLoading = ref(false)
  const originalRows = ref([])

  // Getters
  const isLoaded = computed(() => projectionRows.value.length === 12)

  const hasUnsavedChanges = computed(() => {
    if (!isLoaded.value || originalRows.value.length === 0) return false
    return JSON.stringify(projectionRows.value) !== JSON.stringify(originalRows.value)
  })

  const getRowByMonth = (month) => {
    return projectionRows.value.find(row => row.month === month)
  }

  // Actions
  const fetchProjection = async (mprn, year) => {
    console.log('[Projection Store] fetchProjection called with:', { mprn, year })
    
    if (!mprn || !year) {
      console.warn('[Projection Store] Missing mprn or year, skipping fetch')
      error.value = 'MPRN and year are required'
      return null
    }

    loading.value = true
    error.value = null
    
    try {
      console.log('[Projection Store] Making API call to /projection/')
      const response = await projectionApi.getProjection(mprn, year)
      console.log('[Projection Store] API response received:', response.data)
      
      const data = extractProjectionData(response)
      console.log('[Projection Store] Extracted data:', data)
      
      selectedMprn.value = mprn
      selectedYear.value = year
      projectionRows.value = data.rows || []
      
      // Store original rows for change detection
      originalRows.value = JSON.parse(JSON.stringify(projectionRows.value))
      
      return data
    } catch (err) {
      console.error('[Projection Store] Failed to fetch projection:', err)
      error.value = getErrorMessage(err)
      console.error('Failed to fetch projection:', err)
      return null
    } finally {
      loading.value = false
    }
  }

  const saveProjection = async () => {
    if (!selectedMprn.value || !selectedYear.value) {
      saveError.value = 'MPRN and year are required'
      return null
    }

    saveLoading.value = true
    saveError.value = null
    
    try {
      const payload = {
        mprn: selectedMprn.value,
        year: selectedYear.value,
        projections: projectionRows.value.map(row => ({
          month: row.month,
          st_charge: row.st_charge || 0,
          consumption: row.consumption || 0,
          flex_rate: row.flex_rate || 0
        }))
      }
      
      console.log('[Projection Store] Saving projection:', payload)
      const response = await projectionApi.saveProjection(payload)
      const data = extractProjectionData(response)
      
      // Update original rows after successful save
      originalRows.value = JSON.parse(JSON.stringify(projectionRows.value))
      
      console.log('[Projection Store] Projection saved successfully:', data)
      return data
    } catch (err) {
      console.error('[Projection Store] Failed to save projection:', err)
      saveError.value = getErrorMessage(err)
      const fieldErrors = getFieldErrors(err)
      console.error('Failed to save projection:', err)
      throw { message: saveError.value, fieldErrors }
    } finally {
      saveLoading.value = false
    }
  }

  /**
   * Recalculate cost for a specific row based on current values
   * Formula: Cost (£) = (St Charge p/day × No of Days / 100) + 
   *                   (Consumption (kWh) × (Flex Unit Rate + Traded Price / 29.3071) / 100)
   */
  const recalculateCost = (rowIndex) => {
    const row = projectionRows.value[rowIndex]
    if (!row) return

    const noOfDays = row.no_of_days || 0
    const stCharge = parseFloat(row.st_charge) || 0
    const consumption = parseFloat(row.consumption) || 0
    const flexRate = parseFloat(row.flex_rate) || 0
    const tradedPrice = parseFloat(row.traded_price) || 0

    // Therm to kWh conversion factor
    const thermToKwhFactor = 29.3071

    // Calculate standing charge component (pence to pounds)
    const stChargeComponent = (stCharge * noOfDays) / 100

    // Calculate unit consumption component
    const tradedPricePerKwh = tradedPrice / thermToKwhFactor
    const unitComponent = (consumption * (flexRate + tradedPricePerKwh)) / 100

    // Total cost
    const totalCost = stChargeComponent + unitComponent
    
    // Update the row cost (rounded to 2 decimal places)
    projectionRows.value[rowIndex].cost = Math.round(totalCost * 100) / 100
  }

  /**
   * Update a specific field in a row and recalculate cost
   */
  const updateRowField = (rowIndex, field, value) => {
    if (rowIndex < 0 || rowIndex >= projectionRows.value.length) return

    // Validate non-negative values
    if (field !== 'month' && value < 0) {
      console.warn(`[Projection Store] Negative value not allowed for ${field}`)
      return
    }

    // Apply decimal place limits based on field
    let processedValue = value
    if (field === 'st_charge') {
      // Max 2 decimal places
      processedValue = Math.round(value * 100) / 100
    } else if (field === 'flex_rate') {
      // Max 8 decimal places
      processedValue = Math.round(value * 100000000) / 100000000
    }

    projectionRows.value[rowIndex][field] = processedValue

    // Recalculate cost if the field affects it
    if (field === 'st_charge' || field === 'consumption' || field === 'flex_rate') {
      recalculateCost(rowIndex)
    }
  }

  const clearProjection = () => {
    selectedMprn.value = null
    selectedYear.value = new Date().getFullYear()
    projectionRows.value = []
    originalRows.value = []
    error.value = null
    saveError.value = null
  }

  const setSelectedMprn = (mprn) => {
    selectedMprn.value = mprn
  }

  const setSelectedYear = (year) => {
    selectedYear.value = year
  }

  return {
    // State
    selectedMprn,
    selectedYear,
    projectionRows,
    loading,
    error,
    saveError,
    saveLoading,
    
    // Getters
    isLoaded,
    hasUnsavedChanges,
    getRowByMonth,
    
    // Actions
    fetchProjection,
    saveProjection,
    recalculateCost,
    updateRowField,
    clearProjection,
    setSelectedMprn,
    setSelectedYear,
  }
})
