<template>
  <div class="customers-container">
    <header>
      <h1>Customers</h1>
      <router-link to="/customers/create" class="add-btn">Add Customer</router-link>
    </header>

    <div v-if="customerStore.loading && !customerStore.customers.length" class="loading">
      Loading customers...
    </div>

    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else class="content">
      <!-- Search -->
      <div class="search-bar">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search by name, email, MPRN, or mobile..."
          class="search-input"
        />
      </div>

      <!-- Empty state -->
      <div v-if="!customerStore.customers.length" class="empty-state">
        <p>No customers found. Add your first customer to get started.</p>
        <router-link to="/customers/create" class="add-btn">Add Customer</router-link>
      </div>

      <!-- Table -->
      <table v-else class="customers-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Mobile</th>
            <th>MPRN</th>
            <th>Status</th>
            <th>Created</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="customer in filteredCustomers" :key="customer.mprn">
            <td>{{ getFullName(customer.user) }}</td>
            <td>{{ customer.user?.email }}</td>
            <td>{{ customer.mobile }}</td>
            <td>{{ customer.mprn }}</td>
            <td>
              <span :class="['status-badge', customer.is_active ? 'active' : 'inactive']">
                {{ customer.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td>{{ formatDate(customer.created_at) }}</td>
            <td>
              <router-link :to="`/customers/${customer.mprn}/edit`" class="edit-link">
                Edit
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useCustomerStore } from '../stores/customer'

const customerStore = useCustomerStore()
const searchQuery = ref('')

const error = computed(() => customerStore.error)

const filteredCustomers = computed(() => {
  if (!searchQuery.value) {
    return customerStore.customers
  }
  const query = searchQuery.value.toLowerCase()
  return customerStore.customers.filter(customer => {
    const fullName = getFullName(customer.user).toLowerCase()
    const email = customer.user?.email?.toLowerCase() || ''
    return (
      fullName.includes(query) ||
      email.includes(query) ||
      customer.mobile?.includes(query) ||
      customer.mprn?.includes(query)
    )
  })
})

const getFullName = (user) => {
  if (!user) return ''
  return `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.username
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString()
}

onMounted(async () => {
  try {
    await customerStore.fetchCustomers()
  } catch (err) {
    console.error('Failed to load customers')
  }
})
</script>

<style scoped>
.customers-container {
  max-width: 1100px;
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

header h1 {
  margin: 0;
  color: #333;
}

.add-btn {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  font-size: 14px;
}

.add-btn:hover {
  background-color: #0056b3;
}

.search-bar {
  margin-bottom: 20px;
}

.search-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
}

.loading,
.error,
.empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
}

.error {
  color: red;
  background-color: #ffe6e6;
  border-radius: 4px;
}

.customers-table {
  width: 100%;
  border-collapse: collapse;
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.customers-table th,
.customers-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.customers-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #555;
}

.customers-table tr:hover {
  background-color: #f9f9f9;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background-color: #d4edda;
  color: #155724;
}

.status-badge.inactive {
  background-color: #f8d7da;
  color: #721c24;
}

.edit-link {
  color: #007bff;
  text-decoration: none;
  font-size: 14px;
}

.edit-link:hover {
  text-decoration: underline;
}
</style>
