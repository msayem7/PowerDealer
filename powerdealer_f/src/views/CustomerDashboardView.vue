<template>
  <div class="customer-dashboard">
    <!-- Access Denied Message -->
    <div v-if="accessDenied" class="access-denied">
      <svg viewBox="0 0 24 24" fill="none" class="denied-icon">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" fill="currentColor"/>
      </svg>
      <h2>Access Denied</h2>
      <p>{{ accessDeniedMessage }}</p>
    </div>

    <!-- Dashboard Content -->
    <div v-else-if="!loading && customerData" class="dashboard-content">
      <!-- Dashboard Header -->
      <header class="dashboard-header">
        <div class="header-info">
          <div class="header-left">
            <h1 class="customer-name">Welcome, {{ customerName }}</h1>
            <span class="mprn-badge">MPRN: {{ formattedMprn }}</span>
          </div>
          <div class="header-actions">
            <button 
              class="tab-icon-btn" 
              :class="{ active: activeTab === 'trading' }"
              @click="activeTab = 'trading'"
              title="Trading Status"
            >
              <svg viewBox="0 0 24 24" fill="none" class="tab-icon">
                <path d="M3 13h2v8H3v-8zm4-5h2v13H7V8zm4-5h2v18h-2V3zm4 8h2v10h-2V11zm4-3h2v13h-2V8z" fill="currentColor"/>
              </svg>
              <span class="tab-icon-label">Trading</span>
            </button>
            <button 
              class="tab-icon-btn" 
              :class="{ active: activeTab === 'projection' }"
              @click="activeTab = 'projection'"
              title="Projection Data & Calculator"
            >
              <svg viewBox="0 0 24 24" fill="none" class="tab-icon">
                <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 14H6v-2h6v2zm4-4H6v-2h10v2zm0-4H6V7h10v2z" fill="currentColor"/>
              </svg>
              <span class="tab-icon-label">Projection</span>
            </button>
          </div>
        </div>
      </header>

      <!-- Tab Content -->
      <div class="tab-content">
        <!-- Trading Status Tab -->
        <div v-if="activeTab === 'trading'" class="trading-tab">
          <div class="tab-header">
            <h2>Trading Status</h2>
            <div class="year-selector">
              <label for="trading-year">Year:</label>
              <select 
                id="trading-year" 
                v-model="selectedTradingYear"
                @change="loadTradingData"
                :disabled="tradingLoading"
              >
                <option v-for="year in tradingYears" :key="year" :value="year">
                  {{ year }}
                </option>
              </select>
            </div>
          </div>

          <!-- Trading Loading -->
          <div v-if="tradingLoading" class="loading-state">
            <div class="spinner"></div>
            <p>Loading trading data...</p>
          </div>

          <!-- Trading Error -->
          <div v-else-if="tradingError" class="error-message">
            <svg viewBox="0 0 24 24" fill="none" class="error-icon">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" fill="currentColor"/>
            </svg>
            <p>{{ tradingError }}</p>
            <button @click="loadTradingData" class="retry-button">Retry</button>
          </div>

          <!-- Trading Data -->
          <div v-else-if="tradingData" class="trading-grid-container">
            <table class="pivot-table">
              <thead>
                <tr class="header-row">
                  <th class="header-cell" rowspan="2">Month</th>
                  <th 
                    v-for="tradeNo in tradingData.trade_numbers"
                    :key="'trade-' + tradeNo"
                    class="header-cell trade-header"
                    colspan="3"
                  >
                    Trade {{ tradeNo }}
                  </th>
                  <th class="header-cell summary-header" rowspan="2">Total %</th>
                  <th class="header-cell summary-header" rowspan="2">Avg Price</th>
                </tr>
                <tr class="header-row sub-header-row">
                  <th v-for="n in (tradingData.trade_numbers.length * 3)" :key="'sub-' + n" class="header-cell sub-header">
                    {{ ['Price', '%', 'Date'][((n - 1) % 3)] }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr 
                  v-for="month in tradingData.months"
                  :key="'month-' + month.month"
                  class="data-row"
                >
                  <td class="data-cell month-cell">{{ month.month_name }}</td>
                  <template v-for="tradeNo in tradingData.trade_numbers">
                    <template v-if="getTradeForMonth(month.trades, tradeNo)">
                      <td :key="'ptherm-' + month.month + '-' + tradeNo" class="data-cell">{{ formatNumber(getTradeForMonth(month.trades, tradeNo).p_therm) }}</td>
                      <td :key="'percent-' + month.month + '-' + tradeNo" class="data-cell">{{ formatNumber(getTradeForMonth(month.trades, tradeNo).percent) }}</td>
                      <td :key="'date-' + month.month + '-' + tradeNo" class="data-cell date-cell">{{ formatDate(getTradeForMonth(month.trades, tradeNo).trade_date) }}</td>
                    </template>
                    <template v-else>
                      <td :key="'empty1-' + month.month + '-' + tradeNo" class="data-cell empty-cell">-</td>
                      <td :key="'empty2-' + month.month + '-' + tradeNo" class="data-cell empty-cell">-</td>
                      <td :key="'empty3-' + month.month + '-' + tradeNo" class="data-cell empty-cell">-</td>
                    </template>
                  </template>
                  <td class="data-cell total-cell">{{ month.total_percent }}%</td>
                  <td class="data-cell avg-price-cell">{{ formatNumber(month.avg_price) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- No Trading Data -->
          <div v-else class="empty-state">
            <p>No trading data available for selected year</p>
          </div>
        </div>

        <!-- Projection Data & Calculator Tab -->
        <div v-if="activeTab === 'projection'" class="projection-tab">
          <div class="tab-header">
            <h2>Projection Data & Calculator</h2>
            <div class="year-display">
              <span class="year-badge">Previous Year: {{ computedPreviousYear }}</span>
              <span class="year-badge current">Current Year: {{ computedCurrentYear }}</span>
            </div>
          </div>

          <!-- Projection Loading -->
          <div v-if="projectionLoading" class="loading-state">
            <div class="spinner"></div>
            <p>Loading projection data...</p>
          </div>

          <!-- Projection Error -->
          <div v-else-if="projectionError" class="error-message">
            <svg viewBox="0 0 24 24" fill="none" class="error-icon">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" fill="currentColor"/>
            </svg>
            <p>{{ projectionError }}</p>
            <button @click="loadProjectionData" class="retry-button">Retry</button>
          </div>

          <!-- Three Grids -->
          <div v-else class="projection-grids">
            <!-- Grid 1: Previous Year -->
            <div class="projection-grid">
              <h3>Previous Year ({{ computedPreviousYear }})</h3>
              <table class="mini-table">
                <thead>
                  <tr>
                    <th>Month</th>
                    <th>Trade Price</th>
                    <th>Cost</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in previousYearData" :key="'prev-' + row.month">
                    <td>{{ getMonthName(row.month) }}</td>
                    <td>{{ formatNumber(row.traded_price) }}</td>
                    <td class="cost-cell">£{{ formatNumber(row.cost) }}</td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr class="total-row">
                    <td>Total</td>
                    <td></td>
                    <td class="cost-cell">£{{ previousYearTotal }}</td>
                  </tr>
                </tfoot>
              </table>
            </div>

            <!-- Grid 2: Current Year Projection -->
            <div class="projection-grid">
              <h3>Current Year ({{ computedCurrentYear }})</h3>
              <table class="mini-table">
                <thead>
                  <tr>
                    <th>Month</th>
                    <th>Trade Price</th>
                    <th>Cost</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in currentYearData" :key="'curr-' + row.month">
                    <td>{{ getMonthName(row.month) }}</td>
                    <td>{{ formatNumber(row.traded_price) }}</td>
                    <td class="cost-cell">£{{ formatNumber(row.cost) }}</td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr class="total-row">
                    <td>Total</td>
                    <td></td>
                    <td class="cost-cell">£{{ currentYearTotal }}</td>
                  </tr>
                </tfoot>
              </table>
            </div>

            <!-- Grid 3: Calculator -->
            <div class="projection-grid calculator-grid">
              <h3>Calculator (Simulation)</h3>
              <table class="mini-table calculator-table">
                <thead>
                  <tr>
                    <th>Month</th>
                    <th>Trade Price</th>
                    <th>Cost</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, index) in calculatorData" :key="'calc-' + row.month">
                    <td>{{ getMonthName(row.month) }}</td>
                    <td class="editable-cell">
                      <input 
                        type="number"
                        :value="row.trade_price"
                        @input="updateCalculatorPrice(index, $event.target.value)"
                        @change="recalculateCost"
                        class="price-input"
                        step="0.01"
                        min="0"
                      />
                    </td>
                    <td class="cost-cell">£{{ formatNumber(row.cost) }}</td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr class="total-row">
                    <td>Total</td>
                    <td></td>
                    <td class="cost-cell">£{{ calculatorTotal }}</td>
                  </tr>
                </tfoot>
              </table>
              <p class="calculator-note">
                <em>Edit Trade Price to simulate different scenarios. Costs are calculated automatically using: Cost = (st_charge × days) + (consumption × TradePrice)</em>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Initial Loading -->
    <div v-else-if="!accessDenied" class="loading-state full-page">
      <div class="spinner"></div>
      <p>Loading dashboard...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { projectionApi, extractProjectionData } from '../api/projection'
import { getErrorMessage } from '../api/client'

const router = useRouter()
const authStore = useAuthStore()

// State
const loading = ref(true)
const accessDenied = ref(false)
const accessDeniedMessage = ref('')
const customerData = ref(null)
const activeTab = ref('trading')

// Trading state
const selectedTradingYear = ref(null)
const tradingLoading = ref(false)
const tradingError = ref(null)
const tradingData = ref(null)

// Compute trading years the same way as TradingView (currentYear-2 to currentYear+1)
const tradingYears = computed(() => {
  const currentYear = new Date().getFullYear()
  const years = []
  for (let i = currentYear - 2; i <= currentYear + 1; i++) {
    years.push(i)
  }
  return years
})

// Projection state
const projectionYears = ref([])
const previousYear = ref(null)
const currentYear = ref(null)
const previousYearData = ref([])
const currentYearData = ref([])
const calculatorData = ref([])
const projectionLoading = ref(false)
const projectionError = ref(null)

// Calculate years from projection data - no user selection
const projectionDataYears = computed(() => {
  if (!projectionYears.value.length) {
    const currentYearVal = new Date().getFullYear()
    return [currentYearVal - 1, currentYearVal]
  }
  return projectionYears.value
})

// Current Year = maximum year from projection data
const computedCurrentYear = computed(() => {
  const years = projectionDataYears.value
  if (!years.length) return new Date().getFullYear()
  return Math.max(...years)
})

// Previous Year = Current Year - 1
const computedPreviousYear = computed(() => {
  return computedCurrentYear.value - 1
})

// Computed
const customerName = computed(() => {
  if (authStore.customer) {
    return authStore.customer.name || authStore.user?.username || 'Customer'
  }
  return authStore.user?.username || 'Customer'
})

const formattedMprn = computed(() => {
  return authStore.customer?.mprn || ''
})

const previousYearTotal = computed(() => {
  if (!previousYearData.value.length) return '0.00'
  const sum = previousYearData.value.reduce((acc, row) => acc + (parseFloat(row.cost) || 0), 0)
  return sum.toFixed(2)
})

const currentYearTotal = computed(() => {
  if (!currentYearData.value.length) return '0.00'
  const sum = currentYearData.value.reduce((acc, row) => acc + (parseFloat(row.cost) || 0), 0)
  return sum.toFixed(2)
})

const calculatorTotal = computed(() => {
  if (!calculatorData.value.length) return '0.00'
  const sum = calculatorData.value.reduce((acc, row) => acc + (parseFloat(row.cost) || 0), 0)
  return sum.toFixed(2)
})

// Methods
const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

const getMonthName = (month) => {
  return monthNames[month - 1] || ''
}

const formatNumber = (value) => {
  if (value === null || value === undefined) return '0.00'
  const num = parseFloat(value)
  if (isNaN(num)) return '0.00'
  return num.toFixed(2)
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-GB')
  } catch {
    return dateStr
  }
}

const getTradeForMonth = (trades, tradeNo) => {
  if (!trades) return null
  return trades.find(t => t.trade_no === tradeNo)
}

const checkAccess = async () => {
  // First restore session if needed
  if (!authStore.isAuthenticated) {
    const restored = await authStore.restoreSession()
    if (!restored) {
      accessDenied.value = true
      accessDeniedMessage.value = 'Please login to access this page'
      loading.value = false
      return
    }
  }
  
  // Check if user is a customer
  if (!authStore.isCustomer) {
    accessDenied.value = true
    accessDeniedMessage.value = 'This page is only for customers'
    loading.value = false
    return
  }
  
  // Check if customer data exists
  if (!authStore.customer) {
    accessDenied.value = true
    accessDeniedMessage.value = 'Customer profile not found'
    loading.value = false
    return
  }
  
  // Load dashboard data
  await loadDashboardData()
}

const loadDashboardData = async () => {
  try {
    const response = await projectionApi.getCustomerDashboardData()
    const data = extractProjectionData(response)
    
    customerData.value = data.customer
    projectionYears.value = data.projection_years || []
    
    // Set default trading year from computed years (use current year or most recent)
    const availableTradingYears = tradingYears.value
    selectedTradingYear.value = data.defaults?.trading_year || (availableTradingYears.length ? availableTradingYears[availableTradingYears.length - 1] : null)
    
    // Load initial data
    if (selectedTradingYear.value) {
      loadTradingData()
    }
    // Load projection data (years will be computed from data)
    loadProjectionData()
    
  } catch (err) {
    console.error('Failed to load dashboard data:', err)
    accessDenied.value = true
    accessDeniedMessage.value = getErrorMessage(err)
  } finally {
    loading.value = false
  }
}

const loadTradingData = async () => {
  if (!selectedTradingYear.value) return
  
  tradingLoading.value = true
  tradingError.value = null
  
  try {
    // Use the dedicated customer trading data endpoint (not the trading store which requires business access)
    const response = await projectionApi.getCustomerTradingData(selectedTradingYear.value)
    const data = response.data
    
    if (data.success && data.data.pivot_data) {
      // Transform the trading data to match the template format
      tradingData.value = transformTradingData(data.data.pivot_data)
    } else {
      // No data available for this year
      tradingData.value = null
      if (data.message && !data.message.includes('successfully')) {
        tradingError.value = data.message
      }
    }
  } catch (err) {
    console.error('Failed to load trading data:', err)
    const errorMsg = getErrorMessage(err)
    if (errorMsg.includes('403') || errorMsg.includes('forbidden')) {
      tradingError.value = 'You do not have permission to view this data'
    } else {
      tradingError.value = errorMsg
    }
    tradingData.value = null
  } finally {
    tradingLoading.value = false
  }
}

// Transform trading store data to match template format
const transformTradingData = (data) => {
  if (!data || !data.months) {
    return null
  }
  
  // Find max trades across all months to get trade_numbers
  let maxTrades = 0
  data.months.forEach(month => {
    if (month.trades && month.trades.length > maxTrades) {
      maxTrades = month.trades.length
    }
  })
  
  const tradeNumbers = Array.from({ length: Math.max(maxTrades, 3) }, (_, i) => i + 1)
  
  const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  
  const months = data.months.map(month => ({
    month: month.month,
    month_name: monthNames[month.month - 1] || '',
    trades: month.trades || [],
    total_percent: month.total_percent || 0,
    avg_price: month.average_price_achieved || 0
  }))
  
  return {
    trade_numbers: tradeNumbers,
    months: months
  }
}

// Helper function to generate zero-filled data for missing years
const generateZeroData = () => {
  const months = []
  for (let i = 1; i <= 12; i++) {
    months.push({
      month: i,
      traded_price: 0,
      cost: 0
    })
  }
  return months
}

const loadProjectionData = async () => {
  projectionLoading.value = true
  projectionError.value = null
  
  try {
    // Use computed years
    const prevYear = computedPreviousYear.value
    const currYear = computedCurrentYear.value
    
    // Load both previous and current year data in parallel
    const [prevResponse, currResponse] = await Promise.all([
      prevYear ? projectionApi.getCustomerProjectionData(prevYear) : Promise.resolve({ data: { success: true, data: { rows: [] } } }),
      currYear ? projectionApi.getCustomerProjectionData(currYear) : Promise.resolve({ data: { success: true, data: { rows: [] } } })
    ])
    
    const prevData = prevResponse.data
    const currData = currResponse.data
    
    if (currData.success) {
      currentYearData.value = currData.data.rows || []
      projectionYears.value = currData.data.available_years || projectionYears.value
      
      // Initialize calculator with current year data
      initializeCalculator()
    }
    
    if (prevData.success) {
      const prevRows = prevData.data.rows || []
      // If no data for previous year, use zero-filled data
      if (prevRows.length === 0) {
        previousYearData.value = generateZeroData()
      } else {
        previousYearData.value = prevRows
      }
    } else {
      // If API call failed, use zero-filled data
      previousYearData.value = generateZeroData()
    }
    
    if (!currData.success && currData.message) {
      projectionError.value = currData.message
    }
    
  } catch (err) {
    console.error('Failed to load projection data:', err)
    projectionError.value = getErrorMessage(err)
    // On error, use zero-filled data for both years
    previousYearData.value = generateZeroData()
    currentYearData.value = generateZeroData()
  } finally {
    projectionLoading.value = false
  }
}

const initializeCalculator = () => {
  // Initialize calculator with current year data, pre-filled with trade prices
  calculatorData.value = currentYearData.value.map(row => ({
    month: row.month,
    trade_price: row.traded_price || 0,
    cost: row.cost || 0,
    st_charge: row.st_charge || 0,
    consumption: row.consumption || 0,
    flex_rate: row.flex_rate || 0,
    no_of_days: row.no_of_days || 30
  }))
}

const updateCalculatorPrice = (index, value) => {
  calculatorData.value[index].trade_price = parseFloat(value) || 0
}

const recalculateCost = async () => {
  // Build trade prices object
  const tradePrices = {}
  calculatorData.value.forEach(row => {
    tradePrices[row.month] = row.trade_price
  })
  
  try {
    const response = await projectionApi.calculateCost(computedCurrentYear.value, tradePrices)
    const data = response.data
    
    if (data.success) {
      // Update calculator costs
      data.data.rows.forEach(calcRow => {
        const index = calculatorData.value.findIndex(c => c.month === calcRow.month)
        if (index !== -1) {
          calculatorData.value[index].cost = calcRow.cost
        }
      })
    }
  } catch (err) {
    console.error('Failed to recalculate cost:', err)
  }
}

// Watch for tab changes to reload data when switching to projection tab
watch(activeTab, (newTab) => {
  if (newTab === 'projection' && !projectionLoading.value && currentYearData.value.length === 0) {
    loadProjectionData()
  }
})

// Lifecycle
onMounted(() => {
  checkAccess()
})
</script>

<style scoped>
.customer-dashboard {
  padding: 24px;
  min-height: 100vh;
}

.access-denied {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  text-align: center;
  color: #991b1b;
}

.denied-icon {
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
  color: #dc2626;
}

.access-denied h2 {
  margin: 0 0 8px 0;
  font-size: 1.5rem;
}

.access-denied p {
  margin: 0;
  color: #7f1d1d;
}

.dashboard-header {
  margin-bottom: 24px;
  padding: 20px;
  background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
  border-radius: 12px;
  color: white;
}

.header-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.tab-icon-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-icon-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.5);
}

