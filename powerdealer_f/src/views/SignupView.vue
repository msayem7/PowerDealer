<template>
  <div class="signup-container">
    <h1>Sign Up</h1>
    <form @submit.prevent="handleSignup">
      <div class="form-group">
        <label for="username">Username:</label>
        <input v-model="form.username" type="text" id="username" required />
      </div>

      <div class="form-group">
        <label for="email">Email:</label>
        <input v-model="form.email" type="email" id="email" required />
      </div>

      <div class="form-group">
        <label for="password">Password:</label>
        <input v-model="form.password" type="password" id="password" required />
      </div>

      <div class="form-group">
        <label for="business_name">Business Name:</label>
        <input v-model="form.business_name" type="text" id="business_name" required />
      </div>

      <div v-if="error" class="error">{{ error }}</div>

      <button type="submit" :disabled="loading">
        {{ loading ? 'Signing up...' : 'Sign Up' }}
      </button>

      <p>Already have an account? <router-link to="/login">Login</router-link></p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  username: '',
  email: '',
  password: '',
  business_name: '',
})

const loading = ref(false)
const error = ref(null)

const handleSignup = async () => {
  loading.value = true
  error.value = null
  try {
    await authStore.signup(form.value)
    router.push('/dashboard')
  } catch (err) {
    error.value = err.response?.data || 'Signup failed'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.signup-container {
  max-width: 500px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

h1 {
  text-align: center;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
}

button {
  width: 100%;
  padding: 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error {
  color: red;
  margin-bottom: 10px;
}

p {
  text-align: center;
  margin-top: 15px;
}

a {
  color: #007bff;
  text-decoration: none;
}
</style>
