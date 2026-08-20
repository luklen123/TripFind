<template>
  <div class="date-range-container" :class="{ 'is-disabled': disabled }">
    <h3 class="section-title">{{ title || 'Choose Date Range' }}</h3>
    <div class="date-row">
      <div class="input-wrapper">
        <label>FROM</label>
        <input 
          type="date" 
          v-model="fromDate"
          :max="toDate"
          :disabled="disabled"
          class="native-date-input"
        />
      </div>
      
      <span class="separator">-</span>
      
      <div class="input-wrapper">
        <label>TO</label>
        <input 
          type="date" 
          v-model="toDate"
          :min="fromDate"
          :disabled="disabled"
          class="native-date-input"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  title: { type: String, required: false },
  disabled: { type: Boolean, default: false }
});

const emit = defineEmits(['update-dates']);

const fromDate = ref('');
const toDate = ref('');

watch([fromDate, toDate], () => {
  emit('update-dates', { from: fromDate.value, to: toDate.value });
});

watch(() => props.disabled, (isDisabled) => {
  if (isDisabled) {
    fromDate.value = '';
    toDate.value = '';
  }
});
</script>

<style scoped>
.date-range-container {
  margin-top: 24px;
  transition: opacity 0.3s ease;
}

.date-range-container.is-disabled {
  opacity: 0.4;
  pointer-events: none;
}

.section-title {
  font-size: 14px;
  font-weight: 700;
  color: #1a2b49;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 16px 0;
}

.date-row {
  display: flex;
  align-items: flex-end;
  gap: 12px;
}

.input-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.input-wrapper label {
  font-size: 12px;
  font-weight: 700;
  color: #718096;
  text-transform: uppercase;
  margin-bottom: 8px;
}

.separator {
  color: #a0aec0;
  font-size: 18px;
  padding-bottom: 12px;
}

.native-date-input {
  padding: 12px 14px;
  border: 1px solid #cbd5e0;
  border-radius: 8px;
  font-size: 16px;
  font-family: inherit;
  color: #2d3748;
  background-color: #ffffff;
  width: 100%;
  box-sizing: border-box;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.native-date-input:focus {
  border-color: #2b6cb0;
  box-shadow: 0 0 0 1px #2b6cb0;
}

.native-date-input:disabled {
  background-color: #f7fafc;
  cursor: not-allowed;
  color: #a0aec0;
}
</style>