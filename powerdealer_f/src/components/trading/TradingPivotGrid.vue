<template>
  <div class="trading-pivot-grid">
    <!-- Loading State -->
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <p>Loading pivot data...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-message">
      <svg viewBox="0 0 24 24" fill="none" class="error-icon">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" fill="currentColor"/>
      </svg>
      <p>{{ error }}</p>
      <button @click="$emit('retry')" class="retry-button">Retry</button>
    </div>

    <!-- Empty State -->
    <div v-else-if="!pivotData" class="empty-state">
      <svg viewBox="0 0 24 24" fill="none" class="empty-icon">
        <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z" fill="currentColor"/>
      </svg>
      <p>Select a customer and year to view trading data</p>
    </div>

    <!-- Data Grid -->
    <div v-else class="grid-container">
      <!-- Using table for proper colspan/rowspan support -->
      <table class="pivot-table">
        <!-- Header Row 1 - Trade Numbers with colspan -->
        <thead>
          <tr class="header-row header-row-1">
            <th class="header-cell month-header" rowspan="2">Month</th>
            <th 
              v-for="tradeNo in tradeNumbers"
              :key="'trade-' + tradeNo"
              class="header-cell trade-header"
              :colspan="3"
              :class="{ 'hoverable': getTradesForTradeNo(tradeNo).length > 0 }"
              @mouseenter="hoveredTradeNo = tradeNo"
              @mouseleave="hoveredTradeNo = null"
              
            >
              <div class="trade-header-inner">
                <span>Trade {{ tradeNo }}</span>
              </div>
            </th>
            <th class="header-cell summary-header" rowspan="2">Total %</th>
            <th class="header-cell summary-header" rowspan="2">Avg Price</th>
          </tr>
          
          <!-- Header Row 2 - Sub-headers - interleaved for each trade -->
          <tr class="header-row header-row-2">
            <th 
              v-for="n in totalTradeCells" 
              :key="'sub-' + n" 
              class="header-cell sub-header"
              :class="{ 'date-header': (n - 1) % 3 === 2 }"
            >
              {{ getSubHeaderLabel(n) }}
            </th>
          </tr>
        </thead>

        <!-- Month Rows -->
        <tbody>
          <tr 
            v-for="month in months" 
            :key="'month-' + month.num"
            class="data-row"
            :class="{ 'active-row': editingMonth === month.num }"
          >
            <!-- Month Name -->
            <td class="data-cell month-cell">
              <div class="month-cell-content">
                <span>{{ month.name }}</span>
                <button 
                  class="add-trade-btn"
                  @click="openAddTrade(month.num)"
                  title="Add new trade"
                >
                  <svg viewBox="0 0 24 24" fill="none" class="plus-icon">
                    <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" fill="currentColor"/>
                  </svg>
                </button>
              </div>
            </td>

            <!-- Trade Cells -->
            <template v-for="tradeNo in tradeNumbers">
              <td 
                v-if="getTrade(month.num, tradeNo)" 
                :key="'ptherm-' + month.num + '-' + tradeNo" 
                class="data-cell trade-cell"
                @contextmenu="showContextMenu($event, getTrade(month.num, tradeNo).id, month.num)"
              >
                <input 
                  type="number" 
                  :value="formatPTherm(getTrade(month.num, tradeNo).p_therm)"
                  @input="updateTradeField(month.num, tradeNo, 'p_therm', $event.target.value)"
                  @change="saveTrade(getTrade(month.num, tradeNo).id, month.num, tradeNo)"
                  class="input-field"
                  step="0.0001"
                  min="0"
                  placeholder="0.0000"
                />
              </td>
              <td v-else :key="'ptherm-empty-' + month.num + '-' + tradeNo" class="data-cell empty-cell"></td>
              
              <td v-if="getTrade(month.num, tradeNo)" :key="'percent-' + month.num + '-' + tradeNo" class="data-cell trade-cell" :class="{ 'error-cell': getTrade(month.num, tradeNo).percent > 100 }">
                <input 
                  type="number" 
                  :value="formatPercentInput(getTrade(month.num, tradeNo).percent)"
                  @input="updateTradeField(month.num, tradeNo, 'percent', $event.target.value)"
                  @change="saveTrade(getTrade(month.num, tradeNo).id, month.num, tradeNo)"
                  class="input-field"
                  step="0.01"
                  min="0"
                  max="100"
                  placeholder="0.00"
                />
              </td>
              <td v-else :key="'percent-empty-' + month.num + '-' + tradeNo" class="data-cell empty-cell"></td>
              
              <td v-if="getTrade(month.num, tradeNo)" :key="'date-' + month.num + '-' + tradeNo" class="data-cell trade-cell date-cell">
                <input 
                  type="date" 
                  :value="getTrade(month.num, tradeNo).trade_date"
                  @input="updateTradeField(month.num, tradeNo, 'trade_date', $event.target.value)"
                  @change="saveTrade(getTrade(month.num, tradeNo).id, month.num, tradeNo)"
                  class="input-field date-input"
                />
              </td>
              <td v-else :key="'date-empty-' + month.num + '-' + tradeNo" class="data-cell empty-cell"></td>
            </template>

            <!-- Summary Cells -->
            <td 
              class="data-cell summary-cell"
              :class="getTotalBookedClass(month.num)"
            >
              <span class="summary-value">{{ formatPercent(getMonthTotal(month.num)) }}</span>
            </td>
            <td class="data-cell summary-cell">
              <span class="summary-value">{{ formatPrice(getMonthAveragePrice(month.num)) }}</span>
            </td>
          </tr>
        </tbody>
      </table>
      
      <div class="grid-info-footer">
        <svg viewBox="0 0 24 24" fill="none" class="info-icon">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-4h-2V7h2v6z" fill="currentColor"/>
        </svg>
        <span><strong>Tip:</strong> To delete a trade, <strong>right-click</strong> on any value in the <strong>P/Therm</strong> column.</span>
      </div>
      
    </div>

    <!-- Context Menu -->
    <div 
      v-if="contextMenu.visible" 
      class="context-menu"
      :style="{ top: contextMenu.y + 'px', left: contextMenu.x + 'px' }"
      @click.stop
    >
      <div class="context-menu-item" @click="handleDeleteFromContextMenu">
        <svg viewBox="0 0 24 24" fill="none" class="context-menu-icon">
          <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z" fill="currentColor"/>
        </svg>
        Delete Trade
      </div>
    </div>

    <!-- Add Trade Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="closeAddModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Add New Trade</h3>
          <button class="close-btn" @click="closeAddModal">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" fill="currentColor"/>
            </svg>
          </button>
        </div>
        <form @submit.prevent="submitNewTrade" class="trade-form">
          <div class="form-group">
            <label>Month</label>
            <select v-model="newTrade.month" required>
              <option v-for="month in months" :key="'opt-' + month.num" :value="month.num">
                {{ month.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Price per Therm</label>
            <input 
              v-model="newTrade.p_therm" 
              type="number" 
              step="0.0001" 
              min="0" 
              required
              placeholder="0.0000"
              class="no-spinner"
            />
          </div>
          <div class="form-group">
            <label>Percentage</label>
            <input 
              v-model="newTrade.percent" 
              type="number" 
              step="0.01" 
              min="0" 
              max="100" 
              required
              placeholder="0.00"
              class="no-spinner"
            />
          </div>
          <div class="form-group">
            <label>Trade Date</label>
            <input 
              v-model="newTrade.trade_date" 
              type="date" 
              required
            />
          </div>
          <div v-if="saveError" class="form-error">
            {{ saveError }}
          </div>
          <div class="form-actions">
            <button type="button" class="btn-secondary" @click="closeAddModal">Cancel</button>
            <button type="submit" class="btn-primary" :disabled="saveLoading">
              {{ saveLoading ? 'Saving...' : 'Save Trade' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useTradingStore } from '../../stores/trading'

const props = defineProps({
  mprn: {
    type: String,
    required: true
  },
  year: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['retry', 'trade-created', 'trade-updated', 'trade-deleted'])

// Store
const store = useTradingStore()

// Local state
const editingMonth = ref(null)
const hoveredTradeNo = ref(null)
const showAddModal = ref(false)
const editingTrade = ref({})
const newTrade = ref({
  month: 1,
  p_therm: '',
  percent: '',
  trade_date: ''
})

// Context menu state
const contextMenu = ref({
  visible: false,
  x: 0,
  y: 0,
  tradeId: null,
  month: null
})

// Months data
const months = [
  { num: 1, name: 'January' },
  { num: 2, name: 'February' },
  { num: 3, name: 'March' },
  { num: 4, name: 'April' },
  { num: 5, name: 'May' },
  { num: 6, name: 'June' },
  { num: 7, name: 'July' },
  { num: 8, name: 'August' },
  { num: 9, name: 'September' },
  { num: 10, name: 'October' },
  { num: 11, name: 'November' },
  { num: 12, name: 'December' }
]

// Computed
const tradeNumbers = computed(() => {
  const max = maxTrades.value
  return Array.from({ length: max }, (_, i) => i + 1)
})

const loading = computed(() => store.loading)
const error = computed(() => store.error)
const saveLoading = computed(() => store.saveLoading)
const saveError = computed(() => store.saveError)
const pivotData = computed(() => store.pivotData)

const maxTrades = computed(() => {
  if (!pivotData.value?.months) return 3
  let max = 3
  pivotData.value.months.forEach(month => {
    if (month.trades && month.trades.length > max) {
      max = month.trades.length
    }
  })
  return Math.max(max, 3)
})

// Total number of cells in the trade columns (tradeNumbers * 3)
const totalTradeCells = computed(() => {
  return tradeNumbers.value.length * 3
})

// Get sub-header label for header row 2
const getSubHeaderLabel = (n) => {
  const idx = n - 1 // 0-based index
  const positionInTrade = idx % 3 // 0, 1, or 2
  if (positionInTrade === 0) return 'P/Therm'
  if (positionInTrade === 1) return '%'
  return 'Date'
}

// Methods
const getTradesForTradeNo = (tradeNo) => {
  if (!pivotData.value?.months) return []
  const trades = []
  pivotData.value.months.forEach(month => {
    const trade = month.trades?.find(t => t.trade_no === tradeNo)
    if (trade) trades.push(trade)
  })
  return trades
}

const getTrade = (month, tradeNo) => {
  if (!pivotData.value?.months) return null
  const monthData = pivotData.value.months.find(m => m.month === month)
  if (!monthData?.trades) return null
  
  // Sort trades by trade_date ascending
  const sortedTrades = [...monthData.trades].sort((a, b) => 
    new Date(a.trade_date) - new Date(b.trade_date)
  )
  
  return sortedTrades[tradeNo - 1] || null
}

const getMonthTotal = (month) => {
  if (!pivotData.value?.months) return 0
  const monthData = pivotData.value.months.find(m => m.month === month)
  return monthData?.total_percent || 0
}

const getMonthAveragePrice = (month) => {
  if (!pivotData.value?.months) return 0
  const monthData = pivotData.value.months.find(m => m.month === month)
  return monthData?.average_price_achieved || 0
}

const getTotalBookedClass = (month) => {
  const total = getMonthTotal(month)
  if (total === 100) return 'status-green'
  if (total > 100) return 'status-red'
  if (total > 0) return 'status-yellow'
  return 'status-none'
}

const formatPercent = (value) => {
  return value !== null && value !== undefined ? `${parseFloat(value).toFixed(2)}%` : '0%'
}

const formatPrice = (value) => {
  return value !== null && value !== undefined ? `£${parseFloat(value).toFixed(2)}` : '£0.00'
}

// Format number to 2 decimal places for display in inputs
const formatNumber = (value, decimals = 2) => {
  if (value === null || value === undefined || value === '') return ''
  const num = parseFloat(value)
  if (isNaN(num)) return ''
  return num.toFixed(decimals)
}

// Format P/Therm to 2 decimal places
const formatPTherm = (value) => {
  return formatNumber(value, 2)
}

// Format Percent to 2 decimal places
const formatPercentInput = (value) => {
  return formatNumber(value, 2)
}

const updateTradeField = (month, tradeNo, field, value) => {
  const key = `${month}-${tradeNo}`
  if (!editingTrade.value[key]) {
    editingTrade.value[key] = { ...getTrade(month, tradeNo) }
  }
  editingTrade.value[key][field] = value
  
  // Recalculate totals locally
  recalculateLocally(month)
}

const recalculateLocally = (month) => {
  // This is handled reactively by the computed properties
}

const saveTrade = async (tradeId, month, tradeNo) => {
  const key = `${month}-${tradeNo}`
  const tradeData = editingTrade.value[key]
  
  if (!tradeData || !tradeId) return
  
  try {
    await store.patchTrade(tradeId, {
      p_therm: parseFloat(tradeData.p_therm),
      percent: parseFloat(tradeData.percent),
      trade_date: tradeData.trade_date
    })
    delete editingTrade.value[key]
    emit('trade-updated', tradeId)
  } catch (err) {
    console.error('Failed to save trade:', err)
  }
}

const openAddTrade = (month) => {
  newTrade.value = {
    month,
    p_therm: '',
    percent: '',
    trade_date: new Date().toISOString().split('T')[0]
  }
  showAddModal.value = true
}

const closeAddModal = () => {
  showAddModal.value = false
}

const submitNewTrade = async () => {
  try {
    await store.createTrade({
      mprn: props.mprn,
      month: newTrade.value.month,
      year: props.year,
      p_therm: parseFloat(newTrade.value.p_therm),
      percent: parseFloat(newTrade.value.percent),
      trade_date: newTrade.value.trade_date
    })
    closeAddModal()
    emit('trade-created')
  } catch (err) {
    console.error('Failed to create trade:', err)
  }
}

const handleDeleteTrade = async (tradeId) => {
  // Delete the trade using its unique id
  if (!tradeId) return

  try {
    await store.deleteTrade(tradeId)
    emit('trade-deleted', tradeId)
  } catch (err) {
    console.error('Failed to delete trade:', err)
  }
}

// Context menu handlers
const showContextMenu = (event, tradeId, month) => {
  event.preventDefault()
  contextMenu.value = {
    visible: true,
    x: event.clientX,
    y: event.clientY,
    tradeId: tradeId,
    month: month
  }
}

const hideContextMenu = () => {
  contextMenu.value.visible = false
}

const handleDeleteFromContextMenu = async () => {
  if (contextMenu.value.tradeId) {
    await handleDeleteTrade(contextMenu.value.tradeId)
    hideContextMenu()
  }
}

// Close context menu when clicking outside
const handleGlobalClick = () => {
  if (contextMenu.value.visible) {
    hideContextMenu()
  }
}

// Watch for mprn/year changes
watch(() => [props.mprn, props.year], ([newMprn, newYear]) => {
  console.log('[TradingPivotGrid] Watch triggered:', { newMprn, newYear })
  if (newMprn && newYear) {
    console.log('[TradingPivotGrid] Calling store.fetchPivotDataByMprn')
    store.fetchPivotDataByMprn(newMprn, newYear)
  }
}, { immediate: true })

// Register global click handler to close context menu
onMounted(() => {
  document.addEventListener('click', handleGlobalClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleGlobalClick)
})
</script>

<style scoped>
.trading-pivot-grid {
  width: 100%;
  min-height: 400px;
  position: relative;
}

.loading-overlay,
.error-message,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  color: var(--color-text-secondary, #6b7280);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-icon,
.empty-icon {
  width: 48px;
  height: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.retry-button {
  margin-top: 16px;
  padding: 8px 16px;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.retry-button:hover {
  background-color: #2563eb;
}

.grid-container {
  overflow-x: auto;
  overflow-y: auto;
  max-width: 100%;
  border-radius: 8px;
  border: 1px solid var(--color-border, #e5e7eb);
}

.grid-container::-webkit-scrollbar {
  height: 8px;
  width: 8px;
}

.grid-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.grid-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.grid-container::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

.grid-wrapper {
  display: flex;
  flex-direction: column;
  min-width: 800px;
}

/* Table styles for Excel-like appearance */
.pivot-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: auto;
  min-width: 1200px;
  max-width: none;
}

.pivot-table th,
.pivot-table td {
  border: 1px solid #d1d5db;
  padding: 0;
  vertical-align: middle;
  box-sizing: border-box;
}

.pivot-table thead th {
  background-color: #f3f4f6;
  font-weight: 600;
  position: sticky;
  top: 0;
  z-index: 10;
}

.pivot-table thead tr:first-child th {
  border-bottom: none;
}

.pivot-table thead tr:nth-child(2) th {
  border-top: 1px solid #d1d5db;
  background-color: #e5e7eb;
}

.pivot-table tbody tr:hover {
  background-color: #f9fafb;
}

.header-row-1 {
  font-weight: 600;
}

.header-row-2 {
  font-weight: 500;
  font-size: 0.875rem;
}

.header-cell {
  padding: 12px 8px;
  text-align: center;
  font-size: 0.875rem;
}

.month-header {
  width: 80px;
  min-width: 80px;
  max-width: 80px;
  text-align: left;
  padding-left: 16px;
  background-color: #e5e7eb;
}

.trade-header {
  width: 280px;
  min-width: 280px;
  max-width: 280px;
  position: relative;
}

.trade-header-inner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.trade-header.hoverable {
  cursor: pointer;
}

.trade-header.hoverable:hover {
  background-color: #d1d5db;
}

.trade-subheader-group {
  display: flex;
}

.delete-trade-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  padding: 0;
  background-color: #ef4444;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  color: white;
}

.delete-trade-btn:hover {
  background-color: #dc2626;
}

.trash-icon {
  width: 14px;
  height: 14px;
}

.sub-header {
  width: 80px;
  min-width: 80px;
  max-width: 80px;
  font-size: 0.75rem;
  font-weight: 500;
}

.date-header,
.date-cell {
  width: 120px !important;
  min-width: 120px !important;
  max-width: 120px !important;
}

.summary-header {
  width: 80px;
  min-width: 80px;
  max-width: 80px;
  font-weight: 600;
  background-color: #dbeafe;
}

/* Data rows */
.data-row:hover {
  background-color: #f9fafb;
}

.data-row.active-row {
  background-color: #eff6ff;
}

.data-cell {
  padding: 8px;
  text-align: center;
}

.month-cell {
  width: 80px;
  min-width: 80px;
  max-width: 80px;
  text-align: left;
  padding-left: 16px;
  font-weight: 500;
}

.month-cell-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.add-trade-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  padding: 0;
  background-color: #10b981;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  color: white;
  opacity: 0;
  transition: opacity 0.2s;
}

.data-row:hover .add-trade-btn {
  opacity: 1;
}

.add-trade-btn:hover {
  background-color: #059669;
}

.plus-icon {
  width: 16px;
  height: 16px;
}

.trade-cell {
  width: 80px;
  min-width: 80px;
  max-width: 80px;
  padding: 4px;
  text-align: center;
}

/* .date-cell {
  width: 140px !important;
  min-width: 140px !important;
  max-width: 140px !important;
} */

.trade-cells-group {
  display: contents;
}

.trade-cell.error-cell {
  background-color: #fef2f2;
}

.input-field {
  width: 100%;
  padding: 6px 8px;
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: 4px;
  font-size: 0.875rem;
  text-align: center;
  /* Remove spinner buttons for number inputs */
  -moz-appearance: textfield;
}

.input-field::-webkit-outer-spin-button,
.input-field::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.input-field:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}


.date-input {
  width: 100% !important; 
  box-sizing: border-box;
  font-size: 0.85rem;
  padding: 4px 6px;
}

.empty-cell {
  background-color: #f9fafb;
}

.summary-cell {
  width: 80px;
  min-width: 80px;
  max-width: 80px;
  text-align: center;
}

.summary-value {
  font-weight: 600;
  font-size: 0.875rem;
}

.status-green {
  background-color: #d1fae5;
  color: #065f46;
}

.status-yellow {
  background-color: #fef3c7;
  color: #92400e;
}

.status-red {
  background-color: #fee2e2;
  color: #991b1b;
}

.status-none {
  background-color: #f9fafb;
  color: #6b7280;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 12px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
}

.modal-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  background: none;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  color: #6b7280;
}

.close-btn:hover {
  background-color: #f3f4f6;
}

.close-btn svg {
  width: 20px;
  height: 20px;
}

.trade-form {
  padding: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: 6px;
  font-size: 0.875rem;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

/* Remove spinner buttons for number inputs in modal */
.form-group input[type="number"] {
  -moz-appearance: textfield;
}

.form-group input[type="number"]::-webkit-outer-spin-button,
.form-group input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.form-error {
  padding: 10px;
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  color: #991b1b;
  font-size: 0.875rem;
  margin-bottom: 16px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-secondary,
.btn-primary {
  padding: 10px 16px;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary {
  background-color: white;
  border: 1px solid var(--color-border, #d1d5db);
  color: #374151;
}

.btn-secondary:hover {
  background-color: #f9fafb;
}

.btn-primary {
  background-color: #3b82f6;
  border: none;
  color: white;
}

.btn-primary:hover {
  background-color: #2563eb;
}

.btn-primary:disabled {
  background-color: #93c5fd;
  cursor: not-allowed;
}

/* Context Menu Styles */
.context-menu {
  position: fixed;
  z-index: 1000;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border: 1px solid #e5e7eb;
  min-width: 160px;
  overflow: hidden;
}

.context-menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  cursor: pointer;
  color: #dc2626;
  font-size: 0.875rem;
  font-weight: 500;
  transition: background-color 0.15s;
}

.context-menu-item:hover {
  background-color: #fef2f2;
}

.context-menu-icon {
  width: 16px;
  height: 16px;
}

.grid-info-footer {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 10px 16px;
  background-color: #f0f7ff; /* Light blue background */
  border-left: 4px solid #3b82f6; /* Blue accent border */
  border-radius: 4px;
  color: #1e40af; /* Dark blue text */
  font-size: 0.875rem;
}

.info-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  color: #3b82f6;
}

.grid-info-footer strong {
  font-weight: 600;
}

</style>
