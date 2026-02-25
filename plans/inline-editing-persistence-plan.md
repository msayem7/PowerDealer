# Inline Editing Persistence - Technical Analysis and Solution Design

## Executive Summary

After analyzing the codebase, I identified **two bugs** preventing inline edits from being persisted to the database:

1. **Frontend Bug**: The component uses `store.updateTrade()` which makes a PUT request, but only sends partial data (p_therm, percent, trade_date). PUT requires all required fields.

2. **Backend Bug**: The `TradeSerializer.validate()` method doesn't handle partial updates correctly - it raises an error when `customer` is not in the request data, even for PATCH requests.

---

## Current Implementation Analysis

### Frontend - Inline Editing Flow

#### 1. Template - Input Fields ([`TradingPivotGrid.vue:100-136`](powerdealer_f/src/components/trading/TradingPivotGrid.vue:100))

```vue
<!-- P/Therm input -->
<input 
  type="number" 
  :value="getTrade(month.num, tradeNo).p_therm"
  @input="updateTradeField(month.num, tradeNo, 'p_therm', $event.target.value)"
  @change="saveTrade(getTrade(month.num, tradeNo).id, month.num, tradeNo)"
  ...
/>

<!-- Percent input -->
<input 
  type="number" 
  :value="getTrade(month.num, tradeNo).percent"
  @input="updateTradeField(month.num, tradeNo, 'percent', $event.target.value)"
  @change="saveTrade(getTrade(month.num, tradeNo).id, month.num, tradeNo)"
  ...
/>

<!-- Trade Date input -->
<input 
  type="date" 
  :value="getTrade(month.num, tradeNo).trade_date"
  @input="updateTradeField(month.num, tradeNo, 'trade_date', $event.target.value)"
  @change="saveTrade(getTrade(month.num, tradeNo).id, month.num, tradeNo)"
  ...
/>
```

#### 2. Local State Update ([`TradingPivotGrid.vue:358-367`](powerdealer_f/src/components/trading/TradingPivotGrid.vue:358))

```javascript
const updateTradeField = (month, tradeNo, field, value) => {
  const key = `${month}-${tradeNo}`
  if (!editingTrade.value[key]) {
    editingTrade.value[key] = { ...getTrade(month, tradeNo) }
  }
  editingTrade.value[key][field] = value
  
  // Recalculate totals locally
  recalculateLocally(month)
}
```

#### 3. Save Function ([`TradingPivotGrid.vue:373-390`](powerdealer_f/src/components/trading/TradingPivotGrid.vue:373))

```javascript
const saveTrade = async (tradeId, month, tradeNo) => {
  const key = `${month}-${tradeNo}`
  const tradeData = editingTrade.value[key]
  
  if (!tradeData || !tradeId) return
  
  try {
    await store.updateTrade(tradeId, {
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
```

### Frontend - Store ([`trading.js:160-182`](powerdealer_f/src/stores/trading.js:160))

```javascript
const updateTrade = async (id, tradeData) => {
  saveLoading.value = true
  saveError.value = null
  
  try {
    const response = await tradingApi.updateTrade(id, tradeData)  // PUT request
    const updatedTrade = extractTradingData(response)
    
    // Refresh pivot data after updating trade
    if (selectedCustomer.value && selectedYear.value) {
      await fetchPivotData(selectedCustomer.value, selectedYear.value)
    }
    
    return updatedTrade
  } catch (err) {
    saveError.value = getErrorMessage(err)
    const fieldErrors = getFieldErrors(err)
    console.error('Failed to update trade:', err)
    throw { message: saveError.value, fieldErrors }
  } finally {
    saveLoading.value = false
  }
}
```

### Frontend - API Client ([`trading.js:72-74`](powerdealer_f/src/api/trading.js:72))

```javascript
updateTrade(id, data) {
  return api.put(`/trades/${id}/`, data)  // PUT - full update
}

patchTrade(id, data) {
  return api.patch(`/trades/${id}/`, data)  // PATCH - partial update (exists but unused!)
}
```

### Backend - Trade Update Endpoint ([`views.py:477-517`](powerdealer/trading/views.py:477))

```python
def put(self, request, trade_id):
    """Update a trade (full update)."""
    trade, error_response = self._get_trade(request, trade_id)
    if error_response:
        return error_response

    serializer = TradeSerializer(trade, data=request.data)  # No partial=True
    if serializer.is_valid():
        trade = serializer.save()
        logger.info(f"Trade updated: {trade.id}")
        return Response({
            'success': True,
            'message': 'Trade updated successfully.',
            'data': TradeSerializer(trade).data,
        })
    return Response({
        'success': False,
        'message': 'Please check your input.',
        'errors': serializer.errors,
    }, status=status.HTTP_400_BAD_REQUEST)

def patch(self, request, trade_id):
    """Update a trade (partial update)."""
    ...
    serializer = TradeSerializer(trade, data=request.data, partial=True)  # partial=True
    ...
```

### Backend - Serializer Validation ([`serializers.py:221-261`](powerdealer/trading/serializers.py:221))

