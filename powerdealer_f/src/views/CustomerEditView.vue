<template>
  <div class="edit-customer-container">
    <header>
      <h1>Edit Customer</h1>
    </header>

    <div v-if="customerStore.loading && !customerStore.customer" class="loading">
      Loading customer...
    </div>

    <div v-else-if="loadError" class="error">{{ loadError }}</div>

    <form v-else @submit.prevent="handleSubmit" class="customer-form">
      <div class="form-section">
        <h3>Personal Information</h3>
        <div class="form-group">
          <label for="name">Customer Name *</label>
          <input
            v-model="form.name"
            type="text"
            id="name"
            required
          />
          <span v-if="errors.name" class="field-error">{{ errors.name }}</span>
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
      </div>

      <div class="form-section">
        <h3>Customer Details</h3>
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
          <label for="mobile">Mobile</label>
          <input
            v-model="form.mobile"
            type="text"
            id="mobile"
          />
          <span v-if="errors.mobile" class="field-error">{{ errors.mobile }}</span>
        </div>

        <div class="form-group">
          <label for="address">Address</label>
          <textarea
            v-model="form.address"
            id="address"
            rows="2"
          ></textarea>
          <span v-if="errors.address" class="field-error">{{ errors.address }}</span>
        </div>

        <div class="form-group">
          <label>
            <input
              v-model="form.is_active"
              type="checkbox"
            />
            Active Customer
          </label>
        </div>
      </div>

      <div v-if="submitError" class="form-error">
        {{ submitError }}
      </div>

      <div class="form-actions">
        <button type="button" @click="goBack" class="cancel-btn">Cancel</button>
        <button type="submit" :disabled="customerStore.loading" class="submit-btn">
          {{ customerStore.loading ? 'Saving...' : 'Save Changes' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useCustomerStore } from '../stores/customer'
import { getFieldErrors } from '../api/client'

const router = useRouter()
const route = useRoute()
const customerStore = useCustomerStore()

const mprn = route.params.mprn

const form = reactive({
  name: '',
  email: '',
  mobile: '',
  mprn: '',
  address: '',
  is_active: true,
})

const errors = ref({})
const submitError = ref('')
const loadError = ref('')

const goBack = () => {
  router.push('/customers')
}

const handleSubmit = async () => {
  errors.value = {}
  submitError.value = ''

  try {
    await customerStore.updateCustomer(mprn, form)
    router.push('/customers')
  } catch (err) {
    const fieldErrors = getFieldErrors(err)
    if (Object.keys(fieldErrors).length > 0) {
      errors.value = fieldErrors
    } else {
      submitError.value = err.response?.data?.message || 'Failed to update customer'
    }
  }
}

onMounted(async () => {
  try {
    await customerStore.fetchCustomer(mprn)
    const customer = customerStore.customer
    if (customer && customer.user) {
      form.name = customer.user.first_name || ''  // Using first_name to store full name
      form.email = customer.user.email || ''
      form.mobile = customer.mobile || ''
      form.mprn = customer.mprn || ''
      form.address = customer.address || ''
      form.is_active = customer.is_active
    }
  } catch (err) {
    loadError.value = 'Failed to load customer. The customer may not exist.'
  }
})
</script>

<style scoped>
.edit-customer-container {
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

.loading,
.error {
  text-align: center;
  padding: 40px;
  color: #666;
}

.error {
  color: red;
  background-color: #ffe6e6;
  border-radius: 4px;
}

.customer-form {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.form-section {
  margin-bottom: 25px;
}

.form-section h3 {
  margin: 0 0 15px 0;
  color: #555;
  font-size: 16px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #333;
  font-size: 13px;
}

input[type="text"],
input[type="email"],
textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 13px;
  font-family: inherit;
}

input:focus,
textarea:focus {
  outline: none;
  border-color: #007bff;
}

input[type="checkbox"] {
  margin-right: 8px;
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
  padding: 8px 16px;
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}

.cancel-btn:hover {
  background-color: #5a6268;
}

.submit-btn {
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}

.submit-btn:hover {
  background-color: #0056b3;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
