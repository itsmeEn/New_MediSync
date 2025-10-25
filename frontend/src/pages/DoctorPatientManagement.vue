<template>
  <q-layout view="hHh Lpr fFf">
    <!-- Standardized Header Component -->
    <DoctorHeader @toggle-drawer="rightDrawerOpen = !rightDrawerOpen" />

    <!-- Standardized Sidebar Component -->
    <DoctorSidebar v-model="rightDrawerOpen" active-route="patients" />

    <q-page-container class="page-container-with-fixed-header safe-area-bottom role-body-bg">
      <!-- Main Content -->
      <div class="patient-management-content">
        <!-- Header Section -->
        <div class="greeting-section">
          <q-card class="greeting-card">
            <q-card-section class="greeting-content">
              <div class="greeting-text">
                <h2 class="greeting-title">Patient Management</h2>
                <p class="greeting-subtitle">Manage your patients and their medical records</p>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Patient Management Cards -->
        <div class="management-cards-grid">
          <!-- Left Column: Patient List -->
          <div class="left-column">
            <q-card class="dashboard-card patient-list-card">
              <q-card-section class="card-header">
                <h5 class="card-title">Patient List</h5>
                <q-btn color="primary" icon="refresh" size="sm" @click="loadPatients" :loading="loading" />
              </q-card-section>

              <q-card-section class="card-content">
                <q-banner dense class="q-mb-sm" icon="info" inline-actions>
                  Select a patient from the list to work on OPD forms. Archived patients are hidden from selection.
                </q-banner>
                <div class="row items-center q-col-gutter-sm q-mb-sm">
                  <div class="col-12 col-sm-8">
                    <q-select
                      v-model="selectedForm"
                      :options="opdFormOptions"
                      outlined
                      dense
                      label="OPD Forms"
                      emit-value
                      map-options
                      :disable="!selectedPatient"
                      aria-label="OPD Forms"
                    />
                  </div>
                  <div class="col-6 col-sm-2">
                    <q-select
                      v-model="sortKey"
                      :options="sortOptions"
                      outlined
                      dense
                      label="Sort by"
                      emit-value
                      map-options
                      aria-label="Sort patients"
                    />
                  </div>
                  <div class="col-6 col-sm-2">
                    <q-select
                      v-model="sortOrder"
                      :options="orderOptions"
                      outlined
                      dense
                      label="Order"
                      emit-value
                      map-options
                      aria-label="Sort order"
                    />
                  </div>
                </div>
              </q-card-section>

              <q-card-section class="card-content">
                <div v-if="loading" class="loading-section">
                  <q-spinner color="primary" size="2em" />
                  <p class="loading-text">Loading patients...</p>
                </div>

                <div v-else-if="patients.length === 0" class="empty-section">
                  <q-icon name="people" size="48px" color="grey-5" />
                  <p class="empty-text">No patients found</p>
                </div>

                <div v-else class="patients-list">
                  <div
                    v-for="patient in filteredPatients"
                    :key="patient.id"
                    :class="['patient-card', { selected: selectedPatient && selectedPatient.id === patient.id }]"
                    :aria-selected="selectedPatient && selectedPatient.id === patient.id ? 'true' : 'false'"
                    @click="selectPatient(patient)"
                  >
                    <div class="patient-avatar">
                      <q-avatar size="50px">
                        <img
                          v-if="patient.profile_picture"
                          :src="patient.profile_picture.startsWith('http') ? patient.profile_picture : `http://localhost:8000${patient.profile_picture}`"
                          :alt="patient.full_name"
                          @error="patient.profile_picture = ''"
                        />
                        <q-icon v-else name="person" size="25px" color="white" />
                      </q-avatar>
                    </div>

                    <div class="patient-info">
                      <h6 class="patient-name">{{ patient.full_name }}</h6>
                      <p class="patient-details">
                        Assigned by: {{ patient.assigned_by || 'N/A' }} | 
                        Specialization: {{ patient.specialization_required || 'General' }}
                      </p>
                      <p class="patient-condition">
                        {{ patient.assignment_reason || 'No reason specified' }}
                      </p>
                      <div class="patient-status">
                        <q-chip 
                          :color="patient.assignment_status === 'pending' ? 'orange' : 
                                  patient.assignment_status === 'accepted' ? 'blue' : 
                                  patient.assignment_status === 'in_progress' ? 'purple' : 
                                  patient.assignment_status === 'completed' ? 'green' : 'grey'" 
                          text-color="white" 
                          size="sm"
                        > 
                          {{ patient.assignment_status || 'pending' }} 
                        </q-chip>
                        <q-chip 
                          v-if="patient.priority && patient.priority !== 'normal'"
                          :color="patient.priority === 'high' ? 'red' : 'orange'" 
                          text-color="white" 
                          size="sm"
                          class="q-ml-xs"
                        > 
                          {{ patient.priority }} priority
                        </q-chip>
                      </div>
                    </div>

                    <div class="patient-actions">
                      <q-btn
                        flat
                        round
                        icon="visibility"
                        color="primary"
                        size="sm"
                        @click.stop="viewPatientDetails(patient)"
                        unelevated
                      >
                        <q-tooltip>View Details</q-tooltip>
                      </q-btn>
                      <q-btn
                        flat
                        round
                        icon="edit"
                        color="secondary"
                        size="sm"
                        @click.stop="editPatient(patient)"
                        unelevated
                      >
                        <q-tooltip>Edit Patient</q-tooltip>
                      </q-btn>
                    </div>
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </div>

          <!-- Right Column: Statistics + Medical Requests -->
          <div class="right-column">
            <!-- Patient Statistics Card -->
            <q-card class="dashboard-card statistics-card">
              <q-card-section class="card-content">
                <div class="card-text">
                  <div class="card-title">Patient Statistics</div>
                  <div class="card-description">Overview of patient activity</div>
                </div>
                <div class="card-icon">
                  <q-icon name="insights" size="2.2rem" />
                </div>
              </q-card-section>

              <q-card-section class="card-content">
                <div class="stats-grid">
                  <div class="stat-item">
                    <div class="stat-number">{{ patients.length }}</div>
                    <div class="stat-label">Total Assignments</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-number">{{ pendingAssignmentsCount }}</div>
                    <div class="stat-label">Pending</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-number">{{ acceptedAssignmentsCount }}</div>
                    <div class="stat-label">Accepted</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-number">{{ completedAssignmentsCount }}</div>
                    <div class="stat-label">Completed</div>
                  </div>
                </div>
              </q-card-section>
            </q-card>

            <!-- Medical Requests Card -->
            <q-card class="dashboard-card medical-requests-card">
              <q-card-section class="card-content">
                <div class="card-text">
                  <div class="card-title">Medical Requests</div>
                  <div class="card-description">Pending approvals and lab requests</div>
                  <div class="card-value">
                    <q-spinner v-if="medicalRequestsLoading" size="md" />
                    <span v-else>{{ medicalRequests.length }}</span>
                  </div>
                </div>
                <div class="card-icon">
                  <q-icon name="assignment" size="2.2rem" />
                </div>
              </q-card-section>

              <q-card-actions align="right" class="q-px-md q-pb-md">
                <q-btn
                  color="primary"
                  icon="refresh"
                  size="sm"
                  @click="loadMedicalRequests"
                  :loading="medicalRequestsLoading"
                  label="Refresh"
                  unelevated
                />
                <q-btn
                  color="secondary"
                  icon="visibility"
                  size="sm"
                  label="View"
                  @click="showMedicalRequestsModal = true"
                  unelevated
                />
              </q-card-actions>
            </q-card>

            <!-- List of Available Nurses Card -->
            <q-card class="dashboard-card nurses-card">
              <q-card-section class="card-content">
                <div class="card-text">
                  <div class="card-title">Available Nurses</div>
                  <div class="card-description">Nurses who can assign patients</div>
                </div>
                <div class="card-icon">
                  <q-icon name="local_hospital" size="2.2rem" />
                </div>
              </q-card-section>
              <q-card-section class="card-content">
                <div v-if="nursesLoading" class="loading-section">
                  <q-spinner color="primary" size="2em" />
                  <p class="loading-text">Loading nurses...</p>
                </div>
                <div v-else-if="availableNurses.length === 0" class="empty-section">
                  <q-icon name="local_hospital" size="48px" color="grey-5" />
                  <p class="empty-text">No available nurses</p>
                </div>
                <div v-else class="nurses-list">
                  <div v-for="(nurse, idx) in availableNurses" :key="String(nurse.id ?? nurse.email ?? nurse.full_name ?? idx)" class="nurse-row">
                    <div class="nurse-avatar">
                      <q-avatar size="40px" color="teal-8" text-color="white">
                        {{ getInitials(nurse.full_name || '') }}
                      </q-avatar>
                    </div>
                    <div class="nurse-info">
                      <div class="nurse-name">{{ nurse.full_name }}</div>
                      <div class="nurse-details">Department: {{ nurse.specialization || '—' }} | Status: {{ nurse.availability ?? nurse.status ?? 'Available' }}</div>
                    </div>
                  </div>
                </div>
              </q-card-section>
            </q-card>

            <!-- Patient Archive Card -->
            <q-card class="dashboard-card archive-card">
              <q-card-section class="card-content">
                <div class="card-text">
                  <div class="card-title">Patient Archive</div>
                  <div class="card-description">Doctor OPD forms and clinical documentation</div>
                </div>
                <div class="card-icon"><q-icon name="folder_open" size="2.2rem" /></div>
              </q-card-section>
              <q-card-section class="card-content">
                <q-list bordered separator class="opd-forms-list">
                  <q-item clickable class="q-py-md">
                    <q-item-section avatar>
                      <q-icon name="description" color="primary" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label>History and Physical (H&P) Form</q-item-label>
                      <q-item-label caption>
                        Chief Complaint, HPI, PMH, SH, ROS, Physical Exam, Assessment, and Plan.
                      </q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-btn color="primary" size="sm" label="Create" @click="openForm('hp')" />
                    </q-item-section>
                  </q-item>

                  <q-item clickable class="q-py-md">
                    <q-item-section avatar>
                      <q-icon name="article" color="secondary" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label>Progress Note (SOAP)</q-item-label>
                      <q-item-label caption>
                        Subjective updates, Objective data, Assessment changes, and treatment Plan updates.
                      </q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-btn color="secondary" size="sm" label="Create" @click="openForm('soap')" />
                    </q-item-section>
                  </q-item>

                  <q-item clickable class="q-py-md">
                    <q-item-section avatar>
                      <q-icon name="assignment" color="teal" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label>Provider Order Sheet</q-item-label>
                      <q-item-label caption>
                        Medication orders, diagnostic requests, therapy orders, and consultations.
                      </q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-btn color="teal" size="sm" label="Create" @click="openForm('orders')" />
                    </q-item-section>
                  </q-item>

                  <q-item clickable class="q-py-md">
                    <q-item-section avatar>
                      <q-icon name="medical_services" color="deep-orange" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label>Operative/Procedure Report</q-item-label>
                      <q-item-label caption>
                        Procedure name, indications, anesthesia, steps, findings, complications, and post-procedure plan.
                      </q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-btn color="deep-orange" size="sm" label="Create" @click="openForm('procedure')" />
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </div>
    </q-page-container>

    <!-- Doctor OPD Forms Modal -->
    <q-dialog
      v-model="showFormDialog"
      transition-show="scale"
      transition-hide="scale"
      :persistent="false"
      content-class="form-dialog-container"
    >
      <q-card class="form-dialog-card" style="min-width:700px;max-width:95vw;">
        <q-card-section class="card-header">
          <div class="row items-center justify-between">
            <div class="text-h6">{{ currentFormTitle }}</div>
            <q-btn flat round dense icon="close" aria-label="Close OPD Form modal" @click="showFormDialog = false" />
          </div>
        </q-card-section>
        <q-separator />
        <q-card-section class="card-content">
          <q-banner dense class="q-mb-md" icon="assignment">
            {{ currentFormTitle }} for {{ selectedPatient?.full_name || 'Selected Patient' }}
          </q-banner>

          <div v-if="selectedPatient" class="q-gutter-md q-mb-md">
            <div class="text-subtitle1 text-bold">Patient Demographics</div>
            <div class="row q-col-gutter-md">
              <div class="col-12 col-sm-6 col-md-3"><q-input :model-value="String(selectedPatient.id)" label="Patient ID" outlined dense readonly/></div>
              <div class="col-12 col-sm-6 col-md-3"><q-input :model-value="selectedPatient.full_name" label="Name" outlined dense readonly/></div>
              <div class="col-12 col-sm-6 col-md-3"><q-input :model-value="selectedPatient.gender || ''" label="Sex/Gender" outlined dense readonly/></div>
              <div class="col-12 col-sm-6 col-md-3"><q-input :model-value="String(selectedPatient.age || '')" label="Age" outlined dense readonly/></div>
            </div>
          </div>

          <div v-if="selectedPatient && currentFormType === 'hp'" class="q-gutter-md">
            <div class="text-subtitle1 text-bold">History and Physical (H&P)</div>
            <div class="row q-col-gutter-md">
              <div class="col-12 col-sm-6"><q-input v-model="hpForm.cc" label="Chief Complaint (CC)" outlined dense/></div>
              <div class="col-12"><q-input v-model="hpForm.hpi" type="textarea" label="History of Present Illness (HPI)" outlined dense/></div>
              <div class="col-12 col-sm-6"><q-input v-model="hpForm.pmh" type="textarea" label="Past Medical History (PMH)" outlined dense/></div>
              <div class="col-12 col-sm-6"><q-input v-model="hpForm.sh" type="textarea" label="Social History (SH)" outlined dense/></div>
              <div class="col-12"><q-input v-model="hpForm.ros" type="textarea" label="Review of Systems (ROS)" outlined dense/></div>
              <div class="col-12"><q-input v-model="hpForm.pe" type="textarea" label="Physical Examination" outlined dense/></div>
              <div class="col-12 col-sm-6"><q-input v-model="hpForm.assessment" type="textarea" label="Assessment (Diagnoses)" outlined dense/></div>
              <div class="col-12 col-sm-6"><q-input v-model="hpForm.plan" type="textarea" label="Plan (Treatment, Medications, Tests)" outlined dense/></div>
            </div>
          </div>

          <div v-if="selectedPatient && currentFormType === 'soap'" class="q-gutter-md">
            <div class="text-subtitle1 text-bold">Progress Note (SOAP)</div>
            <div class="row q-col-gutter-md">
              <div class="col-12"><q-input v-model="soapForm.subjective" type="textarea" label="Subjective" outlined dense/></div>
              <div class="col-12"><q-input v-model="soapForm.objective" type="textarea" label="Objective" outlined dense/></div>
              <div class="col-12"><q-input v-model="soapForm.assessment" type="textarea" label="Assessment" outlined dense/></div>
              <div class="col-12"><q-input v-model="soapForm.plan" type="textarea" label="Plan" outlined dense/></div>
            </div>
          </div>

          <div v-if="selectedPatient && currentFormType === 'orders'" class="q-gutter-md">
            <div class="text-subtitle1 text-bold">Provider Order Sheet</div>
            <div class="row q-col-gutter-md">
              <div class="col-12"><q-input v-model="ordersForm.meds" type="textarea" label="Medication Orders (drug, dose, route, frequency)" outlined dense/></div>
              <div class="col-12"><q-input v-model="ordersForm.diagnostics" type="textarea" label="Diagnostic Orders (labs, imaging, procedure)" outlined dense/></div>
              <div class="col-12"><q-input v-model="ordersForm.therapy" type="textarea" label="Therapy Orders (PT/OT, wound care, etc.)" outlined dense/></div>
              <div class="col-12"><q-input v-model="ordersForm.consults" type="textarea" label="Consultation Requests" outlined dense/></div>
            </div>
          </div>

          <div v-if="selectedPatient && currentFormType === 'procedure'" class="q-gutter-md">
            <div class="text-subtitle1 text-bold">Operative/Procedure Report</div>
            <div class="row q-col-gutter-md">
              <div class="col-12 col-sm-6"><q-input v-model="procedureForm.name" label="Procedure Name" outlined dense/></div>
              <div class="col-12 col-sm-6"><q-input v-model="procedureForm.indications" label="Indications" outlined dense/></div>
              <div class="col-12 col-sm-6"><q-input v-model="procedureForm.anesthesia" label="Anesthesia" outlined dense/></div>
              <div class="col-12"><q-input v-model="procedureForm.steps" type="textarea" label="Procedure Steps" outlined dense/></div>
              <div class="col-12"><q-input v-model="procedureForm.findings" type="textarea" label="Findings" outlined dense/></div>
              <div class="col-12"><q-input v-model="procedureForm.complications" type="textarea" label="Complications" outlined dense/></div>
              <div class="col-12 col-sm-6"><q-input v-model="procedureForm.status" type="textarea" label="Post-Procedure Status" outlined dense/></div>
              <div class="col-12 col-sm-6"><q-input v-model="procedureForm.immediatePlan" type="textarea" label="Immediate Plan" outlined dense/></div>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- Notifications Modal -->
    <q-dialog v-model="showNotifications" persistent>
      <q-card style="width: 400px; max-width: 90vw">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Notifications</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-card-section>
          <div v-if="notifications.length === 0" class="text-center text-grey-6 q-py-lg">
            No notifications yet
          </div>
          <div v-else>
            <q-list>
              <q-item
                v-for="notification in notifications"
                :key="notification.id"
                clickable
                @click="handleNotificationClick(notification)"
                :class="{ unread: !notification.is_read }"
              >
                <q-item-section avatar>
                  <q-icon name="info" color="primary" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ notification.message }}</q-item-label>
                  <q-item-label caption class="text-grey-5">{{
                    formatTime(notification.created_at)
                  }}</q-item-label>
                </q-item-section>
                <q-item-section side v-if="!notification.is_read">
                  <q-badge color="red" rounded />
                </q-item-section>
              </q-item>
            </q-list>
          </div>
        </q-card-section>
        <q-card-actions align="right" v-if="notifications.length > 0">
          <q-btn flat label="Mark All Read" @click="markAllNotificationsRead" />
          <q-btn flat label="Close" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Medical Requests Modal -->
    <q-dialog v-model="showMedicalRequestsModal" persistent>
      <q-card class="modal-card" style="width: 520px; max-width: 95vw">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Medical Requests</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-card-section>
          <div v-if="medicalRequests.length === 0" class="text-center text-grey-6 q-py-lg">
            No medical requests found
          </div>
          <div v-else>
            <q-list separator>
              <q-item v-for="req in medicalRequests" :key="req.id" class="q-pa-md">
                <q-item-section>
                  <q-item-label>{{ req.title || 'Request' }}</q-item-label>
                  <q-item-label caption>
                    {{ req.status || 'pending' }} • {{ formatDateTime(req.created_at) }}
                  </q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn color="primary" icon="refresh" size="sm" label="Refresh" @click="loadMedicalRequests" :loading="medicalRequestsLoading" />
          <q-btn flat label="Close" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import { useQuasar } from 'quasar';
