<template>
  <div class="search-bar-wrapper">
    
    <header class="top-header">
      <div class="logo">
        <svg class="logo-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
        </svg>
        <span class="logo-text">TripFind</span>
      </div>
      
      <div class="trip-type-toggle">
        <button :class="{ active: tripType === 'oneway' }" @click="tripType = 'oneway'">One Way</button>
        <button :class="{ active: tripType === 'return' }" @click="tripType = 'return'">Return</button>
      </div>
      
      <div class="header-subtitle">Search the best flights across the globe</div>
    </header>

    <div class="search-grid">
      <div class="grid-column border-right">
        <AirportCountryInput title="DEPARTURE" @update-data="handleDepartureUpdate">
          <template #icon>
            <svg class="header-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
              <polyline points="9 22 9 12 15 12 15 22"></polyline>
            </svg>
          </template>
        </AirportCountryInput>
        <DateRange title="DEPARTURE DATES" @update-dates="handleDepartureDates"/>
      </div>

      <div class="grid-column">
        <AirportCountryInput title="ARRIVAL" @update-data="handleArrivalUpdate">
          <template #icon>
            <svg class="header-icon arrival-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
              <circle cx="12" cy="10" r="3"></circle>
            </svg>
          </template>
        </AirportCountryInput>
        <DateRange title="RETURN DATES" :disabled="tripType === 'oneway'" @update-dates="handleReturnDates"/>
      </div>
    </div>

    <div class="preferences-section" v-show="tripType === 'return'">
      <h4 class="preferences-title">TRIP PREFERENCES</h4>
      
      <div class="preferences-row">
        <label class="toggle-container">
          <div class="toggle-switch">
            <input type="checkbox" v-model="provideStayDays" class="sr-only">
            <div class="toggle-track"></div>
            <div class="toggle-thumb"></div>
          </div>
          <span class="toggle-text">Specify Stay Duration</span>
        </label>

        <div class="stay-duration-box" v-if="provideStayDays">
          <input type="number" v-model.number="minStay" placeholder="Min" :min="calculatedBounds.min" :max="calculatedBounds.max" @change="clampMin" class="stay-input">
          <span class="stay-divider">-</span>
          <input type="number" v-model.number="maxStay" placeholder="Max" :min="calculatedBounds.min" :max="calculatedBounds.max" @change="clampMax" class="stay-input">
          <span class="stay-unit">days</span>
        </div>

        <div class="vertical-divider"></div>

        <label class="checkbox-container">
          <input type="checkbox" v-model="weekendStay" class="custom-checkbox">
          <span class="checkbox-text">Weekend flights only</span>
        </label>
      </div>
    </div>

    <footer class="bottom-footer">
      <div class="search-status">
        Searching for <strong>{{ tripType === 'oneway' ? 'One-Way' : 'Return' }}</strong> flights
      </div>
      <button class="search-submit-btn" @click="submitSearch" :disabled="isLoading" :class="{ 'opacity-75 cursor-not-allowed': isLoading }">
        <svg v-if="!isLoading" class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <span v-else class="mr-2 loader-spinner"></span>
        {{ isLoading ? 'Searching...' : 'Search Flights' }}
      </button>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import AirportCountryInput from './AirportCountryInput.vue'; 
import DateRange from './DateRange.vue';

const props = defineProps({
  isLoading: { type: Boolean, default: false }
});

const emit = defineEmits(['search', 'error']);

const tripType = ref('oneway');
const formData = ref({ departure: null, arrival: null, departureDates: null, returnDates: null });

const provideStayDays = ref(false);
const minStay = ref('');
const maxStay = ref('');
const weekendStay = ref(false);

const handleDepartureUpdate = (data) => { formData.value.departure = data; };
const handleArrivalUpdate = (data) => { formData.value.arrival = data; };
const handleDepartureDates = (dates) => { formData.value.departureDates = dates; };
const handleReturnDates = (dates) => { formData.value.returnDates = dates; };

