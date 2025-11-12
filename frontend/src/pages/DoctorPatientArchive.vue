<template>
  <q-layout view="hHh Lpr fFf" class="page-background">
    <NurseHeader @toggle-drawer="rightDrawerOpen = !rightDrawerOpen" />
    <NurseSidebar v-model="rightDrawerOpen" active-route="patient-archive" />

    <q-page-container class="page-container-with-fixed-header">
      <div class="patient-management-content">
        <q-card class="greeting-card">
          <q-card-section class="greeting-content">
            <div class="greeting-text">
              <h4 class="greeting-title">Patient Archive</h4>
              <p class="greeting-subtitle">Browse and export archived patient assessments</p>
            </div>
          </q-card-section>
        </q-card>
        
        <!-- Archive Analytics -->
        <q-card class="white-card section-spacing">
          <q-card-section class="card-header">
            <h5 class="card-title">Archive Analytics</h5>
          </q-card-section>
          <q-card-section class="card-content">
            <div class="row q-col-gutter-md">
              <div class="col-12 col-md-6">
                <div class="chart-container">
                  <q-inner-loading :showing="archivesLoading"><q-spinner color="primary" /></q-inner-loading>
                  <Line 
                    :data="archiveVolumeChartData" 
                    :options="archiveVolumeChartOptions"
                    aria-label="Archived patient volume line chart"
                  />
                </div>
              </div>
              <div class="col-12 col-md-6">
                <div class="q-mb-sm flex items-center q-gutter-sm">
                  <div class="text-subtitle2">Sort</div>
                  <q-btn-toggle
                    v-model="forecastSortOrder"
                    toggle-color="primary"
                    size="sm"
                    :options="[
                      { label: 'Desc', value: 'desc' },
                      { label: 'Asc', value: 'asc' }
                    ]"
                  />
                </div>
                <div class="chart-container">
                  <q-inner-loading :showing="archivesLoading"><q-spinner color="primary" /></q-inner-loading>
                  <Bar 
                    :data="archiveIllnessForecastData"
                    :options="archiveIllnessForecastOptions"
                    aria-label="Illness forecast bar chart"
                  />
                </div>
              </div>
              <div class="col-12 col-md-6">
                <div class="chart-container">
                  <q-inner-loading :showing="archivesLoading"><q-spinner color="primary" /></q-inner-loading>
                  <Doughnut 
                    :data="archiveGenderData" 
                    :options="doughnutOptions"
                    aria-label="Archive gender distribution doughnut chart"
                  />
                </div>
              </div>
              <div class="col-12 col-md-6">
                <div class="q-mb-sm flex items-center q-gutter-sm">
                  <div class="text-subtitle2">Show Top</div>
                  <q-select v-model="topMedCount" :options="[3,5,8,10]" dense outlined emit-value map-options style="width: 90px;" />
                </div>
                <div class="chart-container">
                  <q-inner-loading :showing="archivesLoading"><q-spinner color="primary" /></q-inner-loading>
                  <Bar 
                    :data="archiveMedicationData" 
                    :options="{
                      ...barOptions,
                      indexAxis: 'y',
                      scales: {
                        x: { title: { display: true, text: 'Total Dispensed (count)' }, ticks: { precision: 0, callback: (v: number | string) => `${Math.round(Number(v))}` } },
                        y: { title: { display: true, text: 'Medicine' } }
                      },
                      plugins: {
                        ...barOptions.plugins,
                        title: { display: true, text: 'Most Dispensed Medications', font: { size: 16, weight: 'bold' } }
                      }
                    }"
                    aria-label="Archive medication analysis horizontal bar chart"
                  />
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>

        <!-- Main archive card (search, results) -->
        <q-card class="white-card archive-card section-spacing">
          <q-card-section class="card-header">
            <h5 class="card-title">Patient Archive</h5>
          </q-card-section>

          <q-card-section class="card-content">
            <div class="row q-col-gutter-md q-mb-lg">
              <div class="col-12 col-md-6"><q-input v-model="archiveFilters.query" label="Patient Name or ID" outlined dense/></div>
              <div class="col-12 col-sm-6 col-md-3"><q-input v-model="archiveFilters.assessment_type" label="Assessment Type" outlined dense/></div>
              <div class="col-12 col-sm-6 col-md-3"><q-input v-model="archiveFilters.medical_condition" label="Medical Condition" outlined dense/></div>
            </div>
            <div class="row q-col-gutter-md q-mb-md">
              <div class="col-12 col-sm-6 col-md-3"><q-input v-model="archiveFilters.start_date" label="Start Date" type="date" outlined dense/></div>
              <div class="col-12 col-sm-6 col-md-3"><q-input v-model="archiveFilters.end_date" label="End Date" type="date" outlined dense/></div>
              <div class="col-12 col-sm-6 col-md-3"><q-btn color="primary" icon="search" label="Search" class="full-width" :loading="archivesLoading" @click="searchArchives"/></div>
            </div>

            <q-inner-loading :showing="archivesLoading"><q-spinner color="primary"/></q-inner-loading>

            <div v-if="!archivesLoading && archivedRecords.length === 0" class="empty-section">
              <q-icon name="inventory_2" size="48px" color="grey-5" />
              <p class="empty-text">No archived records</p>
            </div>

            <q-list v-else bordered separator>
              <q-item v-for="rec in archivedRecords" :key="rec.id">
                <q-item-section>
                  <q-item-label>{{ rec.patient_name }} — {{ rec.assessment_type }} · {{ formatDateDisplay(rec.last_assessed_at) }}</q-item-label>
                  <q-item-label caption>
                    Condition: {{ rec.medical_condition || '—' }} • Hospital: {{ rec.hospital_name || '—' }}
                  </q-item-label>
                </q-item-section>
                <q-item-section side top>
                  <q-chip color="grey-8" text-color="white" size="sm">Archived</q-chip>
                </q-item-section>
                <q-item-section side>
                  <div class="row q-gutter-xs">
                    <q-btn dense flat icon="visibility" color="primary" @click="viewArchive(rec)" />
                    <q-btn dense flat icon="download" color="secondary" @click="exportArchive(rec)" />
                  </div>
                </q-item-section>
              </q-item>
            </q-list>

            <div class="row q-gutter-sm q-mt-md" v-if="archivedRecords.length">
              <q-btn outline color="primary" icon="file_download" label="Export Results" @click="exportFilteredArchives"/>
            </div>

            <q-dialog v-model="showArchiveDetail">
              <q-card style="max-width: 1000px; width: 90vw">
                <q-card-section>
                  <div class="text-h6">Archived Assessment</div>
                </q-card-section>
                <q-separator/>
                <q-card-section>
                  <div class="q-mb-sm"><b>Patient:</b> {{ selectedArchive?.patient_name }}</div>
                  <div class="q-mb-sm"><b>MRN:</b> {{ getAssessmentField('mrn', selectedArchive) || '—' }}</div>
                  <div class="q-mb-sm"><b>Assessment:</b> {{ selectedArchive?.assessment_type }}</div>
                  <div class="q-mb-sm"><b>Last Assessed:</b> {{ formatDateDisplay(selectedArchive?.last_assessed_at || '') }}</div>
                  <div class="q-mb-sm"><b>Condition:</b> {{ selectedArchive?.medical_condition || '—' }}</div>
                  <div class="q-mb-sm"><b>Hospital:</b> {{ selectedArchive?.hospital_name || '—' }}</div>
                  <div class="q-mb-sm"><b>Medical History:</b> {{ selectedArchive?.medical_history_summary || '—' }}</div>
                  <div class="q-mt-md">
                    <div class="text-subtitle2 q-mb-xs">Assessment Data</div>
                    <pre class="q-pa-sm bg-grey-2" style="white-space: pre-wrap;">{{ formatJson(selectedArchive?.decrypted_assessment_data) }}</pre>
                  </div>
                </q-card-section>
                <q-separator/>
                <q-card-actions align="right">
                  <q-btn flat label="Close" color="primary" v-close-popup/>
                  <q-btn flat label="Export" color="secondary" @click="selectedArchive && exportArchive(selectedArchive)"/>
                </q-card-actions>
              </q-card>
            </q-dialog>
          </q-card-section>
        </q-card>
      </div>
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useQuasar } from 'quasar'
import NurseHeader from 'components/NurseHeader.vue'
import NurseSidebar from 'components/NurseSidebar.vue'
import { api } from 'boot/axios'
import { Bar, Doughnut, Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
} from 'chart.js'
import type { TooltipItem, Point } from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement
)

