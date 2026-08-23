<template>
  <div class="min-h-screen py-8 px-4 sm:px-8 w-full bg-slate-50 text-slate-900 font-sans">
    <div class="w-full flex flex-col items-center max-w-7xl mx-auto">
      
      <SearchParamsBar 
        :is-loading="loading" 
        @search="executeSearch"
        @error="handleError"
      />

      <div v-if="errorMsg" class="w-full bg-red-50 border-l-4 border-red-500 p-5 rounded-r-lg mb-8 shadow-sm">
        <h3 class="text-base font-bold text-red-800">Search Error</h3>
        <p class="mt-1 text-sm text-red-700">{{ errorMsg }}</p>
      </div>

      <div v-if="result" class="w-full flex flex-col space-y-12 pb-16 px-4 sm:px-0">

        <div v-if="!hasFlightResults" class="w-full rounded-lg border border-slate-200 bg-white p-8 text-center shadow-sm">
          <h2 class="text-xl font-bold text-slate-800">Found no flights</h2>
        </div>
        
        <section v-if="result.best_overall?.flights?.length > 0">
          <div class="flex items-center space-x-3 mb-6">
            <div class="p-2 bg-green-100 rounded-lg text-green-600 shadow-sm">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
            </div>
            <h2 class="text-2xl font-extrabold text-slate-800">Best Flights</h2>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            <CheapestFlightCard 
              v-for="flight in result.best_overall.flights" 
              :key="flight.outbound_flight.id" 
              :flight-data="flight" 
              badge="Cheapest Option"
              @select="handleFlightSelection"
            />
          </div>
        </section>

        <section v-if="hasFlexibleDurations">
          <div class="flex items-center space-x-3 mb-6">
            <div class="p-2 bg-purple-100 rounded-lg text-purple-600 shadow-sm">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
              </svg>
            </div>
            <h2 class="text-2xl font-extrabold text-slate-800">Flexible Stay Options</h2>
          </div>
          
          <div class="relative w-full">
            
            <div class="flex overflow-x-auto space-x-6 py-4 pl-2 pr-12 no-scrollbar snap-x mandatory">
              
              <CheapestStayCard 
                v-for="(flightGroup, days) in result.flexible_durations" 
                :key="days" 
                :flight-data="flightGroup" 
                class="snap-start"
              />
              
              <div class="w-4 flex-shrink-0"></div>
            </div>
            
            <div class="absolute right-0 top-0 bottom-0 w-24 bg-gradient-to-l from-slate-50 to-transparent pointer-events-none"></div>
          </div>
        </section>

        <section v-if="hasFlightResults && result.calendar_view">
          <div class="grid grid-cols-1 xl:grid-cols-2 gap-10">
            
            <div v-if="result.calendar_view.outbound">
              <div class="flex items-center space-x-3 mb-6">
                <svg class="w-7 h-7 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
                </svg>
                <h2 class="text-2xl font-extrabold text-slate-800">Outbound Calendar</h2>
              </div>
              <FlightCalendar :calendar-data="result.calendar_view.outbound" />
            </div>

            <div v-if="isReturnTrip && result.calendar_view.return && Object.keys(result.calendar_view.return).length > 0">
              <div class="flex items-center space-x-3 mb-6">
                <svg class="w-7 h-7 text-orange-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                  <circle cx="12" cy="10" r="3"></circle>
                </svg>
                <h2 class="text-2xl font-extrabold text-slate-800">Return Calendar</h2>
              </div>
              <FlightCalendar :calendar-data="result.calendar_view.return" />
            </div>

          </div>
        </section>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

import SearchParamsBar from './components/SearchParamsBar.vue';
import CheapestFlightCard from './components/CheapestFlightCard.vue';
import CheapestStayCard from './components/CheapestStayCard.vue';
import FlightCalendar from './components/FlightCalendar.vue';

const loading = ref(false);
const errorMsg = ref(null);
const result = ref(null);
const isReturnTrip = ref(false);

const handleError = (msg) => {
  errorMsg.value = msg;
};

const hasFlexibleDurations = computed(() => {
  return isReturnTrip.value && 
         result.value?.flexible_durations && 
         Object.keys(result.value.flexible_durations).length > 0;
});

const hasFlightResults = computed(() => {
  if (!result.value) {
    return false;
  }

  return result.value.best_overall?.flights?.length > 0 ||
    Object.keys(result.value.calendar_view?.outbound || {}).length > 0 ||
    Object.keys(result.value.calendar_view?.return || {}).length > 0;
});

const executeSearch = async ({ payload, isReturn }) => {
  loading.value = true;
  errorMsg.value = null;
  result.value = null;
  isReturnTrip.value = isReturn;

  try {
    const response = await fetch('http://localhost:8000/api/v1/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      const detailMsg = Array.isArray(errData.detail) 
        ? errData.detail.map(e => `${e.loc.join('.')}: ${e.msg}`).join(' | ') 
        : (errData.detail || `HTTP Error ${response.status}`);
      throw new Error(detailMsg);
    }

    result.value = await response.json();
    
  } catch (err) {
    errorMsg.value = err.message;
  } finally {
    loading.value = false;
  }
};

const handleFlightSelection = (flightData) => {
  console.log("Wybrano lot:", flightData);
};
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
</style>