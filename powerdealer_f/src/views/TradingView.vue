<template>
  <div class="trading-view">
    <header class="view-header">
      <h1 class="view-title">Trading Management</h1>
      <p class="view-subtitle">Manage your monthly trading  entries</p>
    </header>
    
    <!-- Filters -->
    <div class="filters-bar">
      <div class="filter-group">
        <label for="customer-select">Customer</label>
        <select 
          id="customer-select"
          v-model="selectedMprn"
          :disabled="customerLoading"
          class="filter-select"
        >
          <option :value="undefined" disabled>Select a customer</option>
          <option 
            v-for="customer in customers" 
            :key="customer.mprn" 
            :value="customer.mprn"
          >
            {{ getCustomerName(customer) }} ({{ customer.mprn }})
          </option>
        </select>
      </div>

      <div class="filter-group">
        <label for="year-select">Year</label>
        <select 
          id="year-select"
          v-model="selectedYear"
          class="filter-select"
        >
          <option v-for="year in availableYears" :key="year" :value="year">
            {{ year }}
          </option>
        </select>
      </div>

      <div class="filter-actions" v-if="selectedMprn && selectedYear">
        <button 
          class="refresh-btn"
          @click="refreshData"
          :disabled="loading"
        >
          <svg viewBox="0 0 24 24" fill="none" class="refresh-icon" :class="{ 'spinning': loading }">
            <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z" fill="currentColor"/>
          </svg>
          Refresh
        </button>
      </div>
    </div>

    <!-- Loading Customers -->
    <div v-if="customerLoading" class="loading-customers">
      <div class="spinner-small"></div>
      <span>Loading customers...</span>
    </div>

    <!-- Customer Error -->
    <div v-else-if="customerError" class="error-bar">
      <span>{{ customerError }}</span>
      <button @click="loadCustomers" class="retry-link">Retry</button>
    </div>

    <!-- Trading Pivot Grid -->
    <div class="view-content" v-else>
      <TradingPivotGrid 
        v-if="selectedMprn && selectedYear"
        :mprn="selectedMprn"
        :year="selectedYear"
        @retry="refreshData"
        @trade-created="onTradeCreated"
        @trade-updated="onTradeUpdated"
        @trade-deleted="onTradeDeleted"
      />
      
      <div v-else class="no-selection">
        <svg viewBox="0 0 24 24" fill="none" class="no-selection-icon">
          <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z" fill="currentColor"/>
        </svg>
        <p>Select a customer and year to view trading data</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useCustomerStore } from '../stores/customer'
import { useTradingStore } from '../stores/trading'
import TradingPivotGrid from '../components/trading/TradingPivotGrid.vue'

// Stores
const customerStore = useCustomerStore()
const tradingStore = useTradingStore()

// Local state
const selectedMprn = ref(null)
const selectedYear = ref(new Date().getFullYear())

// Computed
const customers = computed(() => customerStore.customers)
const customerLoading = computed(() => customerStore.loading)
const customerError = computed(() => customerStore.error)
const loading = computed(() => tradingStore.loading)

const availableYears = computed(() => {
  const currentYear = new Date().getFullYear()
  const years = []
  for (let i = currentYear - 2; i <= currentYear + 1; i++) {
    years.push(i)
  }
  return years
})

// Methods
const getCustomerName = (customer) => {
  if (customer.user) {
    const name = customer.user.first_name || ''  // Full name stored in first_name
    return name || customer.user.username
  }
  return customer.user?.username || 'Unknown'
}

const loadCustomers = async () => {
  try {
    await customerStore.fetchCustomers()
  } catch (err) {
    console.error('Failed to load customers:', err)
  }
}

// Watch for customer/year changes to fetch pivot data
watch([selectedMprn, selectedYear], ([newMprn, newYear]) => {
  console.log('[TradingView] Watch triggered:', { newMprn, newYear })
  if (newMprn && newYear) {
    console.log('[TradingView] Calling fetchPivotData from watch')
    // Use mprn instead of customer_id since id is not exposed by backend
    tradingStore.fetchPivotDataByMprn(newMprn, newYear)
  }
})

const refreshData = () => {
  console.log('[TradingView] Refresh data called')
  if (selectedMprn.value && selectedYear.value) {
    console.log('[TradingView] Calling fetchPivotData from refreshData')
    tradingStore.fetchPivotDataByMprn(selectedMprn.value, selectedYear.value)
  }
}

const onTradeCreated = () => {
  console.log('Trade created successfully')
}

const onTradeUpdated = () => {
  console.log('Trade updated successfully')
}

const onTradeDeleted = () => {
  console.log('Trade deleted successfully')
}

// Lifecycle
onMounted(() => {
  loadCustomers()
})
</script>

<style scoped>
.trading-view {
  padding: 24px;
}

.view-header {
  margin-bottom: 24px;
}

.view-title {
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 8px 0;
}

.view-subtitle {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin: 0;
}

.filters-bar {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  margin-bottom: 20px;
  padding: 16px;
  background-color: var(--color-surface);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.filter-select {
  min-width: 250px;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-size: 0.875rem;
  background-color: white;
  color: var(--color-text-primary);
  cursor: pointer;
}

.filter-select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.filter-select:disabled {
  background-color: var(--color-background);
  cursor: not-allowed;
}

.filter-actions {
  margin-left: auto;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.refresh-btn:hover:not(:disabled) {
  background-color: #2563eb;
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.refresh-icon {
  width: 18px;
  height: 18px;
}

.refresh-icon.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-customers {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 24px;
  color: var(--color-text-secondary);
}

.spinner-small {
  width: 20px;
  height: 20px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.error-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  color: #991b1b;
  font-size: 0.875rem;
}

.retry-link {
  background: none;
  border: none;
  color: #dc2626;
  text-decoration: underline;
  cursor: pointer;
  font-size: 0.875rem;
}

.view-content {
  background-color: var(--color-surface);
  border-radius: var(--border-radius-lg);
  padding: 24px;
  border: 1px solid var(--color-border);
}

.no-selection {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px;
  color: var(--color-text-secondary);
  text-align: center;
}

.no-selection-icon {
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.no-selection p {
  margin: 0;
  font-size: 1rem;
}
</style>
