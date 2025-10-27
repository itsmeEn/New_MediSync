<template>
  <q-layout view="hHh Lpr fFf">
    <DoctorHeader @toggle-drawer="rightDrawerOpen = !rightDrawerOpen" />

    <DoctorSidebar v-model="rightDrawerOpen" :active-route="isArchiveView ? 'patient-archive' : 'patients'" />

    <q-page-container class="page-container-with-fixed-header safe-area-bottom role-body-bg">
      <div class="patient-management-content">
        <div class="greeting-section">
          <q-card class="greeting-card">
            <q-card-section class="greeting-content">
              <div class="greeting-text">
                <h2 class="greeting-title">{{ greetingTitle }}</h2>
                <p class="greeting-subtitle">{{ greetingSubtitle }}</p>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <div class="management-cards-grid" v-if="false">
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
                    :class="['patient-card', { selected: selectedPatient?.id === patient.id }]"
                    :aria-selected="selectedPatient?.id === patient.id ? 'true' : 'false'"
                    @click="selectPatient(patient)"
                  >
                    <div class="patient-avatar">
                      <q-avatar size="50px">
                        <img
                          v-if="hasProfileSrc(patient.profile_picture)"
                          :src="profileSrc(patient.profile_picture)"
                          :alt="patient.full_name ?? 'Patient avatar'"
                          @error="onAvatarError(patient)"
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
                      <q-btn
                        flat
                        round
                        icon="send"
                        color="info"
                        size="sm"
                        @click.stop="sendPatientRecords(patient)"
                        unelevated
                      >
                        <q-tooltip>Send Records</q-tooltip>
                      </q-btn>
                      <q-btn
                        flat
                        round
                        icon="archive"
                        color="warning"
                        size="sm"
                        @click.stop="archivePatient(patient)"
                        unelevated
                      >
                        <q-tooltip>Archive Patient</q-tooltip>
                      </q-btn>
                    </div>
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </div>

          <div class="right-column">
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
              <q-card-actions align="right" class="q-px-md q-pb-md">
                <q-btn
                  color="primary"
                  icon="refresh"
                  size="sm"
                  label="Refresh"
                  @click="loadDoctorStats"
                  :loading="statsLoading"
                  aria-label="Refresh patient statistics"
                  unelevated
                />
              </q-card-actions>
              <q-card-section class="card-content">
                <div v-if="statsLoading" class="loading-section" aria-live="polite">
                  <q-spinner color="primary" size="2em" />
                  <p class="loading-text">Updating statistics...</p>
                </div>
                <div v-else class="stats-chart" aria-label="Patient statistics chart">
                  <div class="chart-row">
                    <div class="chart-label">Active</div>
                    <q-linear-progress :value="stats.active_rate" color="blue" size="md" aria-label="Active cases rate" />
                  </div>
                  <div class="chart-row">
                    <div class="chart-label">Recovery</div>
                    <q-linear-progress :value="stats.recovery_rate" color="green" size="md" aria-label="Recovery rate" />
                  </div>
                </div>
              </q-card-section>
            </q-card>

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
                      <div class="nurse-details">
                        Department: {{ nurse.department || nurse.specialization || '—' }}
                        <span class="separator">•</span>
                        <q-chip
                          :color="getAvailabilityColor(nurse.availability ?? nurse.status ?? 'Available')"
                          text-color="white"
                          size="sm"
                          :label="(nurse.availability ?? nurse.status ?? 'Available')"
                          dense
                          class="status-chip"
                        />
                      </div>
                      <div class="nurse-contact">Contact: {{ nurse.email || '—' }}</div>
                    </div>
                  </div>
                </div>
              </q-card-section>
            </q-card>

            <q-card class="dashboard-card medical-records-card">
              <q-card-section class="card-content">
                <div class="card-text">
                  <div class="card-title">Medical Records</div>
                  <div class="card-description">Organized patient medical history and archives</div>
                </div>
                <div class="card-icon">
                  <q-icon name="folder" size="2.2rem" />
                </div>
              </q-card-section>
              <q-card-section class="card-content">
                <q-tabs v-model="recordsTab" dense class="q-mb-sm" aria-label="Patient archives navigation">
                  <q-tab name="all" label="All" />
                  <q-tab name="hp" label="H&P" />
                  <q-tab name="soap" label="SOAP" />
                  <q-tab name="orders" label="Orders" />
                  <q-tab name="procedure" label="Procedure" />
                </q-tabs>
                <div class="row items-center q-col-gutter-sm q-mb-sm">
                  <div class="col-12 col-sm-8">
                    <q-input v-model="recordsSearch" outlined dense label="Search records" debounce="300" aria-label="Search medical records" />
                  </div>
                  <div class="col-12 col-sm-4 flex justify-end">
                    <q-btn color="primary" icon="refresh" size="sm" label="Refresh" @click="loadMedicalRecords" :loading="recordsLoading" aria-label="Refresh medical records" />
                  </div>
                </div>
              </q-card-section>
              <q-card-section class="card-content">
                <div v-if="recordsLoading" class="loading-section" aria-live="polite">
                  <q-spinner color="primary" size="2em" />
                  <p class="loading-text">Loading medical records...</p>
                </div>
                <div v-else-if="filteredRecords.length === 0" class="empty-section">
                  <q-icon name="folder_open" size="48px" color="grey-5" />
                  <p class="empty-text">No records found</p>
                </div>
                <div v-else class="records-list">
                  <q-list bordered separator>
                    <q-item v-for="rec in filteredRecords" :key="String(rec.id)" clickable>
                      <q-item-section>
                        <q-item-label>{{ rec.patient_name }} — {{ (rec.assessment_type || '').toUpperCase() }}</q-item-label>
                        <q-item-label caption>
                          {{ rec.medical_condition || 'N/A' }} • {{ formatDate(rec.last_assessed_at) }} • {{ rec.hospital_name || 'Unknown Hospital' }}
                        </q-item-label>
                      </q-item-section>
                      <q-item-section side>
                        <q-btn icon="visibility" color="primary" size="sm" @click.stop="previewRecord(rec)" aria-label="Preview record" />
                        <q-btn icon="download" color="secondary" size="sm" class="q-ml-xs" @click.stop="downloadRecord(rec)" aria-label="Download record" />
                      </q-item-section>
                    </q-item>
                  </q-list>
                </div>
              </q-card-section>
            </q-card>

            <q-card class="dashboard-card form-creation-card">
              <q-card-section class="card-content">
                <div class="card-text">
                  <div class="card-title">OPD Form Creation</div>
                  <div class="card-description">Create new clinical documentation for selected patient</div>
                </div>
                <div class="card-icon"><q-icon name="edit_document" size="2.2rem" /></div>
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
        
        <div class="patient-archive-view" v-else>
          <div class="row q-col-gutter-lg">
            <div class="col-12">
              <q-card class="dashboard-card archive-search-card">
                <q-card-section class="card-header">
                  <h5 class="card-title">Archived Patient Search & Filters</h5>
                  <q-btn color="secondary" icon="search" size="sm" label="Search" unelevated />
                </q-card-section>
                <q-card-section class="card-content">
                  <div class="row q-col-gutter-md">
                    <div class="col-12 col-md-8">
                      <q-input outlined dense v-model="archiveSearchText" label="Search Patient Name or ID" />
                    </div>
                    <div class="col-12 col-md-4">
                      <q-select outlined dense v-model="archiveFilterStatus" :options="['All', 'Discharged', 'Deceased', 'Long-term']" label="Filter Status" />
                    </div>
                  </div>
                </q-card-section>
              </q-card>
            </div>
            
            <div class="col-12">
              <q-card class="dashboard-card archive-list-card">
                <q-card-section class="card-header">
                  <h5 class="card-title">Archived Patients List (Read-Only)</h5>
                </q-card-section>
                <q-card-section class="card-content">
                  <q-list bordered separator v-if="archivePatients.length > 0">
                    <q-item v-for="patient in archivePatients" :key="String(patient.id)" class="q-py-md">
                      <q-item-section avatar>
                        <q-icon name="person_off" color="grey-6" />
                      </q-item-section>
                      <q-item-section>
                        <q-item-label class="text-bold">{{ patient.full_name }}</q-item-label>
                        <q-item-label caption>Archived — {{ patient.assignment_status || 'archived' }}</q-item-label>
                      </q-item-section>
                      <q-item-section side>
                        <q-btn color="primary" icon="unarchive" label="Restore" size="sm" dense />
                      </q-item-section>
                    </q-item>
                  </q-list>
                  <div v-if="archivePatients.length === 0" class="empty-section q-mt-md">
                    <q-icon name="archive" size="48px" color="grey-5" />
                    <p class="empty-text">No archived patients found.</p>
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </div>
        </div>
    </q-page-container>
    
    <q-dialog v-model="showRecordDialog" transition-show="scale" transition-hide="scale" :persistent="false" content-class="record-dialog-container" aria-label="Record preview dialog">
      <q-card class="record-dialog-card" style="min-width:600px;max-width:95vw;">
        <q-card-section class="card-header">
          <div class="row items-center justify-between">
            <div class="text-h6">Record Preview</div>
            <q-btn flat round dense icon="close" aria-label="Close record preview" @click="showRecordDialog = false" />
          </div>
        </q-card-section>
        <q-separator />
        <q-card-section class="card-content">
          <div class="q-mb-sm"><strong>Patient:</strong> {{ selectedRecord?.patient_name }}</div>
          <div class="q-mb-sm"><strong>Type:</strong> {{ (selectedRecord?.assessment_type || '').toUpperCase() }}</div>
          <div class="q-mb-sm"><strong>Condition:</strong> {{ selectedRecord?.medical_condition || 'N/A' }}</div>
          <q-banner dense class="q-mt-md q-mb-md" icon="description">
            Decrypted Assessment Data
          </q-banner>
          <pre class="record-json" aria-label="Decrypted assessment data"><code>{{ JSON.stringify(selectedRecord?.decrypted_assessment_data || {}, null, 2) }}</code></pre>
        </q-card-section>
        <q-card-actions align="right" class="q-px-md q-pb-md">
          <q-btn color="secondary" icon="download" size="sm" label="Download" @click="selectedRecord && downloadRecord(selectedRecord)" aria-label="Download record" />
        </q-card-actions>
      </q-card>
    </q-dialog>

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
import { useRoute } from 'vue-router'; // <-- NEW IMPORT
import { useQuasar } from 'quasar';
import { api } from 'boot/axios';
import DoctorHeader from '../components/DoctorHeader.vue';
import DoctorSidebar from '../components/DoctorSidebar.vue';

