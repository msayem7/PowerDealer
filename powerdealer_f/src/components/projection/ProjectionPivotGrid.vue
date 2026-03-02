<template>
  <div class="projection-pivot-grid">
    <!-- Loading State -->
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <p>Loading projection data...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-message">
      <svg viewBox="0 0 24 24" fill="none" class="error-icon">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" fill="currentColor"/>
      </svg>
      <p>{{ error }}</p>
      <button @click="$emit('retry')" class="retry-button">Retry</button>
    </div>

    <!-- Data Grid -->
    <div v-else class="grid-container">
      <table class="pivot-table">
        <thead>
          <tr class="header-row">
            <th class="header-cell">Month</th>
            <th class="header-cell">No of Days</th>
            <th class="header-cell editable-header">St Charge<br/>(p/day)</th>
            <th class="header-cell editable-header">Consumption<br/>(kWh)</th>
            <th class="header-cell editable-header">Flex Unit Rate<br/>(p/kWh)</th>
            <th class="header-cell">Traded Price<br/>(p/therm)</th>
            <th class="header-cell">Cost<br/>(£)</th>
          </tr>
        </thead>

        <tbody>
          <tr 
            v-for="(row, index) in projectionRows" 
            :key="'month-' + row.month"
            class="data-row"
          >
            <!-- Month Name (readonly) -->
            <td class="data-cell month-cell">
              {{ getMonthName(row.month) }}
            </td>

            <!-- No of Days (readonly) -->
            <td class="data-cell days-cell">
              {{ row.no_of_days }}
            </td>

            <!-- St Charge (editable) -->
            <td class="data-cell editable-cell st-charge-cell">
              <input 
                type="number" 
                :value="getLocalValue(index, 'st_charge')"
                @input="updateLocalField(index, 'st_charge', $event.target.value)"
                @change="commitField(index, 'st_charge', $event.target.value)"
                class="input-field input-field-narrow"
                step="0.01"
                min="0"
                placeholder="0.00"
              />
            </td>

            <!-- Consumption (editable) -->
            <td class="data-cell editable-cell">
              <input 
                type="number" 
                :value="getLocalValue(index, 'consumption')"
                @input="updateLocalField(index, 'consumption', $event.target.value)"
                @change="commitField(index, 'consumption', $event.target.value)"
                class="input-field"
                step="0.01"
                min="0"
                placeholder="0.00"
              />
            </td>

            <!-- Flex Unit Rate (editable) -->
            <td class="data-cell editable-cell flex-rate-cell">
              <input 
                type="number" 
                :value="getLocalValue(index, 'flex_rate')"
                @input="updateLocalField(index, 'flex_rate', $event.target.value)"
                @change="commitField(index, 'flex_rate', $event.target.value)"
                class="input-field input-field-medium"
                step="0.00000001"
                min="0"
                placeholder="0.00000000"
              />
            </td>

            <!-- Traded Price (readonly) -->
            <td class="data-cell readonly-cell">
              {{ formatTradedPrice(row.traded_price) }}
            </td>

            <!-- Cost (readonly, auto-calculated) -->
            <td class="data-cell cost-cell cost-cell-wide">
              {{ formatCost(row.cost) }}
            </td>
          </tr>

          <!-- Grand Total Row -->
          <tr class="total-row">
            <td class="total-cell total-label">Total</td>
            <td class="total-cell"></td>
            <td class="total-cell"></td>
            <td class="total-cell total-consumption">{{ totalConsumption }}</td>
            <td class="total-cell"></td>
            <td class="total-cell"></td>
            <td class="total-cell total-cost">{{ totalCost }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useProjectionStore } from '../../stores/projection'

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

const emit = defineEmits(['retry'])

// Store
const projectionStore = useProjectionStore()

// Local editing state - stores temporary edits before committing to store
const editingRow = ref({})

// Computed
const loading = computed(() => projectionStore.loading)
const error = computed(() => projectionStore.error)
const projectionRows = computed(() => projectionStore.projectionRows)

// Grand Total computations
const totalCost = computed(() => {
  if (!projectionRows.value || projectionRows.value.length === 0) return '0.00'
  const sum = projectionRows.value.reduce((acc, row) => acc + (parseFloat(row.cost) || 0), 0)
  return sum.toFixed(2)
})

const totalConsumption = computed(() => {
  if (!projectionRows.value || projectionRows.value.length === 0) return '0.00'
  const sum = projectionRows.value.reduce((acc, row) => acc + (parseFloat(row.consumption) || 0), 0)
  return sum.toFixed(2)
})

// Month names
const monthNames = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
]

const getMonthName = (month) => {
  return monthNames[month - 1] || ''
}