const palette = {
  blue: '#2196f3', blueDark: '#1976d2',
  green: '#4caf50', greenDark: '#388e3c',
  orange: '#ff9800', orangeDark: '#f57c00',
  red: '#f44336', redDark: '#d32f2f',
  purple: '#9c27b0', purpleDark: '#7b1fa2'
}

// Sidebar state
const rightDrawerOpen = ref(false)

// Archive state and methods
interface ArchiveRecord {
  id: number;
  patient_id: number;
  patient_name: string;
  assessment_type: string;
  medical_condition: string;
  medical_history_summary?: string;
  diagnostics?: Record<string, unknown>;
  last_assessed_at: string;
  hospital_name?: string;
  decrypted_assessment_data?: Record<string, unknown>;
}

const $q = useQuasar()
const archivesLoading = ref(false)
const archivedRecords = ref<ArchiveRecord[]>([])
const showArchiveDetail = ref(false)
const selectedArchive = ref<ArchiveRecord | null>(null)

const archiveFilters = ref({
  query: '',
  patient_id: '',
  assessment_type: '',
  medical_condition: '',
  start_date: '',
  end_date: ''
})

const formatDateDisplay = (dateStr: string): string => {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  return d.toLocaleString()
}

const formatJson = (obj: unknown): string => {
  try {
    return JSON.stringify(obj ?? {}, null, 2)
  } catch {
    return obj ? '[Unable to format object]' : ''
  }
}