// Types (Keep existing types)
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

interface MedicalRecord {
  id: number | string;
  patient_id?: number | string;
  patient_name: string;
  assessment_type: string;
  medical_condition?: string;
  decrypted_assessment_data?: Record<string, unknown> | null;
  last_assessed_at?: string;
  hospital_name?: string;
}

// Router for conditional view logic
const route = useRoute(); // <-- NEW ROUTE INSTANCE

// Reactive data (Keep existing data)
const $q = useQuasar();
const rightDrawerOpen = ref(false);
const loading = ref(false);
const searchText = ref('');
const patients = ref<Patient[]>([]);
const selectedPatient = ref<Patient | null>(null);
const showNotifications = ref(false);

// Archive View State (NEW)
const archiveSearchText = ref('');
const archiveFilterStatus = ref('All');
// This is a placeholder for actual archived patient data
const archivePatients = ref<Patient[]>([]);


// ---------------------------------------------
// View Logic Computed Properties (NEW)
// ---------------------------------------------

/**
 * Determines if the user is on the dedicated patient archive route.
 * Assumes the archive route is defined as a nested route like '/.../archive'.
 */
const isArchiveView = computed(() => {
  return route.path.endsWith('/archive');
});

/**
 * Dynamic title for the greeting card based on the current view.
 */
