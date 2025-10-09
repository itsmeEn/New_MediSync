<template>
  <q-dialog v-model="isOpen" persistent>
    <q-card class="hospital-info-modal" style="min-width: 500px">
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Hospital Information Required</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>

      <q-card-section>
        <p class="text-body2 q-mb-md text-grey-7">
          Please provide your hospital information before saving your settings. This information is required for proper identification and verification.
        </p>

        <div class="q-gutter-md">
          <q-input
            v-model="hospitalInfo.name"
            label="Hospital Name *"
            outlined
            :rules="[val => !!val || 'Hospital name is required']"
            :error="!!errors.name"
            :error-message="errors.name"
          />

          <q-input
            v-model="hospitalInfo.address"
            label="Hospital Address *"
            type="textarea"
            outlined
            rows="3"
            :rules="[val => !!val || 'Hospital address is required']"
            :error="!!errors.address"
            :error-message="errors.address"
          />

          <q-input
            v-model="hospitalInfo.city"
            label="City *"
            outlined
            :rules="[val => !!val || 'City is required']"
            :error="!!errors.city"
            :error-message="errors.city"
          />

          <div class="row q-gutter-md">
            <div class="col">
              <q-input
                v-model="hospitalInfo.state"
                label="State/Province *"
                outlined
                :rules="[val => !!val || 'State/Province is required']"
                :error="!!errors.state"
                :error-message="errors.state"
              />
            </div>
            <div class="col">
              <q-input
                v-model="hospitalInfo.zipCode"
                label="ZIP/Postal Code *"
                outlined
                :rules="[val => !!val || 'ZIP/Postal code is required']"
                :error="!!errors.zipCode"
                :error-message="errors.zipCode"
              />
            </div>
          </div>

          <q-input
            v-model="hospitalInfo.phone"
            label="Hospital Phone Number"
            outlined
            mask="(###) ### - ####"
            placeholder="(555) 123 - 4567"
          />

          <q-input
            v-model="hospitalInfo.website"
            label="Hospital Website"
            outlined
            placeholder="https://www.hospital.com"
          />
        </div>
      </q-card-section>

      <q-card-actions align="right" class="q-pa-md">
        <q-btn
          flat
          label="Cancel"
          color="grey"
          @click="handleCancel"
        />
        <q-btn
          label="Continue"
          color="primary"
          @click="handleContinue"
          :loading="loading"
          :disable="!isFormValid"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

// Props
interface Props {
  modelValue: boolean
  existingHospitalInfo?: HospitalInfo
}

interface HospitalInfo {
  name: string
  address: string
  city: string
  state: string
  zipCode: string
  phone?: string
  website?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  existingHospitalInfo: () => ({
    name: '',
    address: '',
    city: '',
    state: '',
    zipCode: '',
    phone: '',
    website: ''
  })
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'hospital-info-provided': [hospitalInfo: HospitalInfo]
  'cancelled': []
}>()

// Reactive data
const isOpen = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const loading = ref(false)

const hospitalInfo = ref<HospitalInfo>({
  name: '',
  address: '',
  city: '',
  state: '',
  zipCode: '',
  phone: '',
  website: ''
})

const errors = ref({
  name: '',
  address: '',
  city: '',
  state: '',
  zipCode: ''
})

// Computed properties
const isFormValid = computed(() => {
  return hospitalInfo.value.name.trim() !== '' &&
         hospitalInfo.value.address.trim() !== '' &&
         hospitalInfo.value.city.trim() !== '' &&
         hospitalInfo.value.state.trim() !== '' &&
         hospitalInfo.value.zipCode.trim() !== ''
})

// Watch for existing hospital info
watch(() => props.existingHospitalInfo, (newInfo) => {
  if (newInfo) {
    hospitalInfo.value = { ...newInfo }
  }
}, { immediate: true })

// Methods
const validateForm = (): boolean => {
  errors.value = {
    name: '',
    address: '',
    city: '',
    state: '',
    zipCode: ''
  }

  let isValid = true

  if (!hospitalInfo.value.name.trim()) {
    errors.value.name = 'Hospital name is required'
    isValid = false
  }

  if (!hospitalInfo.value.address.trim()) {
    errors.value.address = 'Hospital address is required'
    isValid = false
  }

  if (!hospitalInfo.value.city.trim()) {
    errors.value.city = 'City is required'
    isValid = false
  }

  if (!hospitalInfo.value.state.trim()) {
    errors.value.state = 'State/Province is required'
    isValid = false
  }

  if (!hospitalInfo.value.zipCode.trim()) {
    errors.value.zipCode = 'ZIP/Postal code is required'
    isValid = false
  }

  return isValid
}

const handleContinue = () => {
  if (!validateForm()) {
    return
  }

  loading.value = true

  try {
    // Emit the hospital information
    emit('hospital-info-provided', { ...hospitalInfo.value })
    
    // Close the modal
    isOpen.value = false
  } catch (error) {
    console.error('Error processing hospital information:', error)
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  emit('cancelled')
  isOpen.value = false
}

// Reset form when modal closes
watch(isOpen, (newValue) => {
  if (!newValue) {
    // Reset form after a short delay to avoid visual glitches
    setTimeout(() => {
      hospitalInfo.value = {
        name: '',
        address: '',
        city: '',
        state: '',
        zipCode: '',
        phone: '',
        website: ''
      }
      errors.value = {
        name: '',
        address: '',
        city: '',
        state: '',
        zipCode: ''
      }
    }, 300)
  }
})
</script>

<style scoped>
.hospital-info-modal {
  max-width: 600px;
}

.q-card-section p {
  margin-bottom: 16px;
}

.q-input {
  margin-bottom: 8px;
}

.q-card-actions {
  border-top: 1px solid #e0e0e0;
}
</style>