// Safely read a primitive field from decrypted assessment data
const getAssessmentField = (key: string, rec?: ArchiveRecord | null): string | number | undefined => {
  const data = rec?.decrypted_assessment_data
  const val = data ? data[key] : undefined
  return typeof val === 'string' || typeof val === 'number' ? val : undefined
}

const buildArchiveParams = (): Record<string, string> => {
  const params: Record<string, string> = {}
  const f = archiveFilters.value
  if (f.query) params.patient_name = f.query
  if (f.patient_id) params.patient_id = f.patient_id
  if (f.assessment_type) params.assessment_type = f.assessment_type
  if (f.medical_condition) params.condition = f.medical_condition
  if (f.start_date) params.start = f.start_date
  if (f.end_date) params.end = f.end_date
  return params
}

const searchArchives = async () => {
  archivesLoading.value = true
  try {
    const res = await api.get('/operations/archives/', { params: buildArchiveParams() })
    const list = Array.isArray(res.data)
      ? res.data
      : Array.isArray(res.data?.results)
        ? res.data.results
        : (res.data?.records || [])
    archivedRecords.value = list as ArchiveRecord[]
  } catch (err: unknown) {
    console.error('Archive search failed:', err)
    let msg = 'Archive search failed'
    if (typeof err === 'object' && err !== null) {
      const e = err as { response?: { data?: { error?: unknown } }, message?: unknown }
      const apiMsg = e.response?.data?.error
      if (typeof apiMsg === 'string' && apiMsg.trim()) {
        msg = apiMsg
      } else if (typeof e.message === 'string' && e.message.trim()) {
        msg = e.message
      }
    } else if (typeof err === 'string' && err.trim()) {
      msg = err
    }
    $q.notify({ type: 'negative', message: msg, position: 'top' })
  } finally {
    archivesLoading.value = false
  }
}



const viewArchive = async (rec: ArchiveRecord) => {
  try {
    const res = await api.get(`/operations/archives/${rec.id}/`)
    selectedArchive.value = (res.data?.record || res.data) as ArchiveRecord
    showArchiveDetail.value = true
  } catch (err) {
    console.error('Failed to load archive detail:', err)
    $q.notify({ type: 'negative', message: 'Failed to load archive detail', position: 'top' })
  }
}