import { api } from 'boot/axios';
import DoctorHeader from '../components/DoctorHeader.vue';
import DoctorSidebar from '../components/DoctorSidebar.vue';

// Types
interface Patient {
  id: number;
  user_id: number;
  full_name: string;
  patient_name?: string;
  email?: string;
  age?: number | null;
  gender?: string;
  blood_type?: string;
  medical_condition?: string;
  hospital?: string;
  insurance_provider?: string;
  billing_amount?: number | null;
  room_number?: string;
  admission_type?: string;
  date_of_admission?: string;
  discharge_date?: string | null;
  medication?: string;
  test_results?: string;
  assigned_doctor?: string | null;
  profile_picture?: string | null;
  is_dummy?: boolean;
  // Assignment-related fields
  assignment_id?: number;
  assignment_status?: string;
  assigned_by?: string;
  assigned_at?: string;
  specialization_required?: string;
  assignment_reason?: string;
  priority?: string;
  accepted_at?: string | null;
  completed_at?: string | null;
}

type DoctorNotification = {
  id: number;
  message: string;
  is_read: boolean;
  created_at: string;
};

type MedicalRequest = {
  id: number;
  title?: string;
  status?: string;
  created_at?: string | Date;
};

// Reactive data
const $q = useQuasar();
const rightDrawerOpen = ref(false);
const loading = ref(false);
const searchText = ref('');
const patients = ref<Patient[]>([]);
const selectedPatient = ref<Patient | null>(null);
const showNotifications = ref(false);

