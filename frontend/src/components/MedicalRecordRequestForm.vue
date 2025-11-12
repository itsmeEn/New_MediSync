<template>
  <q-form @submit="handleSubmit" class="q-gutter-md">
    <q-select
      v-model="store.form.requestType"
      :options="requestTypeOptions"
      outlined
      label="Type of Request"
      color="teal"
      placeholder="Select request type"
      :rules="[val => !!val || 'Please select a request type']"
      behavior="menu"
    >
      <template #prepend>
        <q-icon name="description" color="teal" />
      </template>
    </q-select>

    <q-select
      v-if="store.form.requestType === 'medical_certificate'"
      v-model="store.form.purpose"
      :options="purposeOptions"
      emit-value
      map-options
      outlined
      label="Purpose of Request"
      color="teal"
      placeholder="Select purpose"
      :rules="store.form.requestType === 'medical_certificate' ? [val => !!val || 'Please select a purpose'] : []"
      behavior="menu"
    >
      <template #prepend>
        <q-icon name="info" color="teal" />
      </template>
    </q-select>

    <div v-if="store.form.requestType === 'medical_certificate'" class="row q-gutter-md">
      <div class="col-12 col-md-6">
        <q-input
          v-model="store.form.dateRangeStart"
          label="Start Date"
          type="date"
          outlined
          color="teal"
          :rules="store.form.requestType === 'medical_certificate' ? [val => !!val || 'Start date is required'] : []"
        >
          <template #prepend>
            <q-icon name="event" color="teal" />
          </template>
        </q-input>
      </div>
      <div class="col-12 col-md-6">
        <q-input
          v-model="store.form.dateRangeEnd"
          label="End Date"
          type="date"
          outlined
          color="teal"
          :rules="store.form.requestType === 'medical_certificate' ? [val => !!val || 'End date is required'] : []"
        >
          <template #prepend>
            <q-icon name="event" color="teal" />
          </template>
        </q-input>
      </div>
    </div>

    <q-select
      v-model="store.form.recipient"
      :options="store.recipientOptions"
      outlined
      label="Recipient (Doctor)"
      color="teal"
      emit-value
      map-options
      :loading="store.isLoadingRecipients"
      :error="!!store.recipientError"
      :error-message="store.recipientError || ''"
      :rules="[val => !!val || 'Please select a recipient']"
    >
      <template #prepend>
        <q-icon name="person" color="teal" />
      </template>
      <template #option="scope">
        <q-item v-if="(scope.opt as any).type === 'header'" dense class="bg-grey-2">
          <q-item-section>
            <div class="text-caption text-grey-7">{{ (scope.opt as any).label }}</div>
          </q-item-section>
        </q-item>
        <q-item v-else v-bind="scope.itemProps">
          <q-item-section>
            <q-item-label>{{ (scope.opt as StaffOption).label }}</q-item-label>
            <q-item-label caption>
              <span v-if="(scope.opt as StaffOption).group === 'current'" class="text-positive">Current</span>
              <span v-else class="text-grey-7">Historical</span>
              • Doctor
              <span v-if="(scope.opt as StaffOption).specialization"> • {{ (scope.opt as StaffOption).specialization }}</span>
              <span v-if="(scope.opt as StaffOption).department"> • {{ (scope.opt as StaffOption).department }}</span>
            </q-item-label>
          </q-item-section>
        </q-item>
      </template>
    </q-select>

    <q-input
      v-model="store.form.details"
      type="textarea"
      outlined
      label="Additional Details (Optional)"
      color="teal"
      placeholder="Enter additional details about your request"
      rows="3"
      autogrow
    >
      <template #prepend>
        <q-icon name="message" color="teal" />
      </template>
    </q-input>

    <q-btn
      type="submit"
      color="teal"
      class="full-width"
      label="Submit Record Request"
      :loading="store.isSubmitting"
      unelevated
      size="lg"
    />
  </q-form>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar'
import { useMedicalRequestStore, type StaffOption } from 'src/stores/medicalRequest'

const $q = useQuasar()
const store = useMedicalRequestStore()

const requestTypeOptions = [
  { label: 'Medical Certificate', value: 'medical_certificate' },
  { label: 'Full Medical Records (Last 5 Years)', value: 'full_records' },
  { label: 'Specific Lab Results Only', value: 'lab_results' },
  { label: 'Immunization History', value: 'immunization' },
  { label: 'General Inquiry', value: 'general_inquiry' }
]

const purposeOptions = [
  { label: 'Work Leave', value: 'work_leave' },
  { label: 'School/University', value: 'school_university' },
  { label: 'Travel/Immigration', value: 'travel_immigration' },
  { label: 'Insurance Claim', value: 'insurance_claim' },
  { label: 'Legal/Disability', value: 'legal_disability' },
  { label: 'Fitness to Work', value: 'fitness_to_work' },
  { label: 'Other', value: 'other' }
]

const emit = defineEmits<{ (e: 'submitted', created: unknown): void }>()

const handleSubmit = async () => {
  try {
    const created = await store.submit()
    if (created) emit('submitted', created)
    $q.notify({ type: 'positive', message: 'Request submitted successfully', position: 'top' })
  } catch (error: unknown) {
    const msg = typeof error === 'string' ? error : 'Error submitting request. Please try again.'
    $q.notify({ type: 'negative', message: msg, position: 'top' })
  }
}
</script>

<style scoped>
</style>