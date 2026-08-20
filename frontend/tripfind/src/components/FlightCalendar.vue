<template>
  <div class="calendar-wrapper w-full">
    
    <div v-for="monthData in calendars" :key="monthData.monthName" class="mb-8">
      <h3 class="text-lg font-bold text-slate-600 mb-4 ml-1">{{ monthData.monthName }}</h3>
      
      <div class="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
        
        <div class="grid grid-cols-7 bg-slate-50 border-b border-slate-200">
          <div v-for="day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']" :key="day" 
               class="py-3 text-center text-xs font-bold text-slate-500 uppercase">
            {{ day }}
          </div>
        </div>
        
        <div class="grid grid-cols-7 bg-slate-100 gap-px border-b border-slate-200 last:border-b-0">
          <template v-for="(week, wIdx) in monthData.weeks" :key="wIdx">
            <div v-for="(cell, cIdx) in week" :key="cIdx" 
                 @click="handleDayClick(cell)"
                 class="bg-white h-24 p-2 flex flex-col justify-between transition-colors relative group"
                 :class="[
                    !cell ? 'bg-slate-50/50' : '',
                    cell && cell.data ? 'hover:bg-blue-50 cursor-pointer' : '',
                    cell && cell.isToday ? 'ring-2 ring-inset ring-blue-500' : ''
                 ]">
              
              <div v-if="cell" class="text-sm font-semibold" :class="cell.data ? 'text-slate-800' : 'text-slate-400'">
                {{ cell.day }}
              </div>
              
              <div v-if="cell && cell.data" class="text-center pb-1">
                <div class="font-extrabold text-blue-700 text-sm sm:text-base">
                  {{ cell.data.cheapest_price }}
                </div>
                <div class="text-[10px] font-bold text-slate-400 uppercase leading-none">
                  {{ cell.data.currency }}
                </div>
                <div class="absolute top-0 left-0 w-full h-1 bg-blue-500"></div>
              </div>
              
            </div>
          </template>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="isModalOpen && selectedDay" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex justify-center items-center z-50 p-4" @click.self="closeModal">
        <div class="bg-white w-full max-w-2xl rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
          
          <div class="bg-slate-50 px-6 py-4 border-b border-slate-200 flex justify-between items-center sticky top-0">
            <div>
              <h3 class="text-xl font-extrabold text-slate-800">Available Flights</h3>
              <p class="text-sm font-medium text-slate-500">{{ selectedDay.date }}</p>
            </div>
            <button @click="closeModal" class="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-200 rounded-full transition-colors">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
          </div>
          
          <div class="p-6 overflow-y-auto space-y-4 flex-1">
            <div v-for="flight in selectedDay.data.flights" :key="flight.id" class="border border-slate-200 rounded-xl p-5 hover:border-blue-300 transition-colors bg-white flex flex-col sm:flex-row gap-6 justify-between items-center shadow-sm hover:shadow-md">
              
              <div class="flex-1 w-full">
                <div class="flex items-center gap-2 mb-3">
                  <span class="text-xs font-bold px-2 py-1 bg-slate-100 text-slate-600 rounded-md uppercase tracking-wider">{{ flight.airline_name }}</span>
                  <span class="text-xs font-semibold text-slate-400">{{ flight.flight_number }}</span>
                </div>
                
                <div class="flex items-center justify-between w-full">
                    <div class="text-center sm:text-left">
                    <div class="text-2xl font-black text-slate-800">{{ formatTime(flight.dep_time_utc, flight.departure_airport.timezone) }}</div>
                    <div class="text-sm font-bold text-slate-500">{{ flight.dep_iata }}</div>
                    </div>

                    <div class="flex-1 flex flex-col items-center px-4">
                    <div class="text-xs font-semibold text-slate-400 mb-1">{{ flight.flight_time_mins }} mins</div>
                    <div class="w-full h-px bg-slate-300 relative">
                        <div class="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-2 border-t-2 border-r-2 border-slate-400 transform rotate-45"></div>
                    </div>
                    </div>

                    <div class="text-center sm:text-right">
                    <div class="text-2xl font-black text-slate-800">{{ formatTime(flight.arr_time_utc, flight.arrival_airport.timezone) }}</div>
                    <div class="text-sm font-bold text-slate-500">{{ flight.arr_iata }}</div>
                    </div>
                </div>
              </div>
              
              <div class="flex flex-col items-end justify-center sm:border-l border-slate-100 sm:pl-6 w-full sm:w-auto h-full">
                <div class="text-3xl font-black text-blue-700 leading-none mb-1">{{ flight.price }}</div>
                <div class="text-xs font-bold text-slate-400 uppercase tracking-wider">{{ flight.price_currency }}</div>
              </div>
              
            </div>
          </div>
          
        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  calendarData: {
    type: Object,
    required: true,
    default: () => ({})
  }
});

const isModalOpen = ref(false);
const selectedDay = ref(null);

const formatTime = (timestampUtc, timezone) => {
  if (!timestampUtc) return '';
  const dateObj = new Date(timestampUtc * 1000);
  
  const options = { hour: '2-digit', minute: '2-digit' };
  if (timezone) options.timeZone = timezone;
  
  return dateObj.toLocaleTimeString('pl-PL', options);
};

const handleDayClick = (cell) => {
  if (cell && cell.data && cell.data.flights) {
    selectedDay.value = cell;
    isModalOpen.value = true;
  }
};

const closeModal = () => {
  isModalOpen.value = false;
  selectedDay.value = null;
};

const generateCalendarStructure = (flightsData) => {
  if (!flightsData) return [];
  const dates = Object.keys(flightsData).sort();
  if (dates.length === 0) return [];

  const minDate = new Date(dates[0]);
  const maxDate = new Date(dates[dates.length - 1]);
  
  const calendars = [];
  let currMonth = new Date(minDate.getFullYear(), minDate.getMonth(), 1);
  const endMonth = new Date(maxDate.getFullYear(), maxDate.getMonth(), 1);
  
  const todayStr = new Date().toISOString().split('T')[0];

  while (currMonth <= endMonth) {
      const year = currMonth.getFullYear();
      const month = currMonth.getMonth();
      
      const daysInMonth = new Date(year, month + 1, 0).getDate();
      let firstDayJS = new Date(year, month, 1).getDay();
      let startOffset = firstDayJS === 0 ? 6 : firstDayJS - 1;

      const weeks = [];
      let currentWeek = Array(startOffset).fill(null);

      for (let d = 1; d <= daysInMonth; d++) {
          const mStr = String(month + 1).padStart(2, '0');
          const dStr = String(d).padStart(2, '0');
          const dateStr = `${year}-${mStr}-${dStr}`;

          currentWeek.push({
              day: d,
              date: dateStr,
              data: flightsData[dateStr] || null,
              isToday: dateStr === todayStr
          });

          if (currentWeek.length === 7) {
              weeks.push(currentWeek);
              currentWeek = [];
          }
      }

      if (currentWeek.length > 0) {
          while (currentWeek.length < 7) {
              currentWeek.push(null);
          }
          weeks.push(currentWeek);
      }

      const monthName = new Intl.DateTimeFormat('en-US', { month: 'long', year: 'numeric' }).format(currMonth);
      calendars.push({ monthName, weeks });

      currMonth.setMonth(currMonth.getMonth() + 1);
  }

  return calendars;
};

const calendars = computed(() => {
  return generateCalendarStructure(props.calendarData);
});
</script>

<style scoped>

:global(body:has(.fixed.inset-0)) {
  overflow: hidden;
}
</style>