// Formatting functions
const formatStCharge = (value) => {
  if (value === null || value === undefined || value === '') return ''
  return parseFloat(value).toFixed(2)
}

const formatConsumption = (value) => {
  if (value === null || value === undefined || value === '') return ''
  return parseFloat(value).toFixed(2)
}

const formatFlexRate = (value) => {
  if (value === null || value === undefined || value === '') return ''
  return parseFloat(value).toFixed(8)
}

const formatTradedPrice = (value) => {
  if (value === null || value === undefined) return '0.00000000'
  return parseFloat(value).toFixed(8)
}

const formatCost = (value) => {
  if (value === null || value === undefined) return '0.00'
  return parseFloat(value).toFixed(2)
}

// Get local value for input - returns local edit if exists, otherwise the store value
const getLocalValue = (index, field) => {
  const key = `${index}-${field}`
  if (editingRow.value[key] !== undefined) {
    return editingRow.value[key]
  }
  // Return formatted store value if no local edit
  const row = projectionStore.projectionRows[index]
  if (!row) return ''
  const value = row[field]
  if (field === 'st_charge') return formatStCharge(value)
  if (field === 'consumption') return formatConsumption(value)
  if (field === 'flex_rate') return formatFlexRate(value)
  return value
}

// Update local editing state (called on @input)
const updateLocalField = (index, field, value) => {
  const key = `${index}-${field}`
  editingRow.value[key] = value
}

// Commit field to store (called on @change - fires on Enter/blur)
const commitField = (index, field, value) => {
  const numValue = parseFloat(value) || 0
  
  // Check for negative values
  if (numValue < 0) {
    console.warn(`[ProjectionPivotGrid] Negative value not allowed for ${field}`)
    // Reset local edit to store value
    const editKey = `${index}-${field}`
    delete editingRow.value[editKey]
    return
  }
  
  // Commit to store
  projectionStore.updateRowField(index, field, numValue)
  
  // Clear local edit after commit
  const editKey = `${index}-${field}`
  delete editingRow.value[editKey]
}
</script>

<style scoped>
.projection-pivot-grid {
  width: 100%;
}

.loading-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  color: var(--color-text-secondary);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
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
  justify-content: center;
  padding: 48px;
  color: #991b1b;
  text-align: center;
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
  background-color: #dc2626;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.grid-container {
  overflow-x: auto;
}

.pivot-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.header-row {
  background-color: var(--color-background);
}

.header-cell {
  padding: 12px 16px;
  text-align: center;
  font-weight: 600;
  color: var(--color-text-secondary);
  border-bottom: 2px solid var(--color-border);
  white-space: nowrap;
}

.header-cell:first-child {
  text-align: left;
}

.editable-header {
  background-color: #f0f9ff;
  color: var(--color-primary);
}

.data-row {
  border-bottom: 1px solid var(--color-border);
  transition: background-color 0.15s;
}

.data-row:hover {
  background-color: var(--color-background);
}

.data-cell {
  padding: 8px 12px;
  text-align: center;
  vertical-align: middle;
}

.month-cell {
  text-align: left;
  font-weight: 500;
  color: var(--color-text-primary);
}

.days-cell {
  color: var(--color-text-secondary);
}

.editable-cell {
  padding: 4px 8px;
}

.readonly-cell {
  color: var(--color-text-secondary);
}

.cost-cell {
  font-weight: 600;
  color: var(--color-primary);
  background-color: #f0f9ff;
}

.cost-cell-wide {
  min-width: 200px;
  width: 200px;
}

.st-charge-cell .input-field,
.input-field-narrow {
  min-width: 80px;
}

.flex-rate-cell .input-field,
.input-field-medium {
  min-width: 110px;
}

.input-field {
  width: 100%;
  min-width: 100px;
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 0.875rem;
  text-align: right;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.input-field:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.input-field:hover:not(:focus) {
  border-color: var(--color-primary);
}

/* Remove spinner buttons from number inputs */
.input-field::-webkit-outer-spin-button,
.input-field::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.input-field[type=number] {
  -moz-appearance: textfield;
}

/* Total Row Styles */
.total-row {
  background-color: #e0e7ff;
  border-top: 2px solid var(--color-primary);
}

.total-row:hover {
  background-color: #e0e7ff;
}

.total-cell {
  padding: 12px 16px;
  text-align: center;
  font-weight: 600;
  color: var(--color-text-primary);
  border-top: 2px solid var(--color-primary);
}

.total-label {
  text-align: left;
  color: var(--color-primary);
}

.total-cost {
  color: var(--color-primary);
  background-color: #c7d2fe;
}

.total-consumption {
  color: var(--color-text-secondary);
}
</style>