// Form state and handler for OPD forms
const showFormDialog = ref(false);
const currentFormType = ref<'hp' | 'soap' | 'orders' | 'procedure' | null>(null);
const openForm = (type: 'hp' | 'soap' | 'orders' | 'procedure'): void => {
  if (!selectedPatient.value) {
    $q.notify({ type: 'warning', message: 'Select a patient first', position: 'top' });
    return;
  }
  currentFormType.value = type;
  showFormDialog.value = true;
};

const currentFormTitle = computed(() => {
  switch (currentFormType.value) {
    case 'hp': return 'History and Physical (H&P)';
    case 'soap': return 'Progress Note (SOAP)';
    case 'orders': return 'Provider Order Sheet';
    case 'procedure': return 'Operative/Procedure Report';
    default: return 'OPD Form';
  }
});

// OPD form local state to satisfy QInput v-model requirements
// These refs hold in-progress form values per OPD type.
const hpForm = ref({
  cc: '', hpi: '', pmh: '', sh: '', ros: '', pe: '', assessment: '', plan: ''
});
const soapForm = ref({
  subjective: '', objective: '', assessment: '', plan: ''
});
const ordersForm = ref({
  meds: '', diagnostics: '', therapy: '', consults: ''
});
const procedureForm = ref({
  name: '', indications: '', anesthesia: '', steps: '', findings: '', complications: '', status: '', immediatePlan: ''
});

