import api from './client'

export const customerApi = {
  list() {
    return api.get('/customers/')
  },

  get(mprn) {
    return api.get(`/customers/${mprn}/`)
  },

  create(data) {
    return api.post('/customers/', data)
  },

  update(mprn, data) {
    return api.put(`/customers/${mprn}/`, data)
  },
}