const exportArchive = async (rec: ArchiveRecord) => {
  try {
    const res = await api.get(`/operations/archives/${rec.id}/export/`, { responseType: 'blob' })
    const blob = new Blob([res.data], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `archive_${rec.id}.json`
    a.click()
    URL.revokeObjectURL(url)
    $q.notify({ type: 'positive', message: 'Archive exported', position: 'top' })
  } catch (err) {
    console.error('Export failed:', err)
    $q.notify({ type: 'negative', message: 'Export failed', position: 'top' })
  }
}

const exportFilteredArchives = async () => {
  try {
    const res = await api.get('/operations/archives/export/', { params: buildArchiveParams(), responseType: 'blob' })
    const blob = new Blob([res.data], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'archives_export.json'
    a.click()
    URL.revokeObjectURL(url)
    $q.notify({ type: 'positive', message: 'Archives exported', position: 'top' })
  } catch (err) {
    console.error('Export failed:', err)
    $q.notify({ type: 'negative', message: 'Export failed', position: 'top' })
  }
}

// ===== Archive Analytics (derived from archivedRecords) =====
const topMedCount = ref<number>(5)
const forecastSortOrder = ref<'desc' | 'asc'>('desc')

// Volume over time: count records per day/month; use month label for readability
const archiveVolumeEntries = computed(() => {
  const map: Record<string, number> = {}
  for (const rec of archivedRecords.value) {
    const d = rec.last_assessed_at ? new Date(rec.last_assessed_at) : null
    if (!d) continue
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
    map[key] = (map[key] || 0) + 1
  }
  return Object.entries(map).sort((a, b) => a[0].localeCompare(b[0]))
})
const archiveVolumeYLabels = computed(() => archiveVolumeEntries.value.map((e) => e[0]))
const archiveVolumeChartData = computed(() => {
  const points = archiveVolumeEntries.value.map((e, idx) => ({ x: e[1], y: idx }))
  return {
    datasets: [
      { label: 'Actual Volume', data: points, borderColor: palette.green, backgroundColor: 'rgba(76,175,80,0.15)', borderWidth: 2, tension: 0.3, pointRadius: 3, pointBackgroundColor: palette.green }
    ]
  }
})
const archiveVolumeChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'bottom' as const },
    title: { display: true, text: 'Archived Patient Volume', font: { size: 16, weight: 'bold' as const } },
    tooltip: { callbacks: { label: (ctx: TooltipItem<'line'>) => { const p = ctx.parsed as Point; const timeLabel = archiveVolumeYLabels.value[Math.round(Number(p.y))] || ''; return `${Math.round(p.x)} patients on ${timeLabel}` } } }
  },
  scales: {
    x: { title: { display: true, text: 'Patients (count)' }, ticks: { precision: 0, callback: (v: number | string) => `${Math.round(Number(v))}` } },
    y: { type: 'linear' as const, title: { display: true, text: 'Time Period' }, ticks: { callback: (value: string | number) => {
      const idx = Math.round(Number(value))
      return archiveVolumeYLabels.value[idx] || ''
    } } }
  }
}

// Illness forecast: counts of medical_condition sorted
const archiveIllnessForecastData = computed(() => {
  const map: Record<string, number> = {}
  for (const rec of archivedRecords.value) {
    if (rec.medical_condition) {
      map[rec.medical_condition] = (map[rec.medical_condition] || 0) + 1
    }
  }
  const arr = Object.entries(map).map(([condition, count]) => ({ condition, count }))
  arr.sort((a, b) => forecastSortOrder.value === 'desc' ? b.count - a.count : a.count - b.count)
  return {
    labels: arr.map(x => x.condition),
    datasets: [
      { label: 'Predicted Cases', data: arr.map(x => x.count), backgroundColor: palette.orange, borderColor: palette.orangeDark, borderWidth: 1 }
    ]
  }
})

// Illness forecast chart options
const archiveIllnessForecastOptions = {
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: 'y' as const,
  scales: {
    x: { title: { display: true, text: 'Predicted Cases (count)' }, ticks: { precision: 0, callback: (v: number | string) => `${Math.round(Number(v))}` } },
    y: { title: { display: true, text: 'Illness Type' } }
  },
  plugins: {
    legend: { position: 'top' as const },
    title: { display: true, text: 'Illness Forecast', font: { size: 16, weight: 'bold' as const } },
    tooltip: { callbacks: { label: (ctx: TooltipItem<'bar'>) => {
      const parsedUnknown = ctx.parsed as unknown;
      let val = 0;
      if (typeof parsedUnknown === 'number') {
        val = parsedUnknown;
      } else if (typeof parsedUnknown === 'object' && parsedUnknown !== null) {
        const p = parsedUnknown as { x?: number; y?: number };
        val = typeof p.x === 'number' ? p.x : typeof p.y === 'number' ? p.y : 0;
      }
      return `Predicted: ${Math.round(val)} cases`;
    } } }
  }
}

// Gender distribution from decrypted assessment
const archiveGenderData = computed(() => {
  const map: Record<string, number> = {}
  for (const rec of archivedRecords.value) {
    const g = getAssessmentField('gender', rec)
    if (typeof g === 'string' && g) {
      map[g] = (map[g] || 0) + 1
    }
  }
  return {
    labels: Object.keys(map),
    datasets: [
      { data: Object.values(map), backgroundColor: [palette.blue, '#e91e63'], borderColor: [palette.blueDark, '#c2185b'], borderWidth: 2 }
    ]
  }
})
const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'bottom' as const },
    title: { display: true, text: 'Gender Distribution', font: { size: 14, weight: 'bold' as const } },
    tooltip: {
      callbacks: {
        label: (ctx: TooltipItem<'doughnut'>) => {
          const total = ctx.dataset.data.reduce((s: number, n: number) => s + n, 0)
          const val = ctx.parsed
          const pct = total ? Math.round((val / total) * 100) : 0
          return `${ctx.label}: ${val} (${pct}%)`
        }
      }
    }
  }
}