.tab-icon-btn.active {
  background: white;
  color: #1e40af;
  border-color: white;
}

.tab-icon {
  width: 20px;
  height: 20px;
}

.tab-icon-label {
  font-size: 0.875rem;
  font-weight: 500;
}

.customer-name {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.mprn-badge {
  background: rgba(255, 255, 255, 0.2);
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
}

.tab-content {
  background: white;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

.tab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
}

.tab-header h2 {
  margin: 0;
  font-size: 1.25rem;
  color: #1e293b;
}

.year-selector,
.year-display {
  display: flex;
  align-items: center;
  gap: 16px;
}

.year-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.year-group label {
  font-size: 0.875rem;
  color: #64748b;
}

.year-badge {
  padding: 8px 16px;
  background-color: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #64748b;
}

.year-badge.current {
  background-color: #3b82f6;
  border-color: #3b82f6;
  color: white;
}

select {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.875rem;
  background: white;
  cursor: pointer;
}

select:focus {
  outline: none;
  border-color: #3b82f6;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  color: #64748b;
}

.loading-state.full-page {
  min-height: 400px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e2e8f0;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.error-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48px;
  color: #991b1b;
}

.error-icon {
  width: 48px;
  height: 48px;
  margin-bottom: 16px;
  color: #dc2626;
}

.retry-button {
  margin-top: 16px;
  padding: 8px 16px;
  background: #dc2626;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  color: #64748b;
}

/* Trading Grid Styles */
.trading-grid-container {
  overflow-x: auto;
  padding: 24px;
}

.pivot-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.header-row {
  background: #f8fafc;
}

.header-cell {
  padding: 12px 8px;
  text-align: center;
  font-weight: 600;
  color: #475569;
  border-bottom: 2px solid #e2e8f0;
  white-space: nowrap;
}

.trade-header {
  background: #e0f2fe;
  color: #0369a1;
}

.sub-header-row .header-cell {
  font-size: 0.75rem;
  font-weight: 500;
  padding: 8px;
}

.data-row {
  border-bottom: 1px solid #e2e8f0;
}

.data-row:hover {
  background: #f8fafc;
}

.data-cell {
  padding: 10px 8px;
  text-align: center;
  color: #334155;
}

.month-cell {
  font-weight: 500;
  text-align: left;
  color: #1e293b;
}

.empty-cell {
  color: #cbd5e1;
}

.total-cell {
  font-weight: 600;
  color: #0369a1;
  background: #e0f2fe;
}

.avg-price-cell {
  font-weight: 600;
  color: #059669;
  background: #ecfdf5;
}

.date-cell {
  font-size: 0.75rem;
  color: #64748b;
}

/* Projection Grids */
.projection-grids {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  padding: 24px;
}

@media (max-width: 1200px) {
  .projection-grids {
    grid-template-columns: 1fr;
  }
}

.projection-grid {
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e2e8f0;
}

.projection-grid h3 {
  margin: 0 0 16px 0;
  font-size: 1rem;
  color: #1e293b;
  text-align: center;
}

.mini-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8rem;
  table-layout: fixed;
}

.mini-table th,
.mini-table td {
  padding: 8px;
  text-align: center;
  border-bottom: 1px solid #e2e8f0;
  width: 33.33%;
}

.mini-table th {
  background: #e2e8f0;
  font-weight: 600;
  color: #475569;
}

.mini-table td {
  color: #334155;
}

.cost-cell {
  font-weight: 600;
  color: #059669;
}

.total-row {
  background: #e0f2fe;
}

.total-row td {
  font-weight: 600;
  color: #0369a1;
}

.calculator-grid {
  background: #fff7ed;
  border-color: #fed7aa;
}

.calculator-table td.editable-cell {
  padding: 4px;
}

.price-input {
  width: 100%;
  padding: 6px 8px;
  border: 1px solid #fed7aa;
  border-radius: 4px;
  font-size: 0.8rem;
  text-align: right;
  /* Hide number input spinners */
  -moz-appearance: textfield;
}

.price-input::-webkit-outer-spin-button,
.price-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.price-input:focus {
  outline: none;
  border-color: #f97316;
}

.calculator-note {
  margin: 16px 0 0 0;
  font-size: 0.75rem;
  color: #9a3412;
  text-align: center;
}
</style>
