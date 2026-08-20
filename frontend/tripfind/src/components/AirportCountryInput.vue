<template>
  <div class="search-widget">
    <div class="header">
      <slot name="icon"></slot>
      <h2>{{ title }}</h2>
    </div>

    <div class="mode-toggle">
      <button 
        :class="{ active: searchMode === 'airport' }" 
        @click="setMode('airport')"
      >
        Airport
      </button>
      <button 
        :class="{ active: searchMode === 'country' }" 
        @click="setMode('country')"
      >
        Country
      </button>
    </div>

    <div class="input-group">
      <label>{{ searchMode === 'airport' ? 'City or IATA code(s)' : 'Country or code' }}</label>
      
      <div class="autocomplete-container">
        <input 
          type="text" 
          v-model="searchQuery"
          @focus="openDropdown"
          @blur="closeDropdown"
          :placeholder="inputPlaceholder"
          :class="{ 'has-selection': hasSelection }"
        />

        <ul v-if="isDropdownOpen && searchMode === 'airport'" class="dropdown">
          <li v-if="sortedAirports.length === 0" class="no-results">
            No results
          </li>
          
          <li 
            v-for="airport in sortedAirports" 
            :key="airport.iata_code"
            @mousedown.prevent="toggleSelection(airport)"
            class="dropdown-item"
            :class="{ 'disabled-item': !isSelected(airport) && selectedAirports.length >= 3 }"
          >
            <input 
              type="checkbox" 
              :checked="isSelected(airport)"
              class="airport-checkbox"
              readonly
            />
            <div class="airport-info">
              <span class="city-name">{{ airport.city }}</span>
              <span class="airport-name">{{ airport.name }} ({{ airport.iata_code }})</span>
            </div>
          </li>
        </ul>

        <ul v-if="isDropdownOpen && searchMode === 'country'" class="dropdown">
          <li v-if="sortedCountries.length === 0" class="no-results">
            No results
          </li>
          
          <li 
            v-for="country in sortedCountries" 
            :key="country.code"
            @mousedown.prevent="toggleCountrySelection(country)"
            class="dropdown-item"
            :class="{ 'disabled-item': !isCountrySelected(country) && selectedCountries.length >= 1 }"
          >
            <input 
              type="checkbox" 
              :checked="isCountrySelected(country)"
              class="airport-checkbox"
              readonly
            />
            <div class="airport-info">
              <span class="city-name">{{ country.name }}</span>
              <span class="airport-name">{{ country.code }}</span>
            </div>
          </li>
        </ul>
      </div>
    </div>

    <div class="radius-group">
      <label>Include nearby up to</label>
      <div class="radius-input-wrapper">
        <input 
          type="number" 
          v-model="radius" 
          :disabled="isRadiusDisabled"
          min="0"
        />
      </div>
      <span class="unit">km</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';

const props = defineProps({
  title: {
    type: String,
    required: true,
    default: 'DEPARTURE'
  }
});

const emit = defineEmits(['update-data']);

const searchMode = ref('airport');
const searchQuery = ref('');
const isDropdownOpen = ref(false);
const radius = ref();

const selectedAirports = ref([]);
const selectedCountries = ref([]);

const allAirports = ref([]);
const allCountries = ref([]);

const fetchAirports = async () => {
  try {
    const response = await fetch('/api/v1/airports');
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const data = await response.json();
    allAirports.value = data;
  } catch (error) {
    console.error('Błąd podczas pobierania lotnisk:', error);
  }
};

const fetchCountries = async () => {
  try {
    const response = await fetch('/api/v1/countries');
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const data = await response.json();
    allCountries.value = data;
  } catch (error) {
    console.error('Błąd podczas pobierania krajów:', error);
  }
};

onMounted(() => {
  fetchAirports();
  fetchCountries();
});

const hasSelection = computed(() => {
  if (searchMode.value === 'airport') return selectedAirports.value.length > 0;
  return selectedCountries.value.length > 0;
});

const inputPlaceholder = computed(() => {
  if (searchMode.value === 'airport') {
    if (selectedAirports.value.length === 0) return 'Enter city...';
    return selectedAirports.value.map(a => a.iata_code).join(', ');
  } else {
    if (selectedCountries.value.length === 0) return 'Enter country...';
    return selectedCountries.value.map(c => c.code).join(', ');
  }
});

const sortedAirports = computed(() => {
  const query = searchQuery.value.toLowerCase();
  
  let filtered = allAirports.value.filter(airport => 
    airport.city.toLowerCase().includes(query) || 
    airport.iata_code.toLowerCase().includes(query)
  );

  return filtered.sort((a, b) => {
    const aSelected = isSelected(a);
    const bSelected = isSelected(b);
    
    if (aSelected && !bSelected) return -1;
    if (!aSelected && bSelected) return 1;
    return 0; 
  });
});

const sortedCountries = computed(() => {
  const query = searchQuery.value.toLowerCase();
  
  let filtered = allCountries.value.filter(country => 
    country.name.toLowerCase().includes(query) || 
    country.code.toLowerCase().includes(query)
  );

  return filtered.sort((a, b) => {
    const aSelected = isCountrySelected(a);
    const bSelected = isCountrySelected(b);
    
    if (aSelected && !bSelected) return -1;
    if (!aSelected && bSelected) return 1;
    return 0; 
  });
});

