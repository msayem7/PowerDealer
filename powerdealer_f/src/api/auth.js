import api from './client'

export const authApi = {
  signup(data) {
    return api.post('/auth/signup/', data)
  },

  login(username, password) {
    return api.post('/auth/login/', { username, password })
  },

  getMe() {
    return api.get('/auth/me/')
  },

  getBusiness() {
    return api.get('/business/')
  },

  updateBusiness(data) {
    return api.put('/business/', data)
  },
}
