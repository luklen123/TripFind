<template>
  <div v-if="isRoundTrip" class="flex-shrink-0">
    
    <div class="summary-card" @click="isModalOpen = true">
      <div class="days-stay">{{ daysStay }} DAYS STAY</div>
      <div class="price-line">
        <span class="price">{{ totalPrice }}</span>
        <span class="currency">{{ currency }}</span>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="isModalOpen" class="modal-overlay" @click.self="isModalOpen = false">
        <div class="modal-content">
          <div class="modal-header">
            <h3>Trip details</h3>
            <button class="close-btn" @click="isModalOpen = false">✕</button>
          </div>
          
          <div class="modal-body" v-if="modalData">
            <div class="flight-leg">
              <div class="leg-title">OUTBOUND</div>
              <div class="leg-route">{{ modalData.outbound.route }}</div>
              <div class="leg-datetime">
                Date: <strong>{{ modalData.outbound.date }}</strong><br>
                Time: <strong>{{ modalData.outbound.time }}</strong>
              </div>
            </div>

            <hr class="divider" />


            <div class="flight-leg">
              <div class="leg-title">RETURN</div>
              <div class="leg-route">{{ modalData.return.route }}</div>
              <div class="leg-datetime">
                Date: <strong>{{ modalData.return.date }}</strong><br>
                Time: <strong>{{ modalData.return.time }}</strong>
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
  flightData: {
    type: Object,
    required: true
  }
});

const isModalOpen = ref(false);

const isRoundTrip = computed(() => {
  return !!props.flightData?.return_flight;
});

const daysStay = computed(() => {
  if (!isRoundTrip.value) return 0;
  
  const outTime = props.flightData.outbound_flight.dep_time_utc;
  const retTime = props.flightData.return_flight.dep_time_utc;
  
  const diffInSeconds = retTime - outTime;
  const days = Math.round(diffInSeconds / (24 * 3600));
  
  return Math.max(1, days); 
});

const totalPrice = computed(() => {
  if (!isRoundTrip.value) return '0.00';
  const outPrice = props.flightData.outbound_flight.price || 0;
  const retPrice = props.flightData.return_flight.price || 0;
  return (outPrice + retPrice).toFixed(2);
});

const currency = computed(() => {
  return props.flightData?.outbound_flight?.price_currency || 'PLN';
});

const formatDateTime = (timestampUtc, timezone) => {
  if (!timestampUtc) return { date: '', time: '' };
  const dateObj = new Date(timestampUtc * 1000);
  return {
    date: dateObj.toLocaleDateString('pl-PL', { day: '2-digit', month: '2-digit', year: 'numeric', timeZone: timezone }),
    time: dateObj.toLocaleTimeString('pl-PL', { hour: '2-digit', minute: '2-digit', timeZone: timezone })
  };
};

const modalData = computed(() => {
  if (!isRoundTrip.value) return null;
  
  const outF = props.flightData.outbound_flight;
  const retF = props.flightData.return_flight;
  
  return {
    outbound: {
      route: `${outF.departure_airport.name} (${outF.dep_iata}) ➔ ${outF.arrival_airport.name} (${outF.arr_iata})`,
      ...formatDateTime(outF.dep_time_utc, outF.departure_airport.timezone)
    },
    return: {
      route: `${retF.departure_airport.name} (${retF.dep_iata}) ➔ ${retF.arrival_airport.name} (${retF.arr_iata})`,
      ...formatDateTime(retF.dep_time_utc, retF.departure_airport.timezone)
    }
  };
});
</script>

<style scoped>
.summary-card {
  background: #ffffff;
  border: 1.5px solid #e2e8f0;
  border-radius: 16px;
  padding: 20px 24px;
  display: inline-flex;
  flex-direction: column;
  gap: 8px;
  cursor: pointer;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  transition: all 0.2s ease;
  user-select: none;
  min-width: 170px;
}

.summary-card:hover {
  border-color: #9333ea;
  box-shadow: 0 4px 12px rgba(147, 51, 234, 0.1);
  transform: translateY(-2px);
}

.days-stay {
  color: #9333ea;
  font-size: 16px;
  font-weight: 800;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.price-line {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.price {
  color: #1e293b;
  font-size: 32px;
  font-weight: 800;
  letter-spacing: -0.5px;
}

.currency {
  color: #94a3b8;
  font-size: 16px;
  font-weight: 700;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.modal-content {
  background: white;
  width: 90%;
  max-width: 450px;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
  color: #1e293b;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #64748b;
  padding: 4px;
}

.close-btn:hover {
  color: #0f172a;
}

.flight-leg {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.leg-title {
  font-size: 12px;
  font-weight: 700;
  color: #9333ea;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.leg-route {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.leg-datetime {
  font-size: 14px;
  color: #64748b;
  line-height: 1.5;
}

.leg-datetime strong {
  color: #334155;
}

.divider {
  border: none;
  border-top: 1px dashed #cbd5e0;
  margin: 20px 0;
}
</style>