<template>
  <div class="assessment-view">
    <div v-if="hasParticipants" class="section">
      <div class="section-title">Participants</div>
      <q-markup-table flat dense class="q-mt-xs">
        <thead>
          <tr>
            <th v-for="col in participantColumns" :key="col">{{ toTitleCase(col) }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, idx) in participants" :key="idx">
            <td v-for="col in participantColumns" :key="col">{{ formatValue(row[col]) }}</td>
          </tr>
        </tbody>
      </q-markup-table>
    </div>

    <div v-if="hasScores" class="section">
      <div class="section-title">Scores</div>
      <q-markup-table flat dense class="q-mt-xs">
        <tbody>
          <tr v-for="(val, key) in scores" :key="key">
            <td class="cell-key">{{ toTitleCase(key) }}</td>
            <td>{{ formatValue(val) }}</td>
          </tr>
        </tbody>
      </q-markup-table>
    </div>

    <div v-if="hasComments" class="section">
      <div class="section-title">Comments</div>
      <div class="comment-box">{{ commentsText }}</div>
    </div>

    <div v-for="section in otherSections" :key="section.title" class="section">
      <div class="section-title">{{ section.title }}</div>
      <div v-if="section.type === 'table'">
        <q-markup-table flat dense class="q-mt-xs">
          <thead v-if="section.columns && section.columns.length">
            <tr>
              <th v-for="col in section.columns" :key="col">{{ toTitleCase(col) }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, idx) in section.rows" :key="idx">
              <td v-for="col in section.columns" :key="col">{{ formatValue(row[col]) }}</td>
            </tr>
          </tbody>
        </q-markup-table>
      </div>
      <div v-else-if="section.type === 'kv'">
        <q-markup-table flat dense class="q-mt-xs">
          <tbody>
            <tr v-for="(val, key) in section.kv" :key="key">
              <td class="cell-key">{{ toTitleCase(key) }}</td>
              <td>{{ formatValue(val) }}</td>
            </tr>
          </tbody>
        </q-markup-table>
      </div>
      <ul v-else-if="section.type === 'list'" class="bullet-list">
        <li v-for="(item, idx) in section.items" :key="idx">{{ formatValue(item) }}</li>
      </ul>
      <div v-else class="monospace">{{ formatValue(section.raw) }}</div>
    </div>

    <div v-if="!hasRenderableContent" class="empty">No structured assessment data available.</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface GenericObj { [key: string]: unknown }

const props = defineProps<{ data?: GenericObj | null }>()

const toTitleCase = (s: string | number): string => {
  const str = String(s)
  return str.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}
const isPlainObject = (val: unknown): val is GenericObj => !!val && typeof val === 'object' && !Array.isArray(val)

const safeStringify = (val: unknown): string => {
  try {
    return JSON.stringify(val)
  } catch {
    // Fallback for circular or non-serializable values
    return Object.prototype.toString.call(val)
  }
}

const formatValue = (val: unknown): string => {
  if (val == null) return '—'
  if (Array.isArray(val)) return val.map((v) => (typeof v === 'string' ? v : safeStringify(v))).join(', ')
  if (typeof val === 'object') return safeStringify(val)
  return String(val)
}

// Extract common sections
const participants = computed<Record<string, unknown>[]>(() => {
  const d = props.data || {}
  const keys = ['participants', 'attendees', 'staff', 'doctors', 'nurses']
  for (const k of keys) {
    const v = (d as GenericObj)[k]
    if (Array.isArray(v) && v.length) {
      // Normalize array items into objects with consistent columns
      return v.map((item) => (isPlainObject(item) ? item : { value: item })) as Record<string, unknown>[]
    }
  }
  return []
})
const hasParticipants = computed(() => participants.value.length > 0)
const participantColumns = computed<string[]>(() => {
  const colsSet = new Set<string>()
  participants.value.slice(0, 20).forEach((row) => Object.keys(row).forEach((k) => colsSet.add(k)))
  return Array.from(colsSet)
})

const scores = computed<GenericObj>(() => {
  const d = props.data || {}
  const keys = ['scores', 'score', 'metrics', 'evaluation']
  for (const k of keys) {
    const v = (d as GenericObj)[k]
    if (isPlainObject(v)) return v as GenericObj
    if (typeof v === 'number' || typeof v === 'string') return { [k]: v }
  }
  return {}
})
const hasScores = computed(() => Object.keys(scores.value).length > 0)

const commentsText = computed(() => {
  const d = props.data || {}
  const keys = ['comments', 'notes', 'remarks']
  for (const k of keys) {
    const v = (d as GenericObj)[k]
    if (typeof v === 'string') return v
  }
  return ''
})
const hasComments = computed(() => !!commentsText.value)

// Build other sections from remaining keys
const otherSections = computed(() => {
  const d = { ...(props.data || {}) } as GenericObj
  // Omit already extracted keys
  ;['participants', 'attendees', 'staff', 'doctors', 'nurses', 'scores', 'score', 'metrics', 'evaluation', 'comments', 'notes', 'remarks']
    .forEach((k) => delete d[k])

  const sections: Array<
    | { title: string; type: 'table'; columns: string[]; rows: Record<string, unknown>[] }
    | { title: string; type: 'kv'; kv: GenericObj }
    | { title: string; type: 'list'; items: unknown[] }
    | { title: string; type: 'raw'; raw: unknown }
  > = []

  for (const [key, value] of Object.entries(d)) {
    const title = toTitleCase(key)
    if (Array.isArray(value)) {
      if (value.length && isPlainObject(value[0])) {
        const rows = value as Record<string, unknown>[]
        const colsSet = new Set<string>()
        rows.slice(0, 20).forEach((row) => Object.keys(row).forEach((k) => colsSet.add(k)))
        sections.push({ title, type: 'table', rows, columns: Array.from(colsSet) })
      } else {
        sections.push({ title, type: 'list', items: value })
      }
    } else if (isPlainObject(value)) {
      sections.push({ title, type: 'kv', kv: value as GenericObj })
    } else {
      sections.push({ title, type: 'kv', kv: { [title]: value } })
    }
  }
  return sections
})

const hasRenderableContent = computed(() => hasParticipants.value || hasScores.value || hasComments.value || otherSections.value.length > 0)
</script>

<style scoped>
.assessment-view { display: flex; flex-direction: column; gap: 16px; }
.section { margin-top: 6px; }
.section-title { font-weight: 700; color: #2a4b46; margin-bottom: 6px; }
.comment-box { background: #f7f7f8; padding: 10px 12px; border-radius: 6px; white-space: pre-wrap; }
.bullet-list { margin: 0; padding-left: 20px; }
.cell-key { width: 30%; font-weight: 600; color: #415a55; }
.monospace { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; white-space: pre-wrap; background: #f0f2f3; padding: 8px; border-radius: 6px; }
</style>