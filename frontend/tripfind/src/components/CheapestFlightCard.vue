<template>
  <div class="flight-card" v-if="outboundInfo">
    <div class="card-header">
      <div v-if="badge" class="badge">
        {{ badge }}
      </div>
      <div v-else></div> 
      
      <div class="price-container">
        <span class="price">{{ totalPrice }}</span>
        <span class="currency">{{ currency }}</span>
      </div>
    </div>

    <div class="flight-details">
      <div class="flight-row">
        <div class="icon-wrapper outbound-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="5" y1="12" x2="19" y2="12"></line>
            <polyline points="12 5 19 12 12 19"></polyline>
          </svg>
        </div>
        <div class="info">
          <div class="label">OUTBOUND</div>
          <div class="route">
            {{ outboundInfo.from }} ➔ {{ outboundInfo.to }} 
            <span class="datetime">• {{ outboundInfo.date }}, {{ outboundInfo.time }}</span>
          </div>
        </div>
      </div>

      <div class="flight-row" v-if="returnInfo">
        <div class="icon-wrapper return-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="19" y1="12" x2="5" y2="12"></line>
            <polyline points="12 19 5 12 12 5"></polyline>
          </svg>
        </div>
        <div class="info">
          <div class="label">RETURN</div>
          <div class="route">
            {{ returnInfo.from }} ➔ {{ returnInfo.to }}
            <span class="datetime">• {{ returnInfo.date }}, {{ returnInfo.time }}</span>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  flightData: { type: Object, required: true },
  badge: { type: String, default: '' }
});

const emit = defineEmits(['select']);

const formatDateTime = (timestampUtc, timezone) => {
  if (!timestampUtc) return { date: '', time: '' };
  const dateObj = new Date(timestampUtc * 1000);
  
  return {
    date: dateObj.toLocaleDateString('pl-PL', { day: '2-digit', month: '2-digit', year: 'numeric', timeZone: timezone }),
    time: dateObj.toLocaleTimeString('pl-PL', { hour: '2-digit', minute: '2-digit', timeZone: timezone })
  };
};

const outboundInfo = computed(() => {
  const flight = props.flightData?.outbound_flight;
  if (!flight) return null;
  
  const { date, time } = formatDateTime(flight.dep_time_utc, flight.departure_airport.timezone);
  return { from: flight.dep_iata, to: flight.arr_iata, date, time };
});

const returnInfo = computed(() => {
  const flight = props.flightData?.return_flight;
  if (!flight) return null;

  const { date, time } = formatDateTime(flight.dep_time_utc, flight.departure_airport.timezone);
  return { from: flight.dep_iata, to: flight.arr_iata, date, time };
});

const totalPrice = computed(() => {
  const outPrice = props.flightData?.outbound_flight?.price || 0;
  const retPrice = props.flightData?.return_flight?.price || 0;
  return (outPrice + retPrice).toFixed(2);
});

const currency = computed(() => props.flightData?.outbound_flight?.price_currency || 'PLN');
const handleSelect = () => emit('select', props.flightData);
</script>

<style scoped>
.flight-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 24px;
  max-width: 450px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.badge { background-color: #e6f4ea; color: #137333; font-weight: 700; font-size: 14px; padding: 6px 12px; border-radius: 20px; }
.price-container { display: flex; flex-direction: column; align-items: flex-end; line-height: 1.1; }
.price { font-size: 36px; font-weight: 800; color: #1a202c; letter-spacing: -0.5px; }
.currency { font-size: 14px; font-weight: 700; color: #a0aec0; margin-top: 2px; }

.flight-details { display: flex; flex-direction: column; gap: 20px; margin-bottom: 32px; }
.flight-row { display: flex; align-items: center; gap: 16px; }

.icon-wrapper { width: 48px; height: 48px; border-radius: 50%; display: flex; justify-content: center; align-items: center; flex-shrink: 0; }
.icon-wrapper svg { width: 24px; height: 24px; }
.outbound-icon { background-color: #f0f7ff; color: #3b82f6; }
.return-icon { background-color: #fff6eb; color: #ea580c; }

.info { display: flex; flex-direction: column; gap: 4px; }
.label { font-size: 12px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }
.route { font-size: 18px; font-weight: 700; color: #1e293b; }
.datetime { font-size: 14px; font-weight: 500; color: #64748b; margin-left: 6px; }

.select-btn { width: 100%; background-color: #0f172a; color: #ffffff; font-size: 16px; font-weight: 600; padding: 16px; border: none; border-radius: 12px; cursor: pointer; transition: background-color 0.2s; }
.select-btn:hover { background-color: #1e293b; }
</style>