// Medication analysis from decrypted data
const archiveMedicationData = computed(() => {
  const map: Record<string, number> = {}
  type MedicationItem = string | { name?: string }
  type AssessmentData = Record<string, unknown> & { medications?: MedicationItem[] }
  for (const rec of archivedRecords.value) {
    const meds = (rec.decrypted_assessment_data as AssessmentData | undefined)?.medications
    if (Array.isArray(meds)) {
      for (const m of meds) {
        const name = typeof m === 'string' ? m : (typeof (m as { name?: unknown }).name === 'string' ? (m as { name?: unknown }).name as string : '')
        if (name) map[name] = (map[name] || 0) + 1
      }
    }
  }
  const arr = Object.entries(map).map(([name, count]) => ({ name, count }))
  arr.sort((a, b) => b.count - a.count)
  const top = arr.slice(0, topMedCount.value)
  return {
    labels: top.map(x => x.name),
    datasets: [
      { label: 'Total Dispensed', data: top.map(x => x.count), backgroundColor: [palette.purple, palette.blue, palette.green, palette.orange, palette.red], borderColor: [palette.purpleDark, palette.blueDark, palette.greenDark, palette.orangeDark, palette.redDark], borderWidth: 1 }
    ]
  }
})
const barOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'top' as const } },
}
</script>

<style scoped>
/* Page background */
.page-background {
  background: #f6f7f8;
  min-height: 100vh;
  background-size: cover;
}

/* Keep header space */
.page-container-with-fixed-header {
  padding-top: 50px;
}

.patient-management-content {
  max-width: none;        
  width: 100%;
  margin: 0;
  padding: 18px 28px;     
  box-sizing: border-box;
}

.greeting-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 22px 24px;
  box-shadow: 0 6px 24px rgba(17, 24, 39, 0.06);
  border: 1px solid rgba(0,0,0,0.04);
  position: relative;
  margin: 0 0 22px 0;
  overflow: visible;
  width: 100%;
}

/* Decorative thin top bar (matches the Appointment Calendar look) */
.greeting-card::before {
  content: "";
  position: absolute;
  left: 12px;
  right: 12px;
  top: 8px;
  height: 6px;
  border-radius: 6px;
  background: linear-gradient(90deg, rgba(40,102,96,0.95), rgba(46,153,124,0.6));
  opacity: 0.95;
  pointer-events: none;
  box-shadow: 0 2px 6px rgba(46,153,124,0.06);
}

.greeting-content {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  gap: 16px;
  position: relative;
  z-index: 1;
}

.greeting-text { padding: 6px 0; }
.greeting-title {
  font-size: 24px;
  margin: 0;
  color: #1f3f3a;
  font-weight: 700;
}
.greeting-subtitle {
  margin: 10px 0 0;
  color: #6b7a77;
  font-size: 14px;
}

/* Main white card (archive area) - stretch full width of parent */
.white-card {
  background: linear-gradient(180deg, #ffffff, #fcfdfd);
  border-radius: 12px;
  box-shadow: 0 10px 32px rgba(11,22,23,0.06);
  overflow: hidden;
  margin: 0;
  padding: 28px;
  width: 100%;
  border: 1px solid rgba(0,0,0,0.04);
  box-sizing: border-box;
}

/* Slightly larger inner spacing so controls appear wide and airy */
.card-header .card-title {
  font-size: 18px;
  font-weight: 700;
  color: #2a4b46;
  margin-bottom: 18px;
}
.card-content {
  padding-top: 8px;
}

/* empty state */
.empty-section {
  text-align: center;
  padding: 48px 0;
}
.empty-text {
  color: #8a9592;
}

/* Responsive fallbacks */
@media (max-width: 1100px) {
  .patient-management-content { 
    padding: 16px; 
  }
}
@media (max-width: 640px) {
  .greeting-title { 
    font-size: 20px; 
  }
  .greeting-subtitle { 
    font-size: 13px; 
  }
  .patient-management-content { 
    padding: 12px; 
  }
  .white-card { 
    padding: 16px; 
  }
}
</style>