// OPD form selection and sorting state (mirrors nurse design)
const selectedForm = ref<'hp' | 'soap' | 'orders' | 'procedure' | ''>('');
const opdFormOptions = [
  { label: 'Select Form Type', value: '' },
  { label: 'History and Physical (H&P)', value: 'hp' },
  { label: 'Progress Note (SOAP)', value: 'soap' },
  { label: 'Provider Order Sheet', value: 'orders' },
  { label: 'Operative/Procedure Report', value: 'procedure' },
];

const sortKey = ref<'full_name' | 'age' | 'gender'>('full_name');
const sortOrder = ref<'asc' | 'desc'>('asc');
const sortOptions = [
  { label: 'Name', value: 'full_name' },
  { label: 'Age', value: 'age' },
  { label: 'Gender', value: 'gender' },
];
const orderOptions = [
  { label: 'Ascending', value: 'asc' },
  { label: 'Descending', value: 'desc' },
];

watch(selectedForm, (val) => {
  if (val && selectedPatient.value) {
    currentFormType.value = val;
    showFormDialog.value = true;
  }
});

// User profile data
const userProfile = ref<{
  id: number;
  full_name: string;
  specialization?: string;
  role: string;
  profile_picture: string | null;
  verification_status: string;
}>({
  id: 0,
  full_name: '',
  specialization: '',
  role: '',
  profile_picture: null,
  verification_status: '',
});

// Weather data is now handled by DoctorHeader component

// Notification system
const notifications = ref<DoctorNotification[]>([]);

const loadNotifications = async (): Promise<void> => {
  try {
    console.log('📬 Loading doctor notifications...');
    const response = await api.get('/operations/notifications/');
    notifications.value = response.data || [];
    console.log('✅ Doctor notifications loaded:', notifications.value.length);
  } catch (error) {
    console.error('❌ Error loading doctor notifications:', error);
    $q.notify({ type: 'negative', message: 'Failed to load notifications' });
  }
};

// Medical Requests state
const medicalRequests = ref<MedicalRequest[]>([]);
const medicalRequestsLoading = ref(false);
const showMedicalRequestsModal = ref(false);

const loadMedicalRequests = async () => {
  medicalRequestsLoading.value = true;
  try {
    const response = await api.get('/operations/medical-requests/').catch(() => ({ data: [] }));
    medicalRequests.value = (response?.data || []) as MedicalRequest[];
  } catch (error) {
    console.error('Failed to load medical requests:', error);
    medicalRequests.value = [];
    $q.notify({ type: 'negative', message: 'Failed to load medical requests' });
    void api.post('/operations/client-log/', {
      level: 'error',
      message: 'loadMedicalRequests failed',
      route: 'DoctorPatientManagement',
      context: { error: String(error) },
    });
  } finally {
    medicalRequestsLoading.value = false;
  }
};

// Available Nurses list
interface NurseSummary {
  id: number | string;
  full_name: string;
  specialization?: string;
  department?: string;
  status?: string;
  availability?: string;
  email?: string | undefined;
  profile_picture?: string | null;
}

interface AvailableUser {
  id: number | string;
  full_name: string;
  role: string;
  verification_status: string;
  email?: string;
  profile_picture?: string | null;
  nurse_profile?: { department?: string } | null;
  specialization?: string;
}
 
 const availableNurses = ref<NurseSummary[]>([]);
const nursesLoading = ref(false);

const getInitials = (name: string): string => {
  const parts = (name || '').trim().split(/\s+/);
  return parts.slice(0, 2).map(p => (p[0] || '').toUpperCase()).join('');
};

const loadAvailableNurses = async (): Promise<void> => {
  nursesLoading.value = true;
  try {
    const response = await api.get('/operations/messaging/available-users/');
    const users: AvailableUser[] = (response.data?.users ?? response.data ?? []) as AvailableUser[];
    const list: NurseSummary[] = users
      .filter((u) => u.role === 'nurse' && u.verification_status === 'approved')
      .map((u) => ({
        id: u.id,
        full_name: u.full_name,
        department: u.nurse_profile?.department || u.specialization || 'General',
        status: 'Verified',
        availability: 'Available',
        email: u.email ?? '',
        profile_picture: u.profile_picture || null,
      } as NurseSummary));
    availableNurses.value = list;
  } catch (error) {
    console.error('Failed to load available nurses:', error);
    availableNurses.value = [];
  } finally {
    nursesLoading.value = false;
  }
};

