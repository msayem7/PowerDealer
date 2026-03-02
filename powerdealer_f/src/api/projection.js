import api from './client'
import { getErrorMessage, getFieldErrors } from './client'

/**
 * Projection API client for managing cost projections
 */
export const projectionApi = {
  /**
   * Get projection data for a customer for a specific year
   * @param {string} mprn - Customer MPRN (10 digits)
   * @param {number} year - Year
   * @returns {Promise} - API response with projection data
   */
  getProjection(mprn, year) {
    console.log('[API] getProjection called:', { mprn, year })
    return api.get('/projection/', {
      params: { mprn: mprn, year }
    })
  },

  /**
   * Save projection data for 12 months
   * @param {Object} data - Projection data
   * @param {string} data.mprn - Customer MPRN
   * @param {number} data.year - Year
   * @param {Array} data.projections - Array of 12 projection rows
   * @returns {Promise} - API response
   */
  saveProjection(data) {
    console.log('[API] saveProjection called:', data)
    return api.post('/projection/', data)
  },

  /**
   * Get a single projection by ID
   * @param {number} id - Projection ID
   * @returns {Promise} - API response with projection data
   */
  getProjectionById(id) {
    return api.get(`/projection/${id}/`)
  },

  /**
   * Update a single projection
   * @param {number} id - Projection ID
   * @param {Object} data - Projection data
   * @returns {Promise} - API response
   */
  updateProjection(id, data) {
    return api.put(`/projection/${id}/`, data)
  },

  /**
   * Partially update a projection
   * @param {number} id - Projection ID
   * @param {Object} data - Projection data
   * @returns {Promise} - API response
   */
  patchProjection(id, data) {
    return api.patch(`/projection/${id}/`, data)
  },

  /**
   * Delete a projection
   * @param {number} id - Projection ID
   * @returns {Promise} - API response
   */
  deleteProjection(id) {
    return api.delete(`/projection/${id}/`)
  }
}

/**
 * Helper to extract data from standard API response format
 * @param {Object} response - Axios response
 * @returns {Object} - Data or throws error
 */
export const extractProjectionData = (response) => {
  if (response.data.success) {
    return response.data.data
  }
  const error = new Error(response.data.message)
  error.response = response
  throw error
}

export { getErrorMessage, getFieldErrors }