const greetingTitle = computed(() => {
  return isArchiveView.value ? 'Patient Archive' : 'Patient Management';
});

/**
 * Dynamic subtitle for the greeting card based on the current view.
 */
const greetingSubtitle = computed(() => {
  return isArchiveView.value
    ? 'Browse and restore archived patient records and documentation.'
    : 'Manage your patients and their medical records';
});


// ---------------------------------------------
// Existing Form state and handler for OPD forms (Keep existing logic)
// ---------------------------------------------
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

// ---------------------------------------------
// Null-safe helpers for avatar and bindings
// ---------------------------------------------
const hasProfileSrc = (pic?: string | null): boolean => {
  return !!pic;
};

const profileSrc = (pic?: string | null): string => {
  if (!pic) return '';
  return pic.startsWith('http') ? pic : `http://localhost:8000${pic}`;
};

const onAvatarError = (p: Patient): void => {
  // Reset to null to avoid repeated load errors and satisfy strict typing
  p.profile_picture = null;
};

// User profile data (Kept for completeness)
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

// Notification system (Kept for completeness)
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

// Medical Requests state (Kept for completeness)
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
      context: { error: String(error) }
    });
  } finally {
    medicalRequestsLoading.value = false;
  }
};

// Available Nurses list (Kept for completeness)
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