```python
def validate(self, attrs):
    # If mprn is provided, look up the customer
    mprn = attrs.pop('mprn', None)
    if mprn and not attrs.get('customer'):
        try:
            customer = Customer.objects.get(mprn=mprn)
            attrs['customer'] = customer
        except Customer.DoesNotExist:
            raise serializers.ValidationError({'mprn': 'Customer with this MPRN not found.'})
    
    # Validate that customer is provided
    if not attrs.get('customer'):
        # BUG: This fails for PATCH requests where customer is not being updated!
        raise serializers.ValidationError({'customer_id': 'Either customer_id or mprn is required.'})
    
    # Validate percent total doesn't exceed 100%
    customer = attrs.get('customer')
    month = attrs.get('month')
    year = attrs.get('year')
    percent = attrs.get('percent', 0)

    if customer and month and year:
        # ... validation logic
```

---

## Gap Analysis

### Problem 1: Wrong HTTP Method

| Aspect | Current | Expected |
|--------|---------|----------|
| HTTP Method | PUT | PATCH |
| Data Sent | `{p_therm, percent, trade_date}` | Same |
| Backend Expectation | All required fields | Only changed fields |

The `saveTrade` function calls `store.updateTrade()` which uses PUT. For a PUT request, the `TradeSerializer` requires all non-readonly fields:
- `customer` or `customer_id` or `mprn`
- `month`
- `year`
- `p_therm`
- `percent`
- `trade_date`

But only `p_therm`, `percent`, and `trade_date` are sent.

### Problem 2: Serializer Validation Bug

Even if we switch to PATCH, the serializer's `validate()` method has a bug:

```python
if not attrs.get('customer'):
    raise serializers.ValidationError({'customer_id': 'Either customer_id or mprn is required.'})
```

For a PATCH request updating only `p_therm`, `percent`, and `trade_date`:
- `attrs` = `{p_therm, percent, trade_date}`
- `attrs.get('customer')` = `None`
- Validation fails!

The fix should check if this is a partial update and use `self.instance.customer` when customer is not in attrs.

---

## Solution Design

### Option A: Minimal Fix (Recommended)

This approach fixes both bugs with minimal code changes.

#### Backend Changes

**File: [`powerdealer/trading/serializers.py`](powerdealer/trading/serializers.py)**

```python
def validate(self, attrs):
    # If mprn is provided, look up the customer
    mprn = attrs.pop('mprn', None)
    if mprn and not attrs.get('customer'):
        try:
            customer = Customer.objects.get(mprn=mprn)
            attrs['customer'] = customer
        except Customer.DoesNotExist:
            raise serializers.ValidationError({'mprn': 'Customer with this MPRN not found.'})
    
    # For partial updates, use existing customer from instance
    if not attrs.get('customer'):
        if self.instance:
            attrs['customer'] = self.instance.customer
        else:
            raise serializers.ValidationError({'customer_id': 'Either customer_id or mprn is required.'})
    
    # For partial updates, use existing month/year from instance
    customer = attrs.get('customer')
    month = attrs.get('month')
    year = attrs.get('year')
    percent = attrs.get('percent', 0)

    # Use instance values for partial updates
    if self.instance:
        if month is None:
            month = self.instance.month
        if year is None:
            year = self.instance.year

    if customer and month and year:
        # Get existing trades for this customer/month/year
        queryset = Trade.objects.filter(
            customer=customer,
            month=month,
            year=year
        )

        # Exclude current instance if updating
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        total_percent = sum(t.percent for t in queryset)
        new_total = total_percent + percent

        if new_total > 100:
            raise serializers.ValidationError({
                'percent': f"Total booked ({new_total}%) would exceed 100%. Current total: {total_percent}%"
            })

    return attrs
```

#### Frontend Changes

**File: [`powerdealer_f/src/components/trading/TradingPivotGrid.vue`](powerdealer_f/src/components/trading/TradingPivotGrid.vue)**

Change line 380 from:
```javascript
await store.updateTrade(tradeId, {
```

To:
```javascript
await store.patchTrade(tradeId, {
```

**Alternative**: If you want to keep using `updateTrade`, modify the store to use PATCH:

**File: [`powerdealer_f/src/stores/trading.js`](powerdealer_f/src/stores/trading.js)**

Change line 165 from:
```javascript
const response = await tradingApi.updateTrade(id, tradeData)
```

To:
```javascript
const response = await tradingApi.patchTrade(id, tradeData)
```

---

### Option B: Comprehensive Fix

This approach provides better UX with optimistic updates and error handling.

#### Additional Frontend Changes

**File: [`powerdealer_f/src/components/trading/TradingPivotGrid.vue`](powerdealer_f/src/components/trading/TradingPivotGrid.vue)**

1. Add optimistic update to local state
2. Add error handling with rollback
3. Add visual feedback during save