const calculatedBounds = computed(() => {
  const dep = formData.value.departureDates;
  const ret = formData.value.returnDates;
  if (!dep || !ret || !dep.from || !ret.from) return { min: 1, max: 99 };

  const dStart = new Date(dep.from);
  const dEnd = dep.to ? new Date(dep.to) : dStart; 
  const rStart = new Date(ret.from);
  const rEnd = ret.to ? new Date(ret.to) : rStart; 
  const msPerDay = 1000 * 60 * 60 * 24;
  
  return {
    min: Math.max(0, Math.round((rStart - dEnd) / msPerDay)),
    max: Math.max(0, Math.round((rEnd - dStart) / msPerDay))
  };
});

watch(provideStayDays, (isActive) => {
  if (isActive) {
    minStay.value = calculatedBounds.value.min;
    maxStay.value = calculatedBounds.value.max;
  } else {
    minStay.value = ''; maxStay.value = '';
  }
});

const clampMin = () => {
  if (minStay.value === '' || minStay.value === null) return;
  const bounds = calculatedBounds.value;
  if (minStay.value < bounds.min) minStay.value = bounds.min;
  if (minStay.value > bounds.max) minStay.value = bounds.max;
  if (maxStay.value !== '' && minStay.value > maxStay.value) minStay.value = maxStay.value;
};

const clampMax = () => {
  if (maxStay.value === '' || maxStay.value === null) return;
  const bounds = calculatedBounds.value;
  if (maxStay.value > bounds.max) maxStay.value = bounds.max;
  if (maxStay.value < bounds.min) maxStay.value = bounds.min;
  if (minStay.value !== '' && maxStay.value < minStay.value) maxStay.value = minStay.value;
};

const submitSearch = () => {
  const depDates = formData.value.departureDates;
  if (!depDates?.from || !depDates?.to) {
    emit('error', 'Departure start and end dates are required.');
    return;
  }

  const payload = {
    dep_date_start: depDates.from,
    dep_date_end: depDates.to,
    weekend_flights: false
  };

  const dep = formData.value.departure;
  if (dep) {
    if (dep.mode === 'country' && dep.countries && dep.countries.length > 0) {
      payload.dep_airport_country_code = dep.countries[0].code.trim();
    } 
    else if (dep.mode === 'airport' && dep.airports && dep.airports.length > 0) {
      payload.dep_airports = dep.airports.map(a => a.iata_code);
      
      if (payload.dep_airports.length === 1 && dep.radius > 0) {
        payload.dep_max_distance_km = Number(dep.radius);
      }
    }
  }

  const arr = formData.value.arrival;
  if (arr) {
    if (arr.mode === 'country' && arr.countries && arr.countries.length > 0) {
      payload.arr_airport_country_code = arr.countries[0].code.trim();
    } 
    else if (arr.mode === 'airport' && arr.airports && arr.airports.length > 0) {
      payload.arr_airports = arr.airports.map(a => a.iata_code);
      
      if (payload.arr_airports.length === 1 && arr.radius > 0) {
        payload.arr_max_distance_km = Number(arr.radius);
      }
    }
  }

  if (tripType.value === 'return') {
    const retDates = formData.value.returnDates;
    if (!retDates?.from || !retDates?.to) {
      emit('error', 'Return start and end dates are required for Round Trip.');
      return;
    }
    
    payload.arr_date_start = retDates.from;
    payload.arr_date_end = retDates.to;

    if (provideStayDays.value && minStay.value !== '' && maxStay.value !== '') {
      payload.min_stay_days = Number(minStay.value);
      payload.max_stay_days = Number(maxStay.value);
    }

    if (weekendStay.value) {
      payload.weekend_flights = true;
    }
  }

  emit('search', { payload, isReturn: tripType.value === 'return' });
};
</script>