// Patients filtering and statistics
const filteredPatients = computed(() => {
  let list = patients.value;
  if (searchText.value) {
    const search = searchText.value.toLowerCase();
    list = list.filter(
      (patient) =>
        patient.full_name.toLowerCase().includes(search) ||
        (patient.medical_condition || '').toLowerCase().includes(search) ||
        (patient.hospital || '').toLowerCase().includes(search),
    );
  }
  const key = sortKey.value;
  const dir = sortOrder.value === 'desc' ? -1 : 1;
  const toComparable = (p: Patient) => {
    if (key === 'age') return p.age ?? 0;
    const raw = p[key as keyof Patient];
    if (typeof raw === 'string') return raw.toLowerCase();
    if (typeof raw === 'number') return String(raw).toLowerCase();
    return '';
  };
  return [...list].sort((a: Patient, b: Patient) => {
    const av = toComparable(a);
    const bv = toComparable(b);
    if (av < bv) return -1 * dir;
    if (av > bv) return 1 * dir;
    return 0;
  });
});



// Assignment-based statistics
const pendingAssignmentsCount = computed(
  () => patients.value.filter((p) => p.assignment_status === 'pending').length,
);

const acceptedAssignmentsCount = computed(
  () => patients.value.filter((p) => p.assignment_status === 'accepted' || p.assignment_status === 'in_progress').length,
);

const completedAssignmentsCount = computed(
  () => patients.value.filter((p) => p.assignment_status === 'completed').length,
);

// Patient assignment data loading and actions
const loadPatients = async () => {
  loading.value = true;
  try {
    // Load only assigned patients from the assignment API
    const response = await api.get('/operations/doctor/assignments/');
    if (response.data && Array.isArray(response.data)) {
      // Transform assignment data to patient format
      patients.value = response.data.map((assignment: {
        id: number;
        patient_id: number;
        patient_name: string;
        status: string;
        assigned_by_name: string;
        assigned_at: string;
        specialization_required: string;
        assignment_reason: string;
        priority: string;
        accepted_at: string | null;
        completed_at: string | null;
      }) => ({
        id: assignment.patient_id,
        user_id: assignment.patient_id,
        full_name: assignment.patient_name,
        patient_name: assignment.patient_name,
        assignment_id: assignment.id,
        assignment_status: assignment.status,
        assigned_by: assignment.assigned_by_name,
        assigned_at: assignment.assigned_at,
        specialization_required: assignment.specialization_required,
        assignment_reason: assignment.assignment_reason,
        priority: assignment.priority,
        accepted_at: assignment.accepted_at,
        completed_at: assignment.completed_at,
        // Default patient fields for compatibility
        medical_condition: '',
        blood_type: '',
        hospital: '',
        room_number: '',
        discharge_date: null,
        is_dummy: false
      }));
      console.log('Assigned patients loaded:', patients.value.length, 'User role:', userProfile.value.role);
      const first = patients.value[0];
      if (first) { void loadVerificationStatus(first); }
    } else {
      patients.value = [];
      console.log('No patient assignments found');
    }
  } catch (error) {
    console.error('Failed to load patient assignments:', error);
    $q.notify({ type: 'negative', message: 'Failed to load patient assignments', position: 'top' });
    patients.value = [];
    void api.post('/operations/client-log/', {
      level: 'error',
      message: 'loadPatients failed',
      route: 'DoctorPatientManagement',
      context: { error: String(error) },
    });
  } finally {
    loading.value = false;
  }
};

const selectPatient = (patient: Patient) => {
  selectedPatient.value = patient;
  if (selectedPatient.value) {
    console.log('Selected patient id:', selectedPatient.value.id);
    void loadVerificationStatus(patient);
  }
};

// Verification status for selected patient
interface VerificationStatus {
  input: {
    patient_user_id: number;
    patient_profile_id: number;
    doctor_user_id: number;
    doctor_profile_id: number;
  };
  persistence: {
    assignments_count: number;
    appointments_count: number;
    archives_count: number;
  };
  transmission: {
    recent_notification_present: boolean;
    recent_notification_message: string | null;
    recent_notification_at: string | null;
  };
  mapping: {
    assignment_statuses: string[];
    appointment_statuses: string[];
  };
}
const verificationStatus = ref<VerificationStatus | null>(null);

const loadVerificationStatus = async (patient: Patient) => {
  try {
    const pid = Number(patient.user_id ?? patient.id);
    const did = userProfile.value.id;
    const resp = await api.get(`/operations/verification-status/?patient_id=${pid}&doctor_id=${did}`);
    verificationStatus.value = resp.data as VerificationStatus;
    $q.notify({
      type: 'positive',
      message: `Data availability: assignments ${resp.data?.persistence?.assignments_count ?? 0}, archives ${resp.data?.persistence?.archives_count ?? 0}`,
      position: 'top',
      timeout: 2500,
    });
    void api.post('/operations/client-log/', {
      level: 'info',
      message: 'doctor verification fetched',
      route: 'DoctorPatientManagement',
      context: {
        patient_id: pid,
        doctor_id: did,
        counts: resp.data?.persistence ?? {},
      },
    });
  } catch (error) {
    console.error('Verification status error:', error);
    $q.notify({ type: 'warning', message: 'Failed to verify data availability', position: 'top' });
    void api.post('/operations/client-log/', {
      level: 'error',
      message: 'doctor verification failed',
      route: 'DoctorPatientManagement',
      context: {
        patient_id: patient.user_id ?? patient.id,
        doctor_id: userProfile.value.id,
        error: String(error),
      },
    });
  }
};

const viewPatientDetails = (patient: Patient) => {
  const currentId = selectedPatient.value?.id;
  console.log('Viewing patient:', patient.full_name, 'Currently selected:', currentId);
  $q.notify({ type: 'info', message: `Viewing details for ${patient.full_name}`, position: 'top' });
};

const editPatient = (patient: Patient) => {
  const currentId = selectedPatient.value?.id;
  console.log('Editing patient:', patient.full_name, 'Currently selected:', currentId);
  $q.notify({ type: 'info', message: `Editing ${patient.full_name}`, position: 'top' });
};

const fetchUserProfile = async () => {
  try {
    const response = await api.get('/users/profile/');
    const userData = response.data.user;
    userProfile.value = {
      id: userData.id,
      full_name: userData.full_name,
      specialization: userData.doctor_profile?.specialization,
      role: userData.role,
      profile_picture: userData.profile_picture || null,
      verification_status: userData.verification_status,
    };
    console.log('Loaded user profile role:', userProfile.value.role);
  } catch (error) {
    console.error('Failed to fetch user profile:', error);
  }
};