```javascript
const saveTrade = async (tradeId, month, tradeNo) => {
  const key = `${month}-${tradeNo}`
  const tradeData = editingTrade.value[key]
  
  if (!tradeData || !tradeId) return
  
  // Store original data for rollback
  const originalTrade = getTrade(month, tradeNo)
  
  try {
    // Optimistic update - update local state immediately
    store.updateLocalTrade(tradeId, {
      p_therm: parseFloat(tradeData.p_therm),
      percent: parseFloat(tradeData.percent),
      trade_date: tradeData.trade_date
    })
    
    // Persist to database
    await store.patchTrade(tradeId, {
      p_therm: parseFloat(tradeData.p_therm),
      percent: parseFloat(tradeData.percent),
      trade_date: tradeData.trade_date
    })
    
    delete editingTrade.value[key]
    emit('trade-updated', tradeId)
  } catch (err) {
    // Rollback on error
    store.updateLocalTrade(tradeId, originalTrade)
    console.error('Failed to save trade:', err)
    // Show error to user
    alert('Failed to save changes. Please try again.')
  }
}
```

**File: [`powerdealer_f/src/stores/trading.js`](powerdealer_f/src/stores/trading.js)**

Add method for optimistic local updates:

```javascript
const updateLocalTrade = (tradeId, tradeData) => {
  if (!pivotData.value?.months) return
  
  // Find and update the trade in pivot data
  for (const month of pivotData.value.months) {
    const tradeIndex = month.trades?.findIndex(t => t.id === tradeId)
    if (tradeIndex !== -1 && tradeIndex !== undefined) {
      month.trades[tradeIndex] = { ...month.trades[tradeIndex], ...tradeData }
      
      // Recalculate totals
      month.total_percent = month.trades.reduce((sum, t) => sum + parseFloat(t.percent || 0), 0)
      
      const weightedSum = month.trades.reduce((sum, t) => sum + (parseFloat(t.p_therm || 0) * parseFloat(t.percent || 0)), 0)
      month.average_price_achieved = month.total_percent > 0 ? weightedSum / month.total_percent : 0
      break
    }
  }
}
```

---

## Implementation Checklist

### Backend (Required)

- [ ] **Fix serializer validation for partial updates** in [`serializers.py`](powerdealer/trading/serializers.py)
  - Use `self.instance` values for missing fields during PATCH requests
  - Ensure percent validation works correctly for partial updates

### Frontend (Required)

- [ ] **Change to PATCH request** in one of these locations:
  - Option 1: Change `saveTrade` to call `store.patchTrade()` in [`TradingPivotGrid.vue`](powerdealer_f/src/components/trading/TradingPivotGrid.vue)
  - Option 2: Change `updateTrade` action to use `tradingApi.patchTrade()` in [`trading.js`](powerdealer_f/src/stores/trading.js)

### Frontend (Optional Enhancements)

- [ ] Add optimistic updates for better UX
- [ ] Add visual feedback during save (loading indicator on cell)
- [ ] Add error handling with rollback
- [ ] Add debouncing to prevent excessive API calls during rapid edits

---

## Testing Plan

### Unit Tests

1. **Backend - Test PATCH endpoint**
   ```python
   def test_patch_trade_partial_update(self):
       """Test that PATCH works with only p_therm, percent, trade_date"""
       trade = Trade.objects.create(...)
       response = self.client.patch(f'/trades/{trade.id}/', {
           'p_therm': '0.5000',
           'percent': '25.00',
           'trade_date': '2024-01-15'
       })
       self.assertEqual(response.status_code, 200)
   ```

2. **Backend - Test serializer validation**
   ```python
   def test_serializer_partial_validation(self):
       """Test that serializer validates partial updates correctly"""
       trade = Trade.objects.create(...)
       serializer = TradeSerializer(trade, data={
           'percent': '50.00'
       }, partial=True)
       self.assertTrue(serializer.is_valid())
   ```

### Integration Tests

1. Edit a cell value in the pivot grid
2. Click outside the cell to trigger save
3. Verify the value persists after page refresh
4. Verify the value persists after creating a "new set"

---

## API Endpoints Summary

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/trades/` | GET | List trades | ✅ Working |
| `/trades/` | POST | Create trade | ✅ Working |
| `/trades/{id}/` | GET | Get single trade | ✅ Working |
| `/trades/{id}/` | PUT | Full update | ⚠️ Requires all fields |
| `/trades/{id}/` | PATCH | Partial update | ❌ Serializer bug |
| `/trades/{id}/` | DELETE | Delete trade | ✅ Working |
| `/trading/pivot/` | GET | Get pivot data | ✅ Working |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Existing data corruption | Low | High | Test thoroughly in staging |
| API breaking other clients | Low | Medium | PATCH is additive, PUT still works |
| Performance impact | Low | Low | PATCH is lighter than PUT |

---

## Conclusion

The root cause is a mismatch between the frontend sending partial data and the backend expecting full data for PUT requests, combined with a serializer validation bug that prevents PATCH from working correctly.

The recommended fix is:
1. **Backend**: Fix serializer to handle partial updates properly
2. **Frontend**: Switch from PUT to PATCH for inline edits

This is a minimal, low-risk change that will enable inline editing persistence.