const setMode = (mode) => {
  searchMode.value = mode;
  searchQuery.value = '';
  isDropdownOpen.value = false;
};

const openDropdown = () => {
  isDropdownOpen.value = true;
  searchQuery.value = ''; 
};

const closeDropdown = () => {
  isDropdownOpen.value = false;
  searchQuery.value = '';
};

const toggleSelection = (airport) => {
  const index = selectedAirports.value.findIndex(a => a.iata_code === airport.iata_code);
  
  if (index === -1) {
    if (selectedAirports.value.length >= 3) return; 
    selectedAirports.value.push(airport);
  } else {
    selectedAirports.value.splice(index, 1);
  }
};

const isSelected = (airport) => {
  return selectedAirports.value.some(a => a.iata_code === airport.iata_code);
};

const toggleCountrySelection = (country) => {
  const index = selectedCountries.value.findIndex(c => c.code === country.code);
  
  if (index === -1) {
    if (selectedCountries.value.length >= 1) return; 
    selectedCountries.value.push(country);
  } else {
    selectedCountries.value.splice(index, 1);
  }
};

const isCountrySelected = (country) => {
  return selectedCountries.value.some(c => c.code === country.code);
};

const isRadiusDisabled = computed(() => {
  return searchMode.value === 'country' || selectedAirports.value.length > 1;
});

watch(isRadiusDisabled, (isDisabled) => {
  if (isDisabled) {
    radius.value = null;
  }
});

watch([selectedAirports, selectedCountries, radius, searchMode], () => {
  emit('update-data', {
    mode: searchMode.value,
    airports: selectedAirports.value,
    countries: selectedCountries.value,
    radius: radius.value
  });
}, { deep: true });
</script>

<style scoped>
.search-widget {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  max-width: 600px;
  margin: 20px auto;
  color: #333;
  background-color: #f7fafc; 
  padding: 20px;
  border-radius: 12px;
}

.header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  color: #1a2b49;
}
.header .icon {
  width: 24px;
  height: 24px;
  color: #2b6cb0;
}
.header h2 {
  font-size: 18px;
  font-weight: 700;
  margin: 0;
  letter-spacing: 0.5px;
}

.mode-toggle {
  display: flex;
  border: 1px solid #cbd5e0;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 24px;
  background: white;
}
.mode-toggle button {
  flex: 1;
  padding: 12px;
  border: none;
  background: transparent;
  font-size: 14px;
  font-weight: 600;
  color: #4a5568;
  cursor: pointer;
  transition: all 0.2s;
}
.mode-toggle button:first-child {
  border-right: 1px solid #cbd5e0;
}
.mode-toggle button.active {
  background-color: #ebf8ff;
  color: #2b6cb0;
}

.input-group {
  margin-bottom: 24px;
}
.input-group label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #4a5568;
  margin-bottom: 8px;
}
.autocomplete-container {
  position: relative;
}
.autocomplete-container > input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #cbd5e0;
  border-radius: 8px;
  font-size: 16px;
  box-sizing: border-box;
  outline: none;
  background: white;
}
.autocomplete-container > input:focus {
  border-color: #2b6cb0;
  box-shadow: 0 0 0 1px #2b6cb0;
}
.autocomplete-container > input.has-selection::placeholder {
  color: #000000 !important;
  opacity: 1 !important;
}

.dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 4px;
  background: white !important;
  border: 1px solid #cbd5e0;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  max-height: 250px;
  overflow-y: auto;
  z-index: 100;
  padding: 0;
  list-style: none;
}
.dropdown-item {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 10px 16px;
  cursor: pointer;
  border-bottom: 1px solid #edf2f7;
  transition: opacity 0.2s, background-color 0.2s;
}
.dropdown-item:last-child {
  border-bottom: none;
}
.dropdown-item:hover:not(.disabled-item) {
  background-color: #f7fafc;
}

.disabled-item {
  opacity: 0.4;
  cursor: not-allowed;
}

.airport-checkbox {
  flex-shrink: 0;
  margin-right: 12px;
  width: 16px !important;
  height: 16px !important;
  cursor: pointer;
  pointer-events: none;
}

.airport-info {
  display: flex;
  flex-direction: column;
  flex: 1 1 auto;
  text-align: left;
  min-width: 0;
  overflow: hidden; 
}
.city-name, .airport-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: block; 
}
.city-name {
  font-weight: 600;
  font-size: 14px;
  color: #2d3748 !important;
}
.airport-name {
  font-size: 12px;
  color: #718096 !important;
}
.no-results {
  padding: 12px 16px;
  color: #718096 !important;
  font-size: 14px;
  text-align: center;
}

.radius-group {
  display: flex;
  align-items: center;
  gap: 12px;
}
.radius-group label {
  font-size: 14px;
  font-weight: 600;
  color: #4a5568;
}
.radius-input-wrapper {
  position: relative;
}
.radius-input-wrapper input {
  width: 80px;
  padding: 8px 12px;
  border: 1px solid #cbd5e0;
  border-radius: 8px;
  font-size: 14px;
  text-align: center;
  outline: none;
  background: white;
}
.radius-input-wrapper input:focus {
  border-color: #2b6cb0;
}
.radius-input-wrapper input:disabled {
  background-color: #f7fafc;
  color: #a0aec0;
  cursor: not-allowed;
}
.unit {
  font-size: 14px;
  color: #4a5568;
  font-weight: 500;
}
</style>