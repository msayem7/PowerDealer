<template>
  <div class="dashboard-container">
    <header>
      <h1>Dashboard</h1>
      <button @click="handleLogout" class="logout-btn">Logout</button>
    </header>

    <div v-if="!authStore.isAuthenticated" class="not-authenticated">
      <p>Please login to access your dashboard.</p>
    </div>

    <div v-else class="dashboard-content">
      <div class="user-info">
        <h2>Welcome, {{ authStore.user?.username }}!</h2>
      </div>

      <div class="business-section">
        <h2>Your Business</h2>

        <div v-if="businessStore.loading" class="loading">Loading...</div>

        <div v-else-if="businessStore.business" class="business-card">
          <h3>{{ businessStore.business.name }}</h3>
          <p><strong>Email:</strong> {{ businessStore.business.email }}</p>
          <p><strong>Phone:</strong> {{ businessStore.business.phone }}</p>
          <p><strong>Description:</strong> {{ businessStore.business.description }}</p>
          <p><strong>Address:</strong> {{ businessStore.business.address }}</p>
          <p><strong>Created:</strong> {{ new Date(businessStore.business.created_at).toLocaleDateString() }}</p>

          <button @click="toggleEdit" class="edit-btn">
            {{ isEditing ? 'Cancel' : 'Edit' }}
          </button>

          <div v-if="isEditing" class="edit-form">
            <h4>Edit Business Information</h4>
            <div class="form-group">
              <label for="name">Business Name:</label>
              <input v-model="editForm.name" type="text" id="name" />
            </div>

            <div class="form-group">
              <label for="email">Email:</label>
              <input v-model="editForm.email" type="email" id="email" />
            </div>

            <div class="form-group">
              <label for="phone">Phone:</label>
              <input v-model="editForm.phone" type="text" id="phone" />
            </div>

            <div class="form-group">
              <label for="description">Description:</label>
              <textarea v-model="editForm.description" id="description"></textarea>
            </div>

            <div class="form-group">
              <label for="address">Address:</label>
              <textarea v-model="editForm.address" id="address"></textarea>
            </div>

            <div v-if="editError" class="error">{{ editError }}</div>

            <button @click="handleUpdate" :disabled="businessStore.loading" class="save-btn">
              {{ businessStore.loading ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </div>

        <div v-else class="loading">No business found</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useBusinessStore } from '../stores/business'

const router = useRouter()
const authStore = useAuthStore()
const businessStore = useBusinessStore()

const isEditing = ref(false)
const editError = ref(null)
const editForm = ref({
  name: '',
  email: '',
  phone: '',
  description: '',
  address: '',
})

onMounted(() => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
  } else {
    loadBusiness()
  }
})

const loadBusiness = async () => {
  try {
    await businessStore.fetchBusiness()
    if (businessStore.business) {
      editForm.value = {
        name: businessStore.business.name,
        email: businessStore.business.email,
        phone: businessStore.business.phone,
        description: businessStore.business.description,
        address: businessStore.business.address,
      }
    }
  } catch (err) {
    console.error('Failed to load business')
  }
}

const toggleEdit = () => {
  isEditing.value = !isEditing.value
  editError.value = null
}

const handleUpdate = async () => {
  editError.value = null
  try {
    await businessStore.updateBusiness(editForm.value)
    isEditing.value = false
  } catch (err) {
    editError.value = err.response?.data || 'Failed to update business'
  }
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.dashboard-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #ddd;
}

.logout-btn {
  padding: 8px 16px;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.logout-btn:hover {
  background-color: #c82333;
}

.dashboard-content {
  margin-top: 20px;
}

.user-info h2 {
  color: #333;
}

.business-section {
  margin-top: 30px;
}

.business-card {
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #f9f9f9;
}

.business-card h3 {
  margin-top: 0;
  color: #007bff;
}

.business-card p {
  margin: 10px 0;
  line-height: 1.6;
}

.edit-btn {
  margin-top: 15px;
  padding: 10px 20px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.edit-btn:hover {
  background-color: #218838;
}

.edit-form {
  margin-top: 20px;
  padding: 20px;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.edit-form h4 {
  margin-top: 0;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

input,
textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
  font-family: inherit;
}

.save-btn {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error {
  color: red;
  margin-bottom: 10px;
  padding: 10px;
  background-color: #ffe6e6;
  border-radius: 4px;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}

.not-authenticated {
  text-align: center;
  padding: 40px;
  color: #666;
}
</style>