const getAvailabilityColor = (status: string): string => {
  const s = (status || '').toLowerCase();
  if (s.includes('break')) return 'warning';
  if (s.includes('occupied') || s.includes('busy')) return 'negative';
  if (s.includes('available')) return 'positive';
  return 'primary';
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

// Patients filtering and statistics (Kept for completeness)
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

// Patient statistics state and loader
const stats = ref<{ total_patients: number; active_cases: number; recovery_rate: number; active_rate: number }>({ total_patients: 0, active_cases: 0, recovery_rate: 0, active_rate: 0 })
const statsLoading = ref(false)

const loadDoctorStats = async (): Promise<void> => {
  statsLoading.value = true;
  try {
    // Try backend dashboard stats first
    type DashboardStats = { total_patients?: number; patients_total?: number; active_cases?: number; pending_cases?: number; recovered_cases?: number; completed_cases?: number; };
    const res = await api.get('/operations/dashboard/stats/').catch(() => ({ data: null as DashboardStats | null }))
    const data = (res as { data: DashboardStats | null }).data
    if (data && typeof data === 'object') {
      const total = Number(data.total_patients ?? data.patients_total ?? 0)
      const active = Number(data.active_cases ?? data.pending_cases ?? 0)
      const recovered = Number(data.recovered_cases ?? data.completed_cases ?? 0)
      const denom = Math.max(total, 1)
      stats.value = {
        total_patients: total,
        active_cases: active,
        recovery_rate: Math.min(1, Math.max(0, recovered / denom)),
        active_rate: Math.min(1, Math.max(0, active / denom))
      }
    } else {
      // Fallback: compute from current patients list
      const total = patients.value.length
      const active = patients.value.filter(p => ['accepted', 'in_progress'].includes(String(p.assignment_status))).length
      const completed = patients.value.filter(p => String(p.assignment_status) === 'completed').length
      const denom = Math.max(total, 1)
      stats.value = {
        total_patients: total,
        active_cases: active,
        recovery_rate: Math.min(1, Math.max(0, completed / denom)),
        active_rate: Math.min(1, Math.max(0, active / denom))
      }
    }
  } catch (error) {
    console.error('Failed to load doctor stats:', error)
    $q.notify({ type: 'negative', message: 'Failed to load patient statistics', position: 'top' })
  } finally {
    statsLoading.value = false
  }
}

// Medical records state and loader (Kept for completeness)
const records = ref<MedicalRecord[]>([])
const recordsLoading = ref(false)
const recordsTab = ref<'all' | 'hp' | 'soap' | 'orders' | 'procedure'>('all')
const recordsSearch = ref('')
const showRecordDialog = ref(false)
const selectedRecord = ref<MedicalRecord | null>(null)

const loadMedicalRecords = async (): Promise<void> => {
  recordsLoading.value = true
  try {
    type ArchiveItem = { id?: number | string; archive_id?: number | string; _id?: number | string; patient_id?: number | string; patient_name?: string; name?: string; assessment_type?: string; medical_condition?: string; decrypted_assessment_data?: Record<string, unknown> | null; last_assessed_at?: string; updated_at?: string; created_at?: string; hospital_name?: string; };
    type ArchiveResponse = { results?: ArchiveItem[] } | ArchiveItem[];
    const res = await api.get('/operations/archives/')
    const data = (res as { data: ArchiveResponse }).data
    const list: ArchiveItem[] = Array.isArray(data) ? (data as ArchiveItem[]) : (data.results ?? [])
    records.value = list.map((r): MedicalRecord => {
      const last = r.last_assessed_at ?? r.updated_at ?? r.created_at;
      return {
        id: r.id ?? r.archive_id ?? r._id ?? Math.random(),
        ...(r.patient_id != null ? { patient_id: r.patient_id } : {}),
        patient_name: r.patient_name ?? r.name ?? 'Unknown Patient',
        assessment_type: String(r.assessment_type || 'unknown').toLowerCase(),
        medical_condition: r.medical_condition ?? '',
        decrypted_assessment_data: r.decrypted_assessment_data ?? null,
        ...(last != null ? { last_assessed_at: last } : {}),
        hospital_name: r.hospital_name ?? ''
      };
    })
  } catch (error) {
    console.error('Failed to load medical records:', error)
    records.value = []
    $q.notify({ type: 'negative', message: 'Failed to load medical records', position: 'top' })
    void api.post('/operations/client-log/', {
      level: 'error',
      message: 'loadMedicalRecords failed',
      route: 'DoctorPatientManagement',
      context: { error: String(error) }
    })
  } finally {
    recordsLoading.value = false
  }
}

const filteredRecords = computed(() => {
  const tab = recordsTab.value
  const search = recordsSearch.value.trim().toLowerCase()
  return records.value.filter(r => {
    const matchTab = tab === 'all' ? true : r.assessment_type === tab
    const matchSearch = !search || (r.patient_name || '').toLowerCase().includes(search) || (r.medical_condition || '').toLowerCase().includes(search) || (r.assessment_type || '').toLowerCase().includes(search)
    return matchTab && matchSearch
  })
})

const previewRecord = (rec: MedicalRecord): void => {
  selectedRecord.value = rec
  showRecordDialog.value = true
}

const downloadRecord = (rec: MedicalRecord): void => {
  try {
    const url = `/api/operations/archives/${rec.id}/export/`
    window.open(url, '_blank')
  } catch (error) {
    console.error('Download record failed:', error)
    $q.notify({ type: 'negative', message: 'Failed to download record', position: 'top' })
  }
}

const formatDate = (iso?: string): string => {
  if (!iso) return '—'
  try {
    const d = new Date(iso)
    return d.toLocaleString()
  } catch {
    return String(iso)
  }
}

// Patient assignment data loading and actions (Kept for completeness)
const loadPatients = async () => {
  loading.value = true;
  try {
    // Load only assigned patients from the assignment API
    const response = await api.get('/operations/doctor/assignments/');
    if (response.data && Array.isArray(response.data)) {
      // Transform assignment data to patient format
      patients.value = response.data.map((assignment: { id: number; patient_id: number; patient_name: string; status: string; assigned_by_name: string; assigned_at: string; specialization_required: string; assignment_reason: string; priority: string; accepted_at: string | null; completed_at: string | null; }) => ({
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
      // Removed loadVerificationStatus and loadUserProfile calls as they are not defined here
      // const first = patients.value[0];
      // if (first) {
      //   void loadVerificationStatus(first);
      // }
    } else {
      patients.value = [];
    }
  } catch (error) {
    console.error('Failed to load assigned patients:', error);
    patients.value = [];
    $q.notify({ type: 'negative', message: 'Failed to load patient list', position: 'top' });
  } finally {
    loading.value = false;
  }
};

const selectPatient = (patient: Patient): void => {
  if (selectedPatient.value && selectedPatient.value.id === patient.id) {
    // Deselect if already selected
    selectedPatient.value = null;
    selectedForm.value = '';
  } else {
    // Select the new patient
    selectedPatient.value = patient;
    selectedForm.value = ''; // Reset form selection
  }
};

const viewPatientDetails = (patient: Patient): void => {
  $q.notify({ type: 'info', message: `Viewing details for ${patient.full_name}` });
  // Add actual navigation logic here (e.g., router.push(`/patient/${patient.id}/details`))
};

const editPatient = (patient: Patient): void => {
  $q.notify({ type: 'info', message: `Editing patient ${patient.full_name}` });
  // Add actual editing modal/navigation logic here
};

// Add: Send and Archive action handlers
const sendPatientRecords = async (patient: Patient): Promise<void> => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      $q.notify({ type: 'negative', message: 'Authorization required to send records', position: 'top' });
      return;
    }

    const payload = { patient_id: patient.id, destination: 'patient_email' };
    await api.post('/operations/messaging/send-records/', payload).catch(async (err) => {
      // Fallback log to ensure traceability
      console.error('Primary send endpoint failed, logging:', err);
      await api.post('/operations/client-log/', {
        level: 'warning',
        message: 'sendPatientRecords fallback log',
        route: 'DoctorPatientArchive',
        context: { patient_id: patient.id, error: String(err) }
      });
      throw err;
    });

    $q.notify({ type: 'positive', message: `Records sent for ${patient.full_name}`, position: 'top' });
  } catch (error) {
    console.error('Failed to send patient records:', error);
    $q.notify({ type: 'negative', message: 'Failed to send patient records', position: 'top' });
  }
};

const archivePatient = async (patient: Patient): Promise<void> => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      $q.notify({ type: 'negative', message: 'Authorization required to archive', position: 'top' });
      return;
    }

    const payload = { patient_id: patient.id, assignment_id: patient.assignment_id };
    // Try the likely archive endpoint; if it fails, log the attempt
    await api.post('/operations/patient/archive/', payload).catch(async (err) => {
      console.warn('Primary archive endpoint failed, trying alternative:', err);
      try {
        await api.post('/operations/archives/archive-patient/', payload);
      } catch (err2) {
        await api.post('/operations/client-log/', {
          level: 'error',
          message: 'archivePatient failed on all endpoints',
          route: 'DoctorPatientArchive',
          context: { patient_id: patient.id, assignment_id: patient.assignment_id, error: String(err2) }
        });
        throw err2;
      }
    });

    // Update local state upon success
    patients.value = patients.value.filter((p) => p.id !== patient.id);
    archivePatients.value = [{ ...patient, assignment_status: 'archived' }, ...archivePatients.value];
    if (selectedPatient.value?.id === patient.id) {
      selectedPatient.value = null;
      selectedForm.value = '';
    }

    // Refresh records to reflect new archive entries
    void loadMedicalRecords();

    $q.notify({ type: 'positive', message: `${patient.full_name} archived successfully`, position: 'top' });
  } catch (error) {
    console.error('Failed to archive patient:', error);
    $q.notify({ type: 'negative', message: 'Failed to archive patient', position: 'top' });
  }
};
const handleNotificationClick = (notification: DoctorNotification) => {
  $q.notify({ type: 'positive', message: `Notification opened: ${notification.message}` });
  // Add logic to mark as read and navigate
};

const markAllNotificationsRead = () => {
  $q.notify({ type: 'positive', message: 'All notifications marked as read' });
  // Add API call to mark all as read
};

const formatTime = (iso: string): string => {
  // Simple time formatting for display
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

const formatDateTime = (iso?: string | Date): string => {
  if (!iso) return '—';
  try {
    const d = new Date(iso);
    return d.toLocaleString();
  } catch {
    return String(iso);
  }
};

// Lifecycle (Kept for completeness)
onMounted(() => {
  void loadPatients();
  void loadDoctorStats();
  void loadMedicalRequests();
  void loadAvailableNurses();
  void loadMedicalRecords();
  void loadNotifications();
});

onUnmounted(() => {
 
});
</script>