import api from './client'
import { getErrorMessage, getFieldErrors } from './client'

/**
 * Trading API client for managing trades and pivot data
 */
export const tradingApi = {
  /**
   * Get pivot data for a customer for a specific year
   * @param {string} mprn - Customer MPRN (10 digits)
   * @param {number} year - Year
   * @returns {Promise} - API response with pivot data
   */
  getTradingPivot(mprn, year) {
    console.log('[API] getTradingPivot called:', { mprn, year })
    return api.get('/trading/pivot/', {
      params: { mprn: mprn, year }
    })
  },

  /**
   * Get pivot data for a customer by MPRN for a specific year
   * @param {string} mprn - Customer MPRN (10 digits)
   * @param {number} year - Year
   * @returns {Promise} - API response with pivot data
   */
  getTradingPivotByMprn(mprn, year) {
    console.log('[API] getTradingPivotByMprn called:', { mprn, year })
    return api.get('/trading/pivot/', {
      params: { mprn: mprn, year }
    })
  },

  /**
   * Get list of trades with optional filters
   * @param {Object} filters - Filter options
   * @param {number} [filters.customerId] - Filter by customer ID
   * @param {number} [filters.month] - Filter by month (1-12)
   * @param {number} [filters.year] - Filter by year
   * @returns {Promise} - API response with trades list
   */
  getTrades(filters = {}) {
    const params = {}
    if (filters.customerId) params.customer_id = filters.customerId
    if (filters.month) params.month = filters.month
    if (filters.year) params.year = filters.year
    
    return api.get('/trades/', { params })
  },

  /**
   * Create a new trade
   * @param {Object} data - Trade data
   * @param {number} data.customer_id - Customer ID
   * @param {number} data.month - Month (1-12)
   * @param {number} data.year - Year
   * @param {number} data.p_therm - Price per thermal unit
   * @param {number} data.percent - Percentage
   * @param {string} data.trade_date - Trade date (YYYY-MM-DD)
   * @returns {Promise} - API response with created trade
   */
  createTrade(data) {
    return api.post('/trades/', data)
  },

  /**
   * Update an existing trade (full update)
   * @param {number} id - Trade ID
   * @param {Object} data - Trade data to update
   * @returns {Promise} - API response with updated trade
   */
  updateTrade(id, data) {
    return api.put(`/trades/${id}/`, data)
  },

  /**
   * Partially update a trade
   * @param {number} id - Trade ID
   * @param {Object} data - Trade data to update
   * @returns {Promise} - API response with updated trade
   */
  patchTrade(id, data) {
    return api.patch(`/trades/${id}/`, data)
  },

  /**
   * Delete a trade
   * @param {number} id - Trade ID
   * @returns {Promise} - API response
   */
  deleteTrade(id) {
    return api.delete(`/trades/${id}/`)
  },

  /**
   * Get a single trade by ID
   * @param {number} id - Trade ID
   * @returns {Promise} - API response with trade data
   */
  getTrade(id) {
    return api.get(`/trades/${id}/`)
  }
}

/**
 * Helper to extract data from standard API response format
 * @param {Object} response - Axios response
 * @returns {Object} - Data or throws error
 */
export const extractTradingData = (response) => {
  if (response.data.success) {
    return response.data.data
  }
  const error = new Error(response.data.message)
  error.response = response
  throw error
}

export { getErrorMessage, getFieldErrors }