// Fix DateTime optional input
const formatDateTime = (dateStr?: string | number | Date) => {
  if (!dateStr) return '-';
  const d = new Date(dateStr);
  return d.toLocaleString('en-US', {
    year: 'numeric', month: 'short', day: '2-digit',
    hour: 'numeric', minute: '2-digit', hour12: true,
  });
};

// Notifications handlers
const handleNotificationClick = (notification: DoctorNotification): void => {
  notification.is_read = true;
  void markNotificationAsRead(notification.id);
};

const markNotificationAsRead = async (notificationId: number): Promise<void> => {
  try {
    await api.patch(`/operations/notifications/${notificationId}/mark-read/`);
  } catch (error) {
    console.error('Error marking notification as read:', error);
  }
};

const markAllNotificationsRead = async (): Promise<void> => {
  try {
    // Mark all notifications as read locally
    notifications.value.forEach((notification) => {
      notification.is_read = true;
    });

    // Mark all notifications as read on backend
    await api.post('/operations/notifications/mark-all-read/');

    $q.notify({
      type: 'positive',
      message: 'All notifications marked as read',
    });
  } catch (error) {
    console.error('Error marking notifications as read:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to mark notifications as read',
    });
  }
};

const formatTime = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });
};




























let assignmentsTicker: ReturnType<typeof setInterval> | null = null;

const startAssignmentsPolling = (): void => {
  if (assignmentsTicker) return;
  assignmentsTicker = setInterval(() => { void loadPatients(); }, 8000);
};

const stopAssignmentsPolling = (): void => {
  if (assignmentsTicker) {
    clearInterval(assignmentsTicker);
    assignmentsTicker = null;
  }
};

// Doctor messaging WebSocket for real-time patient assignments
let doctorMessagingWS: WebSocket | null = null;

const setupDoctorMessagingWS = (): void => {
  try {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const base = new URL(api.defaults.baseURL || `http://${window.location.hostname}:8000/api`);
    const backendHost = base.hostname;
    const backendPort = base.port || (base.protocol === 'https:' ? '443' : '80');
    const storedUser = JSON.parse(localStorage.getItem('user') || '{}');
    const userId = storedUser.id || storedUser.user?.id || storedUser.user_id;

    if (!userId) {
      console.warn('No user id found for doctor messaging WebSocket');
      return;
    }

    const wsUrl = `${protocol}//${backendHost}:${backendPort}/ws/messaging/${userId}/`;
    const ws = new WebSocket(wsUrl);
    doctorMessagingWS = ws;

    ws.onopen = () => {
      console.log('DoctorPatientManagement messaging WebSocket connected');
    };

    ws.onmessage = async (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data as string);
        if (data.type === 'notification') {
          const notif = data.notification || {};
          if (notif.event === 'patient_assigned') {
            $q.notify({
              type: 'info',
              message: 'New patient assigned to you',
              position: 'top'
            });
            // Immediate refresh of assignments, notifications, and requests
            try {
              await loadPatients();
            } catch (e) {
              console.warn('Failed to refresh patients after assignment', e);
              $q.notify({ type: 'negative', message: 'Failed to refresh patients. Retrying...', position: 'top' });
              // Quick retry once
              setTimeout(() => { void loadPatients(); }, 2000);
            }
            void loadNotifications();
            void loadMedicalRequests();
          }
        }
      } catch (err) {
        console.warn('Failed to parse doctor WS message', err);
      }
    };

    ws.onclose = () => {
      console.log('DoctorPatientManagement messaging WebSocket disconnected');
      // Attempt to reconnect after 5 seconds
      setTimeout(() => setupDoctorMessagingWS(), 5000);
    };
  } catch (e) {
    console.warn('Failed to setup doctor messaging WebSocket', e);
  }
};

onMounted(() => {
  console.log('🚀 DoctorPatientManagement component mounted');
  void fetchUserProfile();
  void loadNotifications();
  void loadPatients();
  void loadMedicalRequests();
  void loadAvailableNurses();
  startAssignmentsPolling();
  setupDoctorMessagingWS();
});

onUnmounted(() => {
  stopAssignmentsPolling();
  try { if (doctorMessagingWS) doctorMessagingWS.close(); } catch (err) { console.warn('Error closing doctor WS', err); } finally { doctorMessagingWS = null; }
});








</script>

<style scoped>
/* Import the same styles as DoctorDashboard */
/* Safe Area Support */
.safe-area-top {
  padding-top: env(safe-area-inset-top);
}

.safe-area-bottom {
  padding-bottom: env(safe-area-inset-bottom);
}

/* Mobile Header Layout */
.mobile-header-layout {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.header-top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  min-height: 48px;
}

.header-bottom-row {
  padding: 0 16px 8px;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  justify-content: center;
}

/* Prototype Header Styles */
.prototype-header {
  background: #286660;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-toolbar {
  padding: 0 24px;
  min-height: 64px;
}

.menu-toggle-btn {
  color: white;
  margin-right: 16px;
}

.header-left {
  flex: 1;
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 24px;
}

.search-container {
  width: 100%;
  max-width: 500px;
}

.search-input {
  background: white;
  border-radius: 8px;
}

.notification-btn {
  color: white;
}

.time-display,
.weather-display,
.weather-loading,
.weather-error {
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
}

.time-text,
.weather-text,
.weather-location {
  font-size: 14px;
  font-weight: 500;
}

/* Drawer Styles */
.drawer-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.user-profile-section {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  margin-bottom: 20px;
  position: relative;
}

.user-avatar-container {
  position: relative;
}

.user-avatar {
  border: 3px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.verified-badge {
  position: absolute;
  bottom: 0;
  right: 0;
  background: white;
  border-radius: 50%;
}

.user-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 4px 0;
}

.user-role {
  font-size: 14px;
  color: #666;
  margin: 0 0 12px 0;
}

.navigation-menu {
  flex: 1;
  padding: 16px 0;
}

.nav-item {
  margin: 4px 16px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.nav-item.active {
  background: #286660;
  color: white;
}

.nav-item.active .q-icon {
  color: white;
}

.nav-item:hover:not(.active) {
  background: #f5f5f5;
}

/* Sidebar Content */
.sidebar-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f8f9fa;
  position: relative;
  padding-bottom: 80px; /* Space for footer */
}

/* Logo Section */
.logo-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #e0e0e0;
}

.logo-container {
  display: flex;
  align-items: center;
  flex: 1;
}

.logo-avatar {
  margin-right: 12px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: #286660;
}

.menu-btn-right {
  color: #666;
  margin-left: auto;
}

