<template>
  <div class="create-customer-container">
    <header>
      <h1>Add Customer</h1>
    </header>

    <form @submit.prevent="handleSubmit" class="customer-form">
      <div class="form-section">
        <h3>Personal Information</h3>
        <div class="form-group">
          <label for="first_name">First Name *</label>
          <input
            v-model="form.first_name"
            type="text"
            id="first_name"
            required
          />
          <span v-if="errors.first_name" class="field-error">{{ errors.first_name }}</span>
        </div>

        <div class="form-group">
          <label for="last_name">Last Name *</label>
          <input
            v-model="form.last_name"
            type="text"
            id="last_name"
            required
          />
          <span v-if="errors.last_name" class="field-error">{{ errors.last_name }}</span>
        </div>

        <div class="form-group">
          <label for="email">Email *</label>
          <input
            v-model="form.email"
            type="email"
            id="email"
            required
          />
          <span v-if="errors.email" class="field-error">{{ errors.email }}</span>
        </div>

        <div class="form-group">
          <label for="password">Password *</label>
          <input
            v-model="form.password"
            type="password"
            id="password"
            required
            minlength="6"
          />
          <span v-if="errors.password" class="field-error">{{ errors.password }}</span>
        </div>
      </div>

      <div class="form-section">
        <h3>Customer Details</h3>
        <div class="form-group">
          <label for="mobile">Mobile *</label>
          <input
            v-model="form.mobile"
            type="text"
            id="mobile"
            required
          />
          <span v-if="errors.mobile" class="field-error">{{ errors.mobile }}</span>
        </div>

        <div class="form-group">
          <label for="mprn">MPRN * (10 digits)</label>
          <input
            v-model="form.mprn"
            type="text"
            id="mprn"
            required
            maxlength="10"
            pattern="^\d{10}$"
          />
          <span v-if="errors.mprn" class="field-error">{{ errors.mprn }}</span>
        </div>

        <div class="form-group">
          <label for="address">Address</label>
          <textarea
            v-model="form.address"
            id="address"
            rows="3"
          ></textarea>
          <span v-if="errors.address" class="field-error">{{ errors.address }}</span>
        </div>
      </div>

      <div v-if="submitError" class="form-error">
        {{ submitError }}
      </div>

      <div class="form-actions">
        <button type="button" @click="goBack" class="cancel-btn">Cancel</button>
        <button type="submit" :disabled="customerStore.loading" class="submit-btn">
          {{ customerStore.loading ? 'Creating...' : 'Create Customer' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useCustomerStore } from '../stores/customer'
import { getFieldErrors } from '../api/client'

const router = useRouter()
const customerStore = useCustomerStore()

const form = reactive({
  first_name: '',
  last_name: '',
  email: '',
  password: '',
  mobile: '',
  mprn: '',
  address: '',
})

const errors = ref({})
const submitError = ref('')

const goBack = () => {
  router.push('/customers')
}

const handleSubmit = async () => {
  errors.value = {}
  submitError.value = ''

  try {
    await customerStore.createCustomer(form)
    router.push('/customers')
  } catch (err) {
    const fieldErrors = getFieldErrors(err)
    if (Object.keys(fieldErrors).length > 0) {
      errors.value = fieldErrors
    } else {
      submitError.value = err.response?.data?.message || 'Failed to create customer'
    }
  }
}
</script>

<style scoped>
.create-customer-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

header {
  margin-bottom: 30px;
}

header h1 {
  margin: 0;
  color: #333;
}

.customer-form {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.form-section {
  margin-bottom: 30px;
}

.form-section h3 {
  margin: 0 0 20px 0;
  color: #555;
  font-size: 16px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #333;
}

input,
textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
  font-family: inherit;
}

input:focus,
textarea:focus {
  outline: none;
  border-color: #007bff;
}

.field-error {
  display: block;
  color: #dc3545;
  font-size: 12px;
  margin-top: 5px;
}

.form-error {
  padding: 15px;
  background-color: #ffe6e6;
  color: #dc3545;
  border-radius: 4px;
  margin-bottom: 20px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.cancel-btn {
  padding: 10px 20px;
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.cancel-btn:hover {
  background-color: #5a6268;
}

.submit-btn {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.submit-btn:hover {
  background-color: #0056b3;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