<style scoped>
.search-bar-wrapper { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 24px; overflow: hidden; width: calc(100% - 32px); margin: 40px auto; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }
.top-header { display: flex; align-items: center; justify-content: space-between; padding: 20px 32px; border-bottom: 1px solid #e2e8f0; }
.logo { display: flex; align-items: center; gap: 8px; color: #2563eb; }
.logo-icon { width: 32px; height: 32px; }
.logo-text { font-size: 30px; line-height: 2.25rem; font-weight: 800; letter-spacing: -0.05em; }
.trip-type-toggle { display: flex; background: #edf2f7; padding: 4px; border-radius: 9999px; }
.trip-type-toggle button { padding: 8px 24px; border: none; background: transparent; border-radius: 9999px; font-size: 14px; font-weight: 600; color: #4a5568; cursor: pointer; transition: all 0.2s; }
.trip-type-toggle button.active { background: white; color: #2b6cb0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.header-subtitle { font-size: 14px; color: #4a5568; font-weight: 500; }
.search-grid { display: grid; grid-template-columns: 1fr 1fr; }
.grid-column { padding: 32px; }
.border-right { border-right: 1px solid #e2e8f0; }
.header-icon { width: 20px; height: 20px; color: #2b6cb0; }
.arrival-icon { color: #ed8936; }
.preferences-section { padding: 24px 32px; border-top: 1px solid #e2e8f0; background: #fcfcfd; }
.preferences-title { font-size: 12px; font-weight: 700; color: #718096; text-transform: uppercase; letter-spacing: 0.5px; margin: 0 0 16px 0; }
.preferences-row { display: flex; align-items: center; flex-wrap: wrap; gap: 24px; }
.toggle-container { display: flex; align-items: center; cursor: pointer; gap: 12px; }
.sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); border: 0; }
.toggle-switch { position: relative; width: 44px; height: 24px; }
.toggle-track { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background-color: #cbd5e0; border-radius: 24px; transition: background-color 0.2s; }
.toggle-thumb { position: absolute; top: 2px; left: 2px; width: 20px; height: 20px; background-color: white; border-radius: 50%; transition: transform 0.2s; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }
input:checked + .toggle-track { background-color: #2563eb; }
input:checked ~ .toggle-thumb { transform: translateX(20px); }
.toggle-text { font-size: 15px; font-weight: 600; color: #2d3748; }
.stay-duration-box { display: flex; align-items: center; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 6px 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.02); }
.stay-input { width: 44px; border: none; border-bottom: 1px solid #cbd5e0; outline: none; font-size: 14px; font-weight: 600; color: #4a5568; text-align: center; padding: 2px; background: transparent; }
.stay-input:focus { border-bottom-color: #2563eb; }
.stay-input::-webkit-outer-spin-button, .stay-input::-webkit-inner-spin-button { margin: 0; }
.stay-divider { color: #a0aec0; margin: 0 10px; font-weight: 500; }
.stay-unit { font-size: 13px; font-weight: 600; color: #718096; margin-left: 10px; }
.vertical-divider { width: 1px; height: 28px; background-color: #e2e8f0; }
.checkbox-container { display: flex; align-items: center; cursor: pointer; gap: 12px; }
.custom-checkbox { width: 20px; height: 20px; border: 1px solid #cbd5e0; border-radius: 6px; accent-color: #2563eb; cursor: pointer; }
.checkbox-text { font-size: 15px; font-weight: 600; color: #2d3748; }
.bottom-footer { display: flex; align-items: center; justify-content: space-between; padding: 20px 32px; background: #f7fafc; border-top: 1px solid #e2e8f0; }
.search-status { font-size: 14px; color: #4a5568; }
.search-submit-btn { display: flex; align-items: center; gap: 8px; background: #2b6cb0; color: white; border: none; padding: 12px 28px; border-radius: 9999px; font-size: 16px; font-weight: 600; cursor: pointer; transition: background 0.2s; }
.search-submit-btn:hover { background: #2c5282; }
.btn-icon { width: 18px; height: 18px; }
.loader-spinner { border: 3px solid rgba(255, 255, 255, 0.3); border-radius: 50%; border-top: 3px solid white; width: 18px; height: 18px; animation: spin 1s linear infinite; display: inline-block; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>