/* Centered User Profile Section */
.sidebar-user-profile {
  padding: 24px 20px;
  border-bottom: 1px solid #e0e0e0;
  text-align: center;
}

/* Logout Section */
.logout-section {
  padding: 20px;
  border-top: 1px solid #e0e0e0;
}

.logout-btn {
  width: 100%;
  border-radius: 8px;
  font-weight: 600;
  text-transform: uppercase;
}

/* Page Container */
.page-container-with-fixed-header {
  background: #f8f9fa;
  background-size: cover;
  min-height: 100vh;
  position: relative;
}

.page-container-with-fixed-header::before {
  content: '';
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  z-index: 0;
}

.patient-management-content {
  position: relative;
  z-index: 1;
  padding: 20px;
}

/* Greeting Section */
.greeting-section {
  padding: 32px 24px 24px 24px;
  background: transparent;
}

.greeting-card {
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.95) 0%,
    rgba(248, 250, 252, 0.9) 50%,
    rgba(241, 245, 249, 0.85) 100%
  );
  backdrop-filter: blur(18px) saturate(120%);
  -webkit-backdrop-filter: blur(18px) saturate(120%);
  border-radius: 20px;
  border: 1px solid rgba(40, 102, 96, 0.1);
  box-shadow:
    0 10px 25px rgba(40, 102, 96, 0.08),
    0 4px 10px rgba(0, 0, 0, 0.03),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  position: relative;
  width: 100%;
  min-height: 160px;
}

.greeting-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #286660, #6ca299, #b8d2ce);
  border-radius: 20px 20px 0 0;
}

.greeting-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 30px;
}

.greeting-text {
  flex: 1;
}

.greeting-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #333;
  margin: 0 0 10px 0;
  background: linear-gradient(135deg, #286660, #4a7c59);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.greeting-subtitle {
  font-size: 1.1rem;
  color: #666;
  margin: 0;
  font-weight: 500;
}

.greeting-icon {
  color: #286660;
  opacity: 0.8;
}

/* Management Cards */
.management-cards-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 30px;
  margin-bottom: 30px;
}

.glassmorphism-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 20px 0 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.card-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.card-content {
  padding: 20px;
}

.search-input {
  width: 240px;
}

/* Patient List */
.patients-list {
  max-height: 500px;
  overflow-y: auto;
}

.patient-card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.patient-card:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.patient-avatar {
  flex-shrink: 0;
}

.patient-info {
  flex: 1;
  min-width: 0;
}

.patient-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 5px 0;
}

.patient-details {
  font-size: 12px;
  color: #666;
  margin: 0 0 5px 0;
}

.patient-condition {
  font-size: 13px;
  color: #555;
  margin: 0 0 8px 0;
  font-style: italic;
}

.patient-status {
  margin-top: 5px;
}

.patient-actions {
  display: flex;
  gap: 5px;
  flex-shrink: 0;
}

/* Statistics */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.stat-item {
  text-align: center;
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: #286660;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

/* Loading & Empty */
.loading-section, .empty-section { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 40px; color: #666; }
.loading-text, .empty-text { margin-top: 15px; font-size: 14px; }

/* Responsive */
@media (max-width: 1024px) {
  .management-cards-grid { grid-template-columns: 1fr; }
  .search-input { width: 180px; }
}
</style>

<style scoped>
/* Import the same styles as DoctorDashboard */
/* Safe Area Support */
.safe-area-top {
  padding-top: env(safe-area-inset-top);
}

.safe-area-bottom {
  padding-bottom: env(safe-area-inset-bottom);
}

/* Mobile Header Layout */
.mobile-header-layout {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.header-top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  min-height: 48px;
}

.header-bottom-row {
  padding: 0 16px 8px;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  justify-content: center;
}

/* Prototype Header Styles */
.prototype-header {
  background: #286660;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-toolbar {
  padding: 0 24px;
  min-height: 64px;
}

.menu-toggle-btn {
  color: white;
  margin-right: 16px;
}

.header-left {
  flex: 1;
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 24px;
}

.search-container {
  width: 100%;
  max-width: 500px;
}

.search-input {
  background: white;
  border-radius: 8px;
}

.notification-btn {
  color: white;
}

.time-display,
.weather-display,
.weather-loading,
.weather-error {
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
}

.time-text,
.weather-text,
.weather-location {
  font-size: 14px;
  font-weight: 500;
}

/* Drawer Styles */
.drawer-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.user-profile-section {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  margin-bottom: 20px;
  position: relative;
}

.user-avatar-container {
  position: relative;
}

.user-avatar {
  border: 3px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.verified-badge {
  position: absolute;
  bottom: 0;
  right: 0;
  background: white;
  border-radius: 50%;
}

.user-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 4px 0;
}

.user-role {
  font-size: 14px;
  color: #666;
  margin: 0 0 12px 0;
}

.navigation-menu {
  flex: 1;
  padding: 16px 0;
}

.nav-item {
  margin: 4px 16px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.nav-item.active {
  background: #286660;
  color: white;
}

.nav-item.active .q-icon {
  color: white;
}

.nav-item:hover:not(.active) {
  background: #f5f5f5;
}

/* Sidebar Content */
.sidebar-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f8f9fa;
  position: relative;
  padding-bottom: 80px; /* Space for footer */
}

/* Logo Section */
.logo-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #e0e0e0;
}

.logo-container {
  display: flex;
  align-items: center;
  flex: 1;
}

.logo-avatar {
  margin-right: 12px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: #286660;
}

.menu-btn-right {
  color: #666;
  margin-left: auto;
}

/* Centered User Profile Section */
.sidebar-user-profile {
  padding: 24px 20px;
  border-bottom: 1px solid #e0e0e0;
  text-align: center;
}

/* Logout Section */
.logout-section {
  padding: 20px;
  border-top: 1px solid #e0e0e0;
}

.logout-btn {
  width: 100%;
  border-radius: 8px;
  font-weight: 600;
  text-transform: uppercase;
}

/* Page Container */
.page-container-with-fixed-header {
  background: #f8f9fa;
  background-size: cover;
  min-height: 100vh;
  position: relative;
}

.page-container-with-fixed-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  z-index: 0;
}

.patient-management-content {
  position: relative;
  z-index: 1;
  padding: 20px;
}

/* Greeting Section */
.greeting-section {
  padding: 32px 24px 24px 24px;
  background: transparent;
}

.greeting-card {
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.95) 0%,
    rgba(248, 250, 252, 0.9) 50%,
    rgba(241, 245, 249, 0.85) 100%
  );
  backdrop-filter: blur(18px) saturate(120%);
  -webkit-backdrop-filter: blur(18px) saturate(120%);
  border-radius: 20px;
  border: 1px solid rgba(40, 102, 96, 0.1);
  box-shadow:
    0 10px 25px rgba(40, 102, 96, 0.08),
    0 4px 10px rgba(0, 0, 0, 0.03),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  position: relative;
  width: 100%;
  min-height: 160px;
}

.greeting-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #286660, #6ca299, #b8d2ce);
  border-radius: 20px 20px 0 0;
}

.greeting-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 30px;
}

.greeting-text {
  flex: 1;
}

.greeting-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #333;
  margin: 0 0 10px 0;
  background: linear-gradient(135deg, #286660, #4a7c59);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.greeting-subtitle {
  font-size: 1.1rem;
  color: #666;
  margin: 0;
  font-weight: 500;
}

.greeting-icon {
  color: #286660;
  opacity: 0.8;
}

/* Management Cards */
.management-cards-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 30px;
  margin-bottom: 30px;
}

.glassmorphism-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 20px 0 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.card-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.card-content {
  padding: 20px;
}

.search-input {
  width: 240px;
}

/* Patient List */
.patients-list {
  max-height: 500px;
  overflow-y: auto;
}

.patient-card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.patient-card:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.patient-avatar {
  flex-shrink: 0;
}

.patient-info {
  flex: 1;
  min-width: 0;
}

.patient-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 5px 0;
}

.patient-details {
  font-size: 12px;
  color: #666;
  margin: 0 0 5px 0;
}

.patient-condition {
  font-size: 13px;
  color: #555;
  margin: 0 0 8px 0;
  font-style: italic;
}

.patient-status {
  margin-top: 5px;
}

.patient-actions {
  display: flex;
  gap: 5px;
  flex-shrink: 0;
}

/* Statistics */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.stat-item {
  text-align: center;
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: #286660;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

/* Loading & Empty */
.loading-section,
.empty-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #666;
}

.loading-text,
.empty-text {
  margin-top: 15px;
  font-size: 14px;
}

/* Time and Weather Display Styles */
.time-display {
  display: flex;
  align-items: center;
  gap: 4px;
  color: white;
  font-size: 12px;
}

.weather-display {
  display: flex;
  align-items: center;
  gap: 4px;
  color: white;
  font-size: 12px;
}

.weather-loading,
.weather-error {
  display: flex;
  align-items: center;
  gap: 4px;
  color: white;
  font-size: 12px;
}

.time-text,
.weather-text {
  font-weight: 500;
}

.weather-location {
  font-size: 10px;
  opacity: 0.8;
}

/* Responsive Design */
@media (max-width: 768px) {
  .prototype-header {
    padding-top: max(env(safe-area-inset-top), 8px);
  }

  .header-toolbar {
    padding: 0 16px;
    min-height: 56px;
    padding-top: max(env(safe-area-inset-top), 4px);
  }

  /* Mobile Header Layout */
  .header-top-row {
    padding: 4px 12px;
    min-height: 44px;
  }

  .header-bottom-row {
    padding: 0 12px 6px;
  }

  .header-info {
    gap: 8px;
  }

  .time-display,
  .weather-display,
  .weather-loading,
  .weather-error {
    font-size: 11px;
  }

  .time-text,
  .weather-text {
    font-size: 11px;
  }

  .weather-location {
    font-size: 9px;
  }

  /* Hide time display on mobile to save space */
  .time-display {
    display: none;
  }

  /* Make weather display more compact */
  .weather-display {
    flex-direction: column;
    align-items: flex-start;
    gap: 2px;
  }

  .weather-location {
    display: none;
  }

  .q-page-container {
    padding: 8px;
  }

  .q-card {
    margin: 8px 0;
    border-radius: 12px;
  }

  .q-card__section {
    padding: 16px;
  }

  .management-cards-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .greeting-content {
    flex-direction: column;
    text-align: center;
    gap: 12px;
    padding: 16px;
  }

  .greeting-title {
    font-size: 1.5rem;
    margin-bottom: 8px;
  }

  .greeting-subtitle {
    font-size: 13px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .stat-card {
    padding: 16px;
  }

  .stat-value {
    font-size: 24px;
  }

  .stat-label {
    font-size: 13px;
  }

  .patient-card {
    flex-direction: column;
    text-align: center;
    padding: 16px;
  }

  .patient-info h6 {
    font-size: 16px;
    margin-bottom: 4px;
  }

  .patient-info .text-caption {
    font-size: 12px;
  }

  .patient-actions {
    justify-content: center;
    gap: 8px;
    margin-top: 12px;
  }

  .q-btn {
    padding: 8px 12px;
    font-size: 12px;
    border-radius: 6px;
  }

  .q-field {
    margin-bottom: 12px;
  }

  .q-field__label {
    font-size: 14px;
  }

  .q-field__control {
    font-size: 14px;
  }
}

/* Profile Avatar Styles - Circular Design */
.profile-avatar {
  border: 3px solid #1e7668 !important;
  border-radius: 50% !important;
  overflow: hidden !important;
}

.profile-avatar img {
  border-radius: 50% !important;
  width: 100% !important;
  height: 100% !important;
  object-fit: cover !important;
}

.profile-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1e7668;
  color: white;
  font-size: 24px;
  font-weight: bold;
  border-radius: 50%;
}

.upload-btn {
  position: absolute;
  bottom: -5px;
  right: -5px;
  background: #1e7668 !important;
  border-radius: 50% !important;
  width: 24px !important;
  height: 24px !important;
  min-height: 24px !important;
  padding: 0 !important;
}

.verified-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

/* Notification styles */
.unread {
  background-color: rgba(25, 118, 210, 0.05);
  border-left: 3px solid #1976d2;
}

.unread .q-item-label {
  font-weight: 600;
}

@media (max-width: 480px) {
  .prototype-header {
    padding-top: max(env(safe-area-inset-top), 12px);
  }

  .header-toolbar {
    padding: 0 12px;
    min-height: 52px;
    padding-top: max(env(safe-area-inset-top), 6px);
  }

  /* Mobile Header Layout - Extra Small */
  .header-top-row {
    padding: 2px 8px;
    min-height: 40px;
  }

  .header-bottom-row {
    padding: 0 8px 4px;
  }

  .header-info {
    gap: 6px;
  }

  .time-display,
  .weather-display,
  .weather-loading,
  .weather-error {
    font-size: 10px;
  }

  .time-text,
  .weather-text {
    font-size: 10px;
  }

  /* Make weather even more compact */
  .weather-display {
    flex-direction: row;
    align-items: center;
    gap: 2px;
  }

  .weather-location {
    display: none;
  }
}
</style>
