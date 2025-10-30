<template>
  <q-layout view="hHh Lpr fFf">
    <!-- Standardized Header Component -->
    <NurseHeader @toggle-drawer="rightDrawerOpen = !rightDrawerOpen" />

    <!-- Standardized Sidebar Component -->
    <NurseSidebar v-model="rightDrawerOpen" active-route="patients" />

    <q-page-container class="page-container-with-fixed-header role-body-bg">
      <!-- Main Content -->
      <div class="patient-management-content">
        <!-- Header Section -->
        <div class="greeting-section">
          <q-card class="greeting-card">
            <q-card-section class="greeting-content">
              <div class="greeting-text">
                <h4 class="greeting-title">Patient Management</h4>
                <p class="greeting-subtitle">Manage your patients and their medical records</p>
              </div>
              <div class="greeting-icon">
                <q-icon name="people" size="3rem" />
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- OPD Forms Modal (kept; card removed) -->
        <q-dialog
          v-model="formDialogOpen"
          transition-show="scale"
          transition-hide="scale"
          :persistent="false"
          content-class="form-dialog-container"
        >
          <q-card class="form-dialog-card">
            <q-card-section class="card-header">
              <div class="row items-center justify-between">
                <div class="text-h6">{{ currentFormTitle }}</div>
                <q-btn flat round dense icon="close" aria-label="Close OPD Form modal" @click="formDialogOpen = false" />
              </div>
            </q-card-section>
            <q-separator />
            <q-card-section class="card-content">
              <q-inner-loading :showing="demoLoading">
                <q-spinner color="primary" />
              </q-inner-loading>

              <!-- Patient Demographics (Standard Upper Section) -->
              <div v-if="demographics" class="q-gutter-md q-mb-md">
                <div class="text-subtitle1 text-bold">Patient Demographics</div>
                <div class="row q-col-gutter-md">
                  <div class="col-12 col-sm-6 col-md-3"><q-input :model-value="demographics.mrn" label="MRN" outlined dense readonly/></div>
                  <div class="col-12 col-sm-6 col-md-3"><q-input :model-value="demographicFullName" label="Name" outlined dense readonly/></div>
                  <div class="col-12 col-sm-6 col-md-3"><q-input :model-value="formattedDOB" label="Date of Birth" outlined dense readonly/></div>
                  <div class="col-12 col-sm-6 col-md-3"><q-input :model-value="String(demographicAge)" label="Age" outlined dense readonly/></div>
                  <div class="col-12 col-sm-6 col-md-3"><q-input :model-value="demographics.sex" label="Sex/Gender" outlined dense readonly/></div>
                  <div class="col-12 col-sm-6 col-md-3"><q-input :model-value="demographics.homeAddress" label="Home Address" outlined dense readonly/></div>
                  <div class="col-12 col-sm-6 col-md-3"><q-input :model-value="demographics.cellPhone" label="Cell Phone" outlined dense readonly/></div>
                  <div class="col-12 col-sm-6 col-md-3"><q-input :model-value="demographics.email" label="Email" outlined dense readonly/></div>
                  <div class="col-12 col-sm-6 col-md-3"><q-input :model-value="demographics.emergencyName" label="Emergency Contact" outlined dense readonly/></div>
                  <div class="col-12 col-sm-6 col-md-3"><q-input :model-value="demographics.emergencyPhone" label="Emergency Phone" outlined dense readonly/></div>
                </div>
                <div v-if="demoLoadError" class="text-negative text-caption">{{ demoLoadError }}</div>
              </div>

              <!-- Removed inline OPD form selector; modal reflects patient list selection -->
              <q-banner dense class="q-mb-sm" icon="assignment">
                {{ currentFormTitle }}
              </q-banner>

              <!-- Nursing Intake & Assessment Form (Modal) -->
              <div v-if="selectedPatient && selectedForm === 'intake'" class="q-gutter-md">
                <div class="row q-col-gutter-md">
                  <div class="col-12">
                    <div class="text-subtitle1 text-bold">Vitals</div>
                  </div>
                  <div class="col-12 col-sm-6 col-md-4"><q-input v-model="intakeForm.bp" label="Blood Pressure" outlined dense :rules="[val => !!val || 'Required']"/></div>
                  <div class="col-12 col-sm-6 col-md-4"><q-input v-model="intakeForm.hr" label="Heart Rate" outlined dense :rules="[val => !!val || 'Required']"/></div>
                  <div class="col-12 col-sm-6 col-md-4"><q-input v-model="intakeForm.rr" label="Respiratory Rate" outlined dense :rules="[val => !!val || 'Required']"/></div>
                  <div class="col-12 col-sm-6 col-md-4"><q-input v-model="intakeForm.temp" label="Temperature" outlined dense :rules="[val => !!val || 'Required']"/></div>
                  <div class="col-12 col-sm-6 col-md-4"><q-input v-model="intakeForm.o2" label="Oxygen Saturation" outlined dense :rules="[val => !!val || 'Required']"/></div>
                  <div class="col-12 col-sm-6 col-md-4"><q-input v-model="intakeForm.weight" label="Weight" outlined dense :rules="[val => !!val || 'Required']"/></div>
                  <div class="col-12 col-sm-6 col-md-4"><q-input v-model="intakeForm.height" label="Height" outlined dense :rules="[val => !!val || 'Required']"/></div>
                </div>

                <div class="row q-col-gutter-md q-mt-sm">
                  <div class="col-12 col-md-6"><q-input v-model="intakeForm.chiefComplaint" label="Chief Complaint" type="textarea" outlined dense :rules="[val => !!val || 'Required']"/></div>
                  <div class="col-12 col-md-6">
                    <div class="q-mb-xs">Pain Score (0-10)</div>
                    <q-slider v-model="intakeForm.painScore" :min="0" :max="10" color="primary"/>
                  </div>
                </div>

                <div class="q-mt-md">
                  <div class="text-subtitle1 text-bold">Allergies</div>
                  <div v-for="(a, idx) in intakeForm.allergies" :key="idx" class="row q-col-gutter-sm q-mt-xs">
                    <div class="col-12 col-sm-5"><q-input v-model="a.name" label="Allergen" outlined dense :rules="[v=>!!v||'Required']"/></div>
                    <div class="col-12 col-sm-5"><q-input v-model="a.reaction" label="Reaction" outlined dense :rules="[v=>!!v||'Required']"/></div>
                    <div class="col-12 col-sm-2"><q-btn flat icon="delete" color="negative" @click="removeAllergy(idx)"/></div>
                  </div>
                  <q-btn flat icon="add" label="Add Allergy" color="primary" class="q-mt-sm" @click="addAllergy"/>
                </div>

                <div class="row q-col-gutter-md q-mt-md">
                  <div class="col-12 col-md-6"><q-select v-model="intakeForm.mentalStatus" :options="mentalStatusOptions" label="Mental Status" emit-value map-options outlined dense :rules="[v=>!!v||'Required']"/></div>
                  <div class="col-12 col-md-6"><q-input v-model="intakeForm.fallRisk" label="Fall Risk Score" outlined dense :rules="[v=>!!v||'Required']"/></div>
                </div>

                <div class="row q-gutter-sm q-mt-md">
                  <q-btn color="primary" label="Save" @click="saveIntake"/>
                  <q-btn flat color="secondary" label="Reset" @click="resetIntake"/>
                </div>
              </div>

              <!-- Graphic Records / Flow Sheets (Modal) -->
              <div v-if="selectedPatient && selectedForm === 'flow'" class="q-gutter-md">
                <div class="row q-col-gutter-md">
                  <div class="col-12 col-md-4"><q-input v-model="newFlowEntry.timestamp" label="Time" type="datetime-local" outlined dense/></div>
                  <div class="col-12 col-sm-6 col-md-2"><q-input v-model="newFlowEntry.bp" label="BP" outlined dense/></div>
                  <div class="col-12 col-sm-6 col-md-2"><q-input v-model="newFlowEntry.hr" label="HR" outlined dense/></div>
                  <div class="col-12 col-sm-6 col-md-2"><q-input v-model.number="newFlowEntry.pain" label="Pain" type="number" outlined dense/></div>
                  <div class="col-12 col-sm-6 col-md-3"><q-input v-model.number="newFlowEntry.intake" label="Intake (mL)" type="number" outlined dense/></div>
                  <div class="col-12 col-sm-6 col-md-3"><q-input v-model.number="newFlowEntry.output" label="Output (mL)" type="number" outlined dense/></div>
                  <div class="col-12"><q-input v-model="newFlowEntry.siteCheck" label="Site Check Notes" outlined dense/></div>
                  <div class="col-12"><q-input v-model="newFlowEntry.interventions" label="Interventions" outlined dense/></div>
                </div>
                <div class="row q-gutter-sm q-mt-sm">
                  <q-btn color="primary" label="Add Entry" @click="addFlowEntry"/>
                  <q-btn flat color="secondary" label="Save All" @click="saveFlowSheet"/>
                </div>

                <q-separator class="q-my-md"/>
                <div>
                  <div class="text-subtitle1 text-bold q-mb-sm">Entries</div>
                  <q-list bordered separator>
                    <q-item v-for="(entry, idx) in flowSheetEntries" :key="idx">
                      <q-item-section>
                        <q-item-label>{{ entry.timestamp }} — BP {{ entry.bp }}, HR {{ entry.hr }}, Pain {{ entry.pain }}</q-item-label>
                        <q-item-label caption>I&O: {{ entry.intake }} / {{ entry.output }} | Site: {{ entry.siteCheck }} | Interventions: {{ entry.interventions }}</q-item-label>
                      </q-item-section>
                      <q-item-section side>
                        <q-btn dense flat icon="delete" color="negative" @click="removeFlowEntry(idx)"/>
                      </q-item-section>
                    </q-item>
                    <q-item v-if="flowSheetEntries.length === 0">
                      <q-item-section>No entries yet</q-item-section>
                    </q-item>
                  </q-list>
                </div>
              </div>

              <!-- Medication Administration Record (MAR) (Modal) -->
              <div v-if="selectedPatient && selectedForm === 'mar'" class="q-gutter-md">
                <div class="row q-col-gutter-md">
                  <div class="col-12 col-md-4"><q-input v-model="newMarEntry.datetime" label="Date/Time Administered" type="datetime-local" outlined dense/></div>
                  <div class="col-12 col-sm-6 col-md-3"><q-input v-model="newMarEntry.medName" label="Medication Name" outlined dense/></div>
                  <div class="col-12 col-sm-6 col-md-2"><q-input v-model="newMarEntry.dose" label="Dose" outlined dense/></div>
                  <div class="col-12 col-sm-6 col-md-2"><q-input v-model="newMarEntry.route" label="Route" outlined dense/></div>
                  <div class="col-12 col-sm-6 col-md-3"><q-input v-model="newMarEntry.nurseId" label="Nurse Initials/ID" outlined dense/></div>
                </div>
                <div class="row q-gutter-sm q-mt-sm">
                  <q-btn color="primary" label="Add Record" @click="addMarEntry"/>
                  <q-btn flat color="secondary" label="Save All" @click="saveMar"/>
                </div>

                <q-separator class="q-my-md"/>
                <div>
                  <div class="text-subtitle1 text-bold q-mb-sm">Records</div>
                  <q-list bordered separator>
                    <q-item v-for="(entry, idx) in marEntries" :key="idx">
                      <q-item-section>
                        <q-item-label>{{ entry.datetime }} — {{ entry.medName }} {{ entry.dose }} via {{ entry.route }} by {{ entry.nurseId }}</q-item-label>
                        <q-item-label caption>
                          <span v-if="entry.isPRN">PRN: {{ entry.prnReason }} → {{ entry.prnResponse }}</span>
                          <span v-else-if="entry.notGiven">Withheld: {{ entry.withheldReason }}</span>
                          <span v-else>Given</span>
                        </q-item-label>
                      </q-item-section>
                      <q-item-section side>
                        <q-btn dense flat icon="delete" color="negative" @click="removeMarEntry(idx)"/>
                      </q-item-section>
                    </q-item>
                    <q-item v-if="marEntries.length === 0">
                      <q-item-section>No records yet</q-item-section>
                    </q-item>
                  </q-list>
                </div>
              </div>

              <!-- Discharge Checklist (Modal) -->
              <div v-if="selectedPatient && selectedForm === 'discharge'" class="q-gutter-md">
                <div class="row q-col-gutter-md">
                  <div class="col-12 col-sm-6"><q-toggle v-model="dischargeForm.verbalUnderstands" label="Patient verbalizes understanding"/></div>
                  <div class="col-12 col-sm-6"><q-toggle v-model="dischargeForm.writtenProvided" label="Written instructions provided"/></div>
                  <div class="col-12 col-sm-6"><q-input v-model="dischargeForm.followUpDate" label="Follow-up Date" type="date" outlined dense/></div>
                  <div class="col-12 col-sm-6"><q-input v-model="dischargeForm.followUpTime" label="Follow-up Time" type="time" outlined dense/></div>
                  <div class="col-12"><q-input v-model="dischargeForm.equipmentNeeds" label="Equipment Needs" type="textarea" outlined dense/></div>
                  <div class="col-12 col-sm-6"><q-input v-model="dischargeForm.finalBP" label="Final BP" outlined dense/></div>
                  <div class="col-12 col-sm-6"><q-input v-model="dischargeForm.finalHR" label="Final HR" outlined dense/></div>
                  <div class="col-12"><q-input v-model="dischargeForm.transportationStatus" label="Transportation Status" outlined dense/></div>
                  <div class="col-12 col-sm-6"><q-input v-model="dischargeForm.nurseId" label="Nurse Signature/ID" outlined dense/></div>
                  <div class="col-12 col-sm-6"><q-toggle v-model="dischargeForm.patientAcknowledged" label="Patient Signature/Acknowledgment"/></div>
                </div>
                <div class="row q-gutter-sm q-mt-sm">
                  <q-btn color="primary" label="Save" @click="saveDischarge"/>
                  <q-btn flat color="secondary" label="Reset" @click="resetDischarge"/>
                </div>
              </div>

            </q-card-section>
          </q-card>
        </q-dialog>

        <!-- Patient Document View (Modal) -->
        <q-dialog v-model="showDocumentView" transition-show="scale" transition-hide="scale" :persistent="false" content-class="document-dialog-container">
          <q-card class="document-view-card">
            <q-card-section class="doc-header">
              <div class="text-h6">{{ userProfile.hospital_name || 'Hospital' }}</div>
              <div class="text-caption">{{ userProfile.hospital_address || 'Address' }}</div>
              <div class="text-caption">Department: {{ department }}</div>
            </q-card-section>
            <q-separator />
            <q-card-section class="doc-content">
              <div class="text-subtitle1 text-bold q-mb-sm">Patient Record</div>
              <div v-if="selectedPatientDoc" class="q-gutter-sm">
                <div><strong>Name:</strong> {{ selectedPatientDoc.full_name || '—' }}</div>
                <div><strong>ID:</strong> {{ selectedPatientDoc.id }}</div>
                <div><strong>Age:</strong> {{ selectedPatientDoc.age || '—' }}</div>
                <div><strong>Gender:</strong> {{ selectedPatientDoc.gender || '—' }}</div>
                <div><strong>Blood Type:</strong> {{ selectedPatientDoc.blood_type || '—' }}</div>
                <div><strong>Condition:</strong> {{ selectedPatientDoc.medical_condition || '—' }}</div>
                <div><strong>Email:</strong> {{ selectedPatientDoc.email || '—' }}</div>
                <div><strong>Hospital:</strong> {{ selectedPatientDoc.hospital || userProfile.hospital_name || '—' }}</div>
                <div><strong>Insurance:</strong> {{ selectedPatientDoc.insurance_provider || '—' }}</div>
              </div>
              <div v-else>
                <q-banner dense class="q-mt-sm" icon="info">No patient selected</q-banner>
              </div>
            </q-card-section>
            <q-card-actions align="right">
              <q-btn flat icon="close" label="Close" @click="showDocumentView = false" />
            </q-card-actions>
          </q-card>
        </q-dialog>

        <!-- Patient Management Cards -->
        <div class="management-cards-grid">
          <div class="left-column">
            <!-- Patient List Card -->
            <q-card class="glassmorphism-card patient-list-card">
              <q-card-section class="card-header">
                <h5 class="card-title">Patient List</h5>
                <q-btn
                  color="primary"
                  icon="refresh"
                  size="sm"
                  @click="loadPatients"
                  :loading="loading"
                />
              </q-card-section>

              <q-card-section class="card-content">
                <q-banner dense class="q-mb-sm" icon="info" inline-actions>
                  Select a patient from the list to work on OPD forms. Archived patients are hidden from selection.
                </q-banner>
                <div class="row items-center q-col-gutter-sm q-mb-sm">
                  <div class="col-12 col-sm-8">
                    <q-select v-model="selectedForm" :options="opdFormOptions" outlined dense label="OPD Forms" emit-value map-options :disable="!selectedPatient" aria-label="OPD Forms"/>
                  </div>
                  <div class="col-6 col-sm-2">
                    <q-select v-model="sortKey" :options="sortOptions" outlined dense label="Sort by" emit-value map-options aria-label="Sort patients"/>
                  </div>
                  <div class="col-6 col-sm-2">
                    <q-select v-model="sortOrder" :options="orderOptions" outlined dense label="Order" emit-value map-options aria-label="Sort order"/>
                  </div>
                </div>
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
                      <q-avatar size="50px" color="primary" text-color="white">
                        <img
                          v-if="patient.profile_picture"
                          :src="
                            patient.profile_picture.startsWith('http')
                              ? patient.profile_picture
                              : `http://localhost:8000${patient.profile_picture}`
                          "
                          :alt="patient.full_name"
                          @error="patient.profile_picture = ''"
                        />
                        <div v-else class="avatar-initials">{{ getInitials(patient.full_name || '') }}</div>
                      </q-avatar>
                    </div>

                    <div class="patient-info">
                      <h6 class="patient-name">{{ patient.full_name }}</h6>
                      <p class="patient-details">
                        Age: {{ patient.age || 'N/A' }} | {{ patient.gender || 'N/A' }} |
                        {{ patient.blood_type || 'N/A' }}
                      </p>
                      <p class="patient-condition">
                        {{ patient.medical_condition || 'No condition specified' }}
                      </p>
                      <div class="patient-status">
                        <q-chip color="primary" text-color="white" size="sm"> Patient </q-chip>
                      </div>
                    </div>

                    <div class="patient-actions">
                      <q-btn
                        aria-label="View patient"
                        flat
                        round
                        icon="visibility"
                        color="primary"
                        size="sm"
                        @click.stop="viewPatientDetails(patient)"
                      >
                        <q-tooltip>View</q-tooltip>
                      </q-btn>
                      <q-btn
                        aria-label="Edit patient"
                        flat
                        round
                        icon="edit"
                        color="secondary"
                        size="sm"
                        @click.stop="editPatient(patient)"
                      >
                        <q-tooltip>Edit</q-tooltip>
                      </q-btn>
                      <q-btn
                        aria-label="Send patient records"
                        flat
                        round
                        icon="send"
                        color="positive"
                        size="sm"
                        @click.stop="sendPatientRecords(patient)"
                      >
                        <q-tooltip>Send</q-tooltip>
                      </q-btn>
                      <q-btn
                        aria-label="Archive patient"
                        flat
                        round
                        icon="archive"
                        color="negative"
                        size="sm"
                        @click.stop="archivePatient(patient)"
                      >
                        <q-tooltip>Archive</q-tooltip>
                      </q-btn>
                    </div>
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </div>
          <div class="right-column">
            <!-- Patient Statistics Card -->
            <q-card class="glassmorphism-card statistics-card section-spacing">
              <q-card-section class="card-header">
                <h5 class="card-title">Patient Statistics</h5>
              </q-card-section>

              <q-card-section class="card-content">
                <div class="stats-grid">
                  <div class="stat-item">
                    <div class="stat-number">{{ patients.length }}</div>
                    <div class="stat-label">Total Patients</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-number">{{ activePatientsCount }}</div>
                    <div class="stat-label">Active</div>
                  </div>
                </div>
              </q-card-section>
            </q-card>

            <!-- List of Available Doctors Card -->
            <q-card class="glassmorphism-card doctors-card section-spacing">
              <q-card-section class="card-header">
                <h5 class="card-title">List of Available Doctors</h5>
              </q-card-section>
              <q-card-section class="card-content">
                <div v-if="doctorsLoading" class="loading-section">
                  <q-spinner color="primary" size="2em" />
                  <p class="loading-text">Loading doctors...</p>
                </div>
                <div v-else-if="filteredAvailableDoctors.length === 0" class="empty-section">
                  <q-icon name="medical_services" size="48px" color="grey-5" />
                  <p class="empty-text">No available doctors</p>
                </div>
                <div v-else class="doctors-list">
                  <div v-for="(doc, idx) in filteredAvailableDoctors" :key="String(doc.id ?? doc.email ?? doc.full_name ?? idx)" class="doctor-row">
                    <div class="doctor-avatar">
                      <q-avatar size="40px" color="teal-8" text-color="white">
                        {{ getInitials(doc.full_name || '') }}
                      </q-avatar>
                    </div>
                    <div class="doctor-info">
                      <div class="doctor-name">{{ doc.full_name }}</div>
                      <div class="doctor-details">Specialization: {{ doc.specialization || '—' }} | Availability: {{ doc.availability ?? doc.status ?? '—' }}</div>
                    </div>
                  </div>
                </div>
              </q-card-section>
            </q-card>

            <!-- Patient Archive Card -->
            <q-card class="glassmorphism-card archive-card section-spacing">
              <q-card-section class="card-header">
                <h5 class="card-title">Patient Archive</h5>
              </q-card-section>
              <q-card-section class="card-content">
                <div class="row q-col-gutter-md q-mb-sm">
                  <div class="col-12 col-md-6"><q-input v-model="archiveFilters.query" label="Patient Name or ID" outlined dense/></div>
                  <div class="col-12 col-sm-6 col-md-3"><q-input v-model="archiveFilters.assessment_type" label="Assessment Type" outlined dense/></div>
                  <div class="col-12 col-sm-6 col-md-3"><q-input v-model="archiveFilters.medical_condition" label="Medical Condition" outlined dense/></div>
                </div>
                <div class="row q-col-gutter-md q-mb-sm">
                  <div class="col-12 col-sm-6 col-md-3"><q-input v-model="archiveFilters.start_date" label="Start Date" type="date" outlined dense/></div>
                  <div class="col-12 col-sm-6 col-md-3"><q-input v-model="archiveFilters.end_date" label="End Date" type="date" outlined dense/></div>
                  <div class="col-12 col-sm-6 col-md-3"><q-btn color="primary" icon="search" label="Search" class="full-width" :loading="archivesLoading" @click="searchArchives"/></div>
                  <div class="col-12 col-sm-6 col-md-3"><q-btn flat color="secondary" icon="clear" label="Reset" class="full-width" @click="resetArchiveFilters"/></div>
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

                <div class="row q-gutter-sm q-mt-sm" v-if="archivedRecords.length">
                  <q-btn outline color="primary" icon="file_download" label="Export Results" @click="exportFilteredArchives"/>
                </div>

                <q-dialog v-model="showArchiveDetail">
                  <q-card style="max-width: 800px; width: 90vw">
                    <q-card-section>
                      <div class="text-h6">Archived Assessment</div>
                    </q-card-section>
                    <q-separator/>
                    <q-card-section>
                      <div class="q-mb-sm"><b>Patient:</b> {{ selectedArchive?.patient_name }}</div>
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
        </div>


      <!-- Registration / Demographics Dialog -->
      <q-dialog v-model="showRegistrationDialog">
        <q-card class="registration-dialog-card" style="min-width:700px;max-width:90vw;">
          <q-card-section>
            <div class="text-h6">Patient Registration / Demographics</div>
            <div class="text-caption">Complete registration to enable OPD forms.</div>
          </q-card-section>

          <q-card-section class="q-gutter-md registration-form">
            <q-stepper v-model="registrationStep" flat animated color="primary">
              <q-step :name="1" title="Header & Administrative" subtitle="Hospital details and identifiers" done-icon="check">
                <q-slide-transition>
                  <div class="row q-col-gutter-md">
                    <div class="col-12 col-md-6">
                      <q-input v-model="registrationForm.hospitalName" label="Hospital/Clinic Name *" hint="Official facility name" outlined dense :rules="[v=>!!v || 'Required']" :input-attrs="{ 'aria-label':'Hospital/Clinic Name' }"/>
                    </div>
                    <div class="col-12 col-md-6">
                      <q-input v-model="registrationForm.departmentName" label="Department Name" hint="e.g., OPD, ER" outlined dense :input-attrs="{ 'aria-label':'Department Name' }"/>
                    </div>
                    <div class="col-12">
                      <q-input v-model="registrationForm.hospitalAddress" label="Hospital Address *" hint="Street, city, province" outlined dense :rules="[v=>!!v || 'Required']" :input-attrs="{ 'aria-label':'Hospital Address' }"/>
                    </div>
                    <div class="col-12 col-md-6">
                      <q-input v-model="registrationForm.mrn" label="Medical Record Number (MRN) *" hint="Unique hospital record ID" outlined dense :rules="[v=>!!v || 'Required']" :input-attrs="{ 'aria-label':'Medical Record Number' }"/>
                    </div>
                    <div class="col-12 col-md-6">
                      <q-input v-model="registrationForm.dateOfRegistration" label="Date of Registration" hint="Auto-set at opening" outlined dense readonly :input-attrs="{ 'aria-label':'Date of Registration' }"/>
                    </div>
                    <div class="col-12 col-md-6">
                      <q-input v-model="registrationForm.registeredBy" label="Registered By" hint="Your email/username" outlined dense readonly :input-attrs="{ 'aria-label':'Registered By' }"/>
                    </div>
                  </div>
                </q-slide-transition>
              </q-step>

              <q-step :name="2" title="Patient Identification" subtitle="Names, DOB, sex, status" done-icon="check">
                <q-slide-transition>
                  <div class="row q-col-gutter-md">
                    <div class="col-12 col-md-4"><q-input v-model="registrationForm.firstName" label="First Name *" outlined dense :rules="[v=>!!v || 'Required']" :input-attrs="{ 'aria-label':'First Name' }"/></div>
                    <div class="col-12 col-md-4"><q-input v-model="registrationForm.middleName" label="Middle Name" outlined dense :input-attrs="{ 'aria-label':'Middle Name' }"/></div>
                    <div class="col-12 col-md-4"><q-input v-model="registrationForm.lastName" label="Last Name *" outlined dense :rules="[v=>!!v || 'Required']" :input-attrs="{ 'aria-label':'Last Name' }"/></div>
                    <div class="col-12 col-md-4"><q-input v-model="registrationForm.dob" type="date" label="Date of Birth *" outlined dense :rules="[v=>!!v || 'Required']" :input-attrs="{ 'aria-label':'Date of Birth' }"/></div>
                    <div class="col-12 col-md-4"><q-select v-model="registrationForm.sex" :options="['Male','Female','Other']" label="Sex/Gender *" outlined dense :rules="[v=>!!v || 'Required']" :aria-label="'Sex/Gender'"/></div>
                    <div class="col-12 col-md-4"><q-select v-model="registrationForm.maritalStatus" :options="['Single','Married','Separated','Divorced','Widowed']" label="Marital Status" outlined dense :aria-label="'Marital Status'"/></div>
                    <div class="col-12 col-md-6"><q-input v-model="registrationForm.nationality" label="Nationality/Citizenship" outlined dense :input-attrs="{ 'aria-label':'Nationality/Citizenship' }"/></div>
                  </div>
                </q-slide-transition>
              </q-step>

              <q-step :name="3" title="Contact Information" subtitle="Addresses and contact numbers" done-icon="check">
                <q-slide-transition>
                  <div class="row q-col-gutter-md">
                    <div class="col-12"><q-input v-model="registrationForm.homeAddress" label="Home Address" outlined dense :input-attrs="{ 'aria-label':'Home Address' }"/></div>
                    <div class="col-12 col-md-4"><q-input v-model="registrationForm.cellPhone" label="Cell Phone *" hint="Primary mobile number" outlined dense :rules="[v=>!!v || 'Required']" :input-attrs="{ 'aria-label':'Cell Phone' }"/></div>
                    <div class="col-12 col-md-4"><q-input v-model="registrationForm.homePhone" label="Home Phone" outlined dense :input-attrs="{ 'aria-label':'Home Phone' }"/></div>
                    <div class="col-12 col-md-4"><q-input v-model="registrationForm.email" type="email" label="Email Address" hint="Valid email format" outlined dense :rules="[v=>!v || /.+@.+\..+/.test(v) || 'Invalid email']" :input-attrs="{ 'aria-label':'Email Address' }"/></div>
                    <div class="col-12 col-md-6"><q-input v-model="registrationForm.occupation" label="Occupation" outlined dense :input-attrs="{ 'aria-label':'Occupation' }"/></div>
                  </div>
                </q-slide-transition>
              </q-step>

              <q-step :name="4" title="Emergency Contact" subtitle="Primary emergency contact" done-icon="check">
                <q-slide-transition>
                  <div class="row q-col-gutter-md">
                    <div class="col-12 col-md-4"><q-input v-model="registrationForm.emergencyName" label="Contact Name *" outlined dense :rules="[v=>!!v || 'Required']" :input-attrs="{ 'aria-label':'Emergency Contact Name' }"/></div>
                    <div class="col-12 col-md-4"><q-input v-model="registrationForm.emergencyRelationship" label="Relationship to Patient *" outlined dense :rules="[v=>!!v || 'Required']" :input-attrs="{ 'aria-label':'Emergency Contact Relationship' }"/></div>
                    <div class="col-12 col-md-4"><q-input v-model="registrationForm.emergencyPhone" label="Contact Phone Number *" hint="e.g., +63 912 345 6789" outlined dense :rules="[v=>!!v || 'Required']" :input-attrs="{ 'aria-label':'Emergency Contact Phone' }"/></div>
                  </div>
                </q-slide-transition>
              </q-step>

              <template v-slot:navigation>
                <q-separator spaced/>
                <div class="row items-center justify-between q-gutter-sm">
                  <div>
                    <q-btn flat color="primary" label="Back" :disable="registrationStep===1" @click="prevStep"/>
                  </div>
                  <div>
                    <q-btn color="primary" label="Next" :disable="registrationStep===4 || !canAdvance" @click="nextStep"/>
                  </div>
                </div>
              </template>
            </q-stepper>
          </q-card-section>

          <q-card-actions align="between" class="registration-actions">
            <div class="row items-center q-gutter-sm">
              <q-icon name="save" size="18px"/>
              <span class="text-caption" v-if="draftSavedAt">Draft saved {{ draftSavedAt }}</span>
              <span class="text-caption" v-else>Draft not saved</span>
            </div>
            <div class="row q-gutter-sm">
              <q-btn flat label="Cancel" v-close-popup />
              <q-btn flat color="primary" label="Save Draft" @click="saveRegistrationDraft" />
              <q-btn color="primary" label="Save Registration" @click="saveRegistration" />
            </div>
          </q-card-actions>
        </q-card>
      </q-dialog>
      </div>
    </q-page-container>

    <!-- Send Records Dialog -->
    <q-dialog v-model="showSendDialog" persistent content-class="form-dialog-container">
      <q-card class="form-dialog-card">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Send Patient Records</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup aria-label="Close" />
        </q-card-section>
        <q-separator />
        <q-card-section>
          <q-inner-loading :showing="sendLoading">
            <q-spinner color="primary" size="32px" />
          </q-inner-loading>
          <q-select
            v-model="sendForm.doctorId"
            :options="doctorOptions"
            label="Select Doctor"
            outlined
            dense
            emit-value
            map-options
            aria-label="Select doctor to send to"
          />
          <q-input
            v-model="sendForm.message"
            type="textarea"
            label="Message (optional)"
            outlined
            dense
            autogrow
            aria-label="Message to include with records"
          />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup aria-label="Cancel" />
          <q-btn color="primary" label="Send" :loading="sendLoading" @click="confirmSend" aria-label="Confirm send" />
        </q-card-actions>
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
  </q-layout>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import { useQuasar } from 'quasar';
import { api } from 'boot/axios';
import NurseHeader from '../components/NurseHeader.vue';
import NurseSidebar from '../components/NurseSidebar.vue';

// Types
interface Patient {
  id: number;
  user_id: number;
  full_name: string;
  email: string;
  age: number | null;
  gender: string;
  blood_type: string;
  medical_condition: string;
  hospital: string;
  insurance_provider: string;
  billing_amount: number | null;
  room_number: string;
  admission_type: string;
  date_of_admission: string;
  discharge_date: string;
  medication: string;
  test_results: string;
  assigned_doctor: string | null;
  profile_picture?: string | null;
  // Provided by backend to identify analytics dummy records
  is_dummy?: boolean;
}

// Reactive data
const $q = useQuasar();
const rightDrawerOpen = ref(false);
const loading = ref(false);
const searchText = ref('');
const sortKey = ref<'full_name' | 'age' | 'gender'>('full_name');
const sortOptions = [
  { label: 'Name', value: 'full_name' },
  { label: 'Age', value: 'age' },
  { label: 'Gender', value: 'gender' },
];

// Base form options with role permissions
const allFormOptions = [
  {label: 'Select Form Type', value: '', roles: ['nurse', 'doctor']},
  { label: 'Assessment Forms', value: 'intake', roles: ['nurse', 'doctor'] },
  { label: 'Graphic Records', value: 'flow', roles: ['nurse', 'doctor'] },
  { label: 'Medication Administration Record', value: 'mar', roles: ['nurse'] },
  { label: 'Patient Education Record', value: 'education', roles: ['nurse', 'doctor'] },
  { label: 'Discharge Checklist', value: 'discharge', roles: ['nurse', 'doctor'] },
];

// Computed property for filtered form options based on user role and verification
const opdFormOptions = computed(() => {
  const userRole = userProfile.value.role;
  const isVerified = userProfile.value.verification_status === 'approved';
  
  // If user is not verified, only show the select placeholder
  if (!isVerified) {
    return [
      {label: 'Select Form Type', value: ''},
      {label: 'Verification Required', value: '', disabled: true}
    ];
  }
  
  // Filter forms based on user role
  return allFormOptions
    .filter(option => option.roles.includes(userRole))
    .map(option => ({
      label: option.label,
      value: option.value,
      disable: option.value !== '' && !option.roles.includes(userRole)
    }));
});
const sortOrder = ref<'asc' | 'desc'>('asc');
const orderOptions = [
  { label: 'Ascending', value: 'asc' },
  { label: 'Descending', value: 'desc' },
];
const patients = ref<Patient[]>([]);
const selectedPatient = ref<Patient | null>(null);
const showNotifications = ref(false);

// User profile data
const userProfile = ref<{
  full_name: string;
  specialization?: string;
  role: string;
  profile_picture: string | null;
  verification_status: string;
  hospital_name?: string;
  hospital_address?: string;
}>({
  full_name: '',
  specialization: '',
  role: '',
  profile_picture: null,
  verification_status: '',
  hospital_name: '',
  hospital_address: '',
});

// Document view dialog state
const showDocumentView = ref(false)
const selectedPatientDoc = ref<Patient | null>(null)
const department = computed(() => (userProfile.value?.specialization || '').trim() || 'Nursing')

// Notification system
const notifications = ref<
  {
    id: number;
    message: string;
    is_read: boolean;
    created_at: string;
  }[]
>([]);

// Notification interface
interface Notification {
  id: number;
  message: string;
  is_read: boolean;
  created_at: string;
}

// Computed properties
const filteredPatients = computed(() => {
  // Base: only active (not discharged) patients
  let list = patients.value.filter((p) => p.discharge_date === null || p.discharge_date === '');

  // Search filter
  if (searchText.value) {
    const search = searchText.value.toLowerCase();
    list = list.filter(
      (patient) =>
        (patient.full_name || '').toLowerCase().includes(search) ||
        (patient.medical_condition || '').toLowerCase().includes(search) ||
        (patient.hospital || '').toLowerCase().includes(search),
    );
  }

  // Sorting
  const key = sortKey.value;
  const dir = sortOrder.value === 'desc' ? -1 : 1;
  list = [...list].sort((a, b) => {
    const av = (key === 'age' ? (a.age ?? 0) : (a[key] ?? '')).toString().toLowerCase();
    const bv = (key === 'age' ? (b.age ?? 0) : (b[key] ?? '')).toString().toLowerCase();
    if (av < bv) return -1 * dir;
    if (av > bv) return 1 * dir;
    return 0;
  });

  return list;
});

const activePatientsCount = computed(
  () => patients.value.filter((p) => p.discharge_date === null || p.discharge_date === '').length,
);

// Methods
const loadPatients = async () => {
  loading.value = true;
  try {
    const response = await api.get('/users/nurse/patients/');
    if (response.data.success) {
      // Exclude any dummy patients used for analytics/demo data
      patients.value = (response.data.patients || []).filter(
        (p: Patient | Record<string, unknown>) => !(p as Patient).is_dummy,
      ) as Patient[];
      console.log('Patients loaded:', patients.value.length);
    }
  } catch (error) {
    console.error('Failed to load patients:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to load patients',
      position: 'top',
    });
  } finally {
    loading.value = false;
  }
};

const selectPatient = (patient: Patient) => {
  selectedPatient.value = patient;
  // Auto-filter archives by selected patient (User ID) and fetch
  try {
    const pid = String(patient.user_id ?? patient.id ?? '');
    // Reset non-patient archive filters to avoid form coupling
    archiveFilters.value = {
      query: '',
      patient_id: pid,
      assessment_type: '',
      medical_condition: '',
      start_date: '',
      end_date: ''
    };
    void searchArchives();
  } catch (error) {
    console.error('Error setting archive filters for patient:', error);
  }
  console.log('Selected patient:', patient);
};

const viewPatientDetails = (patient: Patient) => {
  // Open document-style view with header details
  selectedPatient.value = patient;
  selectedPatientDoc.value = patient;
  loadDemographics();
  showDocumentView.value = true;
  $q.notify({ type: 'info', message: `Viewing record for ${patient.full_name}`, position: 'top' });
};

const editPatient = (patient: Patient) => {
  selectedPatient.value = patient;
  openRegistration();
};

const fetchUserProfile = async () => {
  try {
    const response = await api.get('/users/profile/');
    const userData = response.data.user;

    userProfile.value = {
      full_name: userData.full_name,
      specialization: userData.nurse_profile?.specialization,
      role: userData.role,
      profile_picture: userData.profile_picture || null,
      verification_status: userData.verification_status,
      hospital_name: userData.hospital_name || '',
      hospital_address: userData.hospital_address || '',
    };
  } catch (error) {
    console.error('Failed to fetch user profile:', error);
    // Fallback to localStorage if API call fails
    const userLS = localStorage.getItem('user');
    if (userLS) {
      const user = JSON.parse(userLS);
      userProfile.value = {
        full_name: user.full_name,
        specialization: user.nurse_profile?.specialization,
        role: user.role,
        profile_picture: user.profile_picture || null,
        verification_status: user.verification_status,
        hospital_name: user.hospital_name || '',
        hospital_address: user.hospital_address || '',
      };
    }
  }
};

// Navigation and logout functionality handled by NurseSidebar component

// Notification functions
const loadNotifications = async (): Promise<void> => {
  try {
    console.log('📬 Loading nurse notifications...');

    const response = await api.get('/operations/notifications/');
    notifications.value = response.data || [];

    console.log('✅ Nurse notifications loaded:', notifications.value.length);
  } catch (error: unknown) {
    console.error('❌ Error loading notifications:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to load notifications',
    });
  }
};

const handleNotificationClick = (notification: Notification): void => {
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
    notifications.value.forEach((notification) => {
      notification.is_read = true;
    });

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

// Registration / Demographics gating
const showRegistrationDialog = ref(false)
const registrationCompleted = ref(false)
const registrationForm = ref({
  // Header and Administrative Data
  hospitalName: '',
  departmentName: 'OPD',
  hospitalAddress: '',
  mrn: '',
  dateOfRegistration: '',
  registeredBy: '',
  // Patient Identification Data
  firstName: '',
  middleName: '',
  lastName: '',
  dob: '',
  sex: '',
  maritalStatus: '',
  nationality: '',
  // Contact Information
  homeAddress: '',
  cellPhone: '',
  homePhone: '',
  email: '',
  occupation: '',
  // Emergency Contact Information
  emergencyName: '',
  emergencyRelationship: '',
  emergencyPhone: ''
})

// Stepper state & validation
const registrationStep = ref(1)
const draftSavedAt = ref<string | null>(null)

const requiredByStep = {
  1: ['hospitalName', 'hospitalAddress', 'mrn'],
  2: ['firstName', 'lastName', 'dob', 'sex'],
  3: ['cellPhone'],
  4: ['emergencyName', 'emergencyRelationship', 'emergencyPhone']
} as Record<number, string[]>

const isStepValid = (step: number) => {
  const r = registrationForm.value as Record<string, string>
  return (requiredByStep[step] || []).every(k => !!r[k])
}

const canAdvance = computed(() => isStepValid(registrationStep.value))

const nextStep = () => {
  if (!isStepValid(registrationStep.value)) {
    $q.notify({ type: 'warning', message: 'Please complete required fields before proceeding' })
    return
  }
  if (registrationStep.value < 4) registrationStep.value += 1
}

const prevStep = () => { if (registrationStep.value > 1) registrationStep.value -= 1 }

const saveRegistrationDraft = () => {
  if (!selectedPatient.value) { $q.notify({ type: 'negative', message: 'Select a patient first' }); return }
  const key = `patient_reg_draft_${selectedPatient.value.id}`
  const payload = { patientId: selectedPatient.value.id, ...registrationForm.value, step: registrationStep.value, savedAt: new Date().toISOString() }
  localStorage.setItem(key, JSON.stringify(payload))
  draftSavedAt.value = payload.savedAt
  $q.notify({ type: 'info', message: 'Draft saved' })
}

const loadRegistrationDraft = () => {
  if (!selectedPatient.value) return
  const key = `patient_reg_draft_${selectedPatient.value.id}`
  const raw = localStorage.getItem(key)
  if (!raw) return
  try {
    const payload = JSON.parse(raw)
    Object.assign(registrationForm.value, payload)
    if (payload.step) registrationStep.value = Number(payload.step) || 1
    draftSavedAt.value = payload.savedAt || null
  } catch { /* ignore */ }
}


const prefillRegistrationFromProfile = () => {
  try {
    // Attempt to infer nurse profile info if available with a safe type
    type MaybeUserProfile = {
      hospital_name?: string;
      hospital_address?: string;
      nurse_profile?: { department?: string };
      email?: string;
      username?: string;
    }
    const upHolder = userProfile as unknown as { value?: MaybeUserProfile | null }
    const up: MaybeUserProfile | null = upHolder?.value ?? null
    if (up) {
      registrationForm.value.hospitalName = up.hospital_name ?? ''
      registrationForm.value.hospitalAddress = up.hospital_address ?? ''
      registrationForm.value.departmentName = up.nurse_profile?.department ?? 'OPD'
      registrationForm.value.registeredBy = up.email ?? up.username ?? ''
    }
  } catch {
    // ignore
  }
}

const generateMRN = (id: number | string) => {
  const rand = Math.floor(Math.random() * 9000) + 1000
  return `MRN-${id}-${rand}`
}

const openRegistration = () => {
  if (!selectedPatient.value) { $q.notify({ type: 'warning', message: 'Select a patient first' }); return }
  // Load draft if available; otherwise prefill defaults
  type MaybePatient = { mrn?: string; id: number; full_name?: string; email?: string }
  const sp = selectedPatient.value as unknown as MaybePatient
  const draftKey = `patient_reg_draft_${sp.id}`
  if (localStorage.getItem(draftKey)) {
    loadRegistrationDraft()
  } else {
    prefillRegistrationFromProfile()
    // prefill MRN and date
    registrationForm.value.mrn = sp.mrn ?? generateMRN(sp.id)
    registrationForm.value.dateOfRegistration = new Date().toISOString()
    // prefill identity if available from patient list
    const names = (sp.full_name ?? '').trim().split(/\s+/)
    registrationForm.value.firstName = String(names[0] || '')
    registrationForm.value.lastName = String(names.length > 1 ? names[names.length - 1] : '')
    registrationForm.value.email = sp.email ?? ''
    registrationStep.value = 1
    draftSavedAt.value = null
  }
  showRegistrationDialog.value = true
}

const saveRegistration = () => {
  if (!selectedPatient.value) { $q.notify({ type: 'negative', message: 'Select a patient first' }); return }
  const r = registrationForm.value
  const required = [r.hospitalName, r.hospitalAddress, r.mrn, r.firstName, r.lastName, r.dob, r.sex, r.cellPhone, r.emergencyName, r.emergencyRelationship, r.emergencyPhone]
  if (required.some(v => !v)) { $q.notify({ type: 'warning', message: 'Please complete required registration fields' }); return }
  const key = `patient_reg_${selectedPatient.value.id}`
  const payload = { patientId: selectedPatient.value.id, ...r }
  localStorage.setItem(key, JSON.stringify(payload))
  registrationCompleted.value = true
  showRegistrationDialog.value = false
  $q.notify({ type: 'positive', message: 'Patient registration saved' })
}

const loadIntake = async () => {
  if (!selectedPatient.value) return
  try {
    const res = await api.get(`/users/nurse/patient/${selectedPatient.value.id}/intake/`)
    type ApiAllergy = { name?: string; substance?: string; reaction?: string }
    type ApiIntake = {
      vitals?: { bp?: string; hr?: number | string; rr?: number | string; temp_c?: number | string; temp?: number | string; o2_sat?: number | string }
      weight_kg?: number | string
      height_cm?: number | string
      chief_complaint?: string
      pain_score?: number | string
      allergies?: ApiAllergy[]
      mental_status?: string
      fall_risk_score?: number | string
    }
    const d = (res.data?.data as ApiIntake) || {}
    const vit = d.vitals || {}
    intakeForm.value = {
      bp: String(vit.bp || ''),
      hr: String(vit.hr ?? ''),
      rr: String(vit.rr ?? ''),
      temp: String(vit.temp_c ?? vit.temp ?? ''),
      o2: String(vit.o2_sat ?? ''),
      weight: String(d.weight_kg ?? ''),
      height: String(d.height_cm ?? ''),
      chiefComplaint: String(d.chief_complaint || ''),
      painScore: Number(d.pain_score ?? 0),
      allergies: Array.isArray(d.allergies) ? d.allergies.map((a: ApiAllergy) => ({ name: a.name ?? a.substance ?? '', reaction: a.reaction ?? '' })) : [],
      mentalStatus: String(d.mental_status || ''),
      fallRisk: String(d.fall_risk_score ?? '')
    }
  } catch (e) {
    console.warn('Failed to fetch intake', e)
    $q.notify({ type: 'warning', message: 'Unable to load intake from server' })
  }
}

const loadFlowSheet = async () => {
  if (!selectedPatient.value) return
  try {
    const res = await api.get(`/users/nurse/patient/${selectedPatient.value.id}/flow-sheets/`)
    type FlowSheetApiEntry = {
      time_of_reading?: string
      repeated_vitals?: { bp?: string; hr?: number | string; pain?: number | string }
      intake_ml?: number | string
      output_ml?: number | string
      site_checks?: string
      nursing_interventions?: string[] | string
    }
    const list: FlowSheetApiEntry[] = Array.isArray(res.data?.data) ? (res.data.data as FlowSheetApiEntry[]) : []
    flowSheetEntries.value = list.map((e: FlowSheetApiEntry) => ({
      timestamp: String(e.time_of_reading || ''),
      bp: String((e.repeated_vitals || {}).bp || ''),
      hr: String((e.repeated_vitals || {}).hr ?? ''),
      pain: Number((e.repeated_vitals || {}).pain ?? 0),
      intake: Number(e.intake_ml ?? 0),
      output: Number(e.output_ml ?? 0),
      siteCheck: String(e.site_checks || ''),
      interventions: Array.isArray(e.nursing_interventions) ? (e.nursing_interventions.join(', ')) : String(e.nursing_interventions || '')
    }))
  } catch (e) {
    console.warn('Failed to fetch flow sheets', e)
    $q.notify({ type: 'warning', message: 'Unable to load flow sheets from server' })
    flowSheetEntries.value = []
  }
}

const loadMar = async () => {
  if (!selectedPatient.value) return
  try {
    const res = await api.get(`/users/nurse/patient/${selectedPatient.value.id}/mar/`)
    type MarApiEntry = {
      datetime_administered?: string
      name?: string
      dose?: string
      route?: string
      nurse_initials?: string
      prn_reason?: string | null
      prn_response?: string | null
      withheld_reason?: string | null
    }
    const list: MarApiEntry[] = Array.isArray(res.data?.data) ? (res.data.data as MarApiEntry[]) : []
    marEntries.value = list.map((e: MarApiEntry) => ({
      datetime: String(e.datetime_administered || ''),
      medName: String(e.name || ''),
      dose: String(e.dose || ''),
      route: String(e.route || ''),
      nurseId: String(e.nurse_initials || ''),
      isPRN: Boolean(e.prn_reason || e.prn_response),
      prnReason: String(e.prn_reason || ''),
      prnResponse: String(e.prn_response || ''),
      notGiven: Boolean(e.withheld_reason),
      withheldReason: String(e.withheld_reason || '')
    }))
  } catch (e) {
    console.warn('Failed to fetch MAR', e)
    $q.notify({ type: 'warning', message: 'Unable to load MAR from server' })
    marEntries.value = []
  }
}

const loadEducation = async () => {
  if (!selectedPatient.value) return
  try {
    const res = await api.get(`/users/nurse/patient/${selectedPatient.value.id}/education/`)
    type EducationApiEntry = {
      topics?: string[]
      comprehension_level?: string
      return_demonstration?: boolean
      barriers_to_learning?: string[] | string
    }
    const list: EducationApiEntry[] = Array.isArray(res.data?.data) ? (res.data.data as EducationApiEntry[]) : []
    // Use the most recent education entry to populate form
    const latest: EducationApiEntry = list[list.length - 1] ?? {}
    educationForm.value = {
      topics: Array.isArray(latest.topics) ? latest.topics : [],
      warningSigns: '',
      comprehension: String(latest.comprehension_level || ''),
      returnDemoSuccess: Boolean(latest.return_demonstration || false),
      barriers: Array.isArray(latest.barriers_to_learning) ? latest.barriers_to_learning.join(', ') : String(latest.barriers_to_learning || '')
    }
    const savedTopics = Array.from(new Set([...(educationForm.value.topics || [])])).map(String)
    educationTopicOptions.length = 0
    educationTopicOptions.push(...savedTopics)
  } catch (e) {
    console.warn('Failed to fetch education', e)
    $q.notify({ type: 'warning', message: 'Unable to load education from server' })
  }
}

const loadDischarge = async () => {
  if (!selectedPatient.value) return
  try {
    const res = await api.get(`/users/nurse/patient/${selectedPatient.value.id}/discharge/`)
    const d = res.data?.data || {}
    const vit = d.discharge_vitals || {}
    dischargeForm.value = {
      verbalUnderstands: Boolean(d.understanding_confirmed || false),
      writtenProvided: Boolean(d.written_instructions_provided || false),
      followUpDate: '',
      followUpTime: '',
      equipmentNeeds: Array.isArray(d.equipment_needs) ? d.equipment_needs.join(', ') : String(d.equipment_needs || ''),
      finalBP: String(vit.bp || ''),
      finalHR: String(vit.hr ?? ''),
      transportationStatus: String(d.transportation_status || ''),
      nurseId: String(d.nurse_signature || ''),
      patientAcknowledged: Boolean(d.patient_acknowledgment || false)
    }
  } catch (e) {
    console.warn('Failed to fetch discharge', e)
    $q.notify({ type: 'warning', message: 'Unable to load discharge from server' })
  }
}

watch(selectedPatient, (p) => {
  registrationCompleted.value = !!(p && localStorage.getItem(`patient_reg_${p.id}`))
  if (p) {
    loadDemographics();
    void loadIntake(); void loadFlowSheet(); void loadMar(); void loadEducation(); void loadDischarge();
  } else {
    demographics.value = null
  }
})

// OPD Forms state and methods
const selectedForm = ref<'' | 'intake' | 'flow' | 'mar' | 'education' | 'discharge'>('')

// Modal state for OPD forms
const formDialogOpen = ref(false)
const currentFormTitle = computed(() => {
  switch (selectedForm.value) {
    case '': return 'Select Form Type'
    case 'intake': return 'Assessment Forms'
    case 'flow': return 'Graphic Records'
    case 'mar': return 'Medication Administration Record'
    case 'education': return 'Patient Education Record'
    case 'discharge': return 'Discharge Checklist & Summary'
    default: return 'OPD Form'
  }
})

// Demographics state and helpers
type Demographics = {
  mrn?: string; firstName?: string; middleName?: string; lastName?: string;
  dob?: string; sex?: string; maritalStatus?: string; nationality?: string;
  homeAddress?: string; cellPhone?: string; homePhone?: string; email?: string;
  emergencyName?: string; emergencyRelationship?: string; emergencyPhone?: string;
}
const demographics = ref<Demographics | null>(null)
const demoLoadError = ref<string | null>(null)
const demographicFullName = computed(() => {
  const d = demographics.value
  if (!d) return ''
  const names = [d.firstName, d.middleName, d.lastName].filter(Boolean)
  return names.join(' ').trim()
})
const formattedDOB = computed(() => {
  const dob = demographics.value?.dob
  if (!dob) return ''
  try {
    const dt = new Date(dob)
    return dt.toLocaleDateString()
  } catch { return String(dob) }
})
const demographicAge = computed(() => {
  const dob = demographics.value?.dob
  if (!dob) return ''
  try {
    const d = new Date(dob)
    const diff = Date.now() - d.getTime()
    const ageDt = new Date(diff)
    return Math.abs(ageDt.getUTCFullYear() - 1970)
  } catch { return '' }
})
const demoLoading = ref(false)
const loadDemographics = () => {
  demoLoadError.value = null
  demographics.value = null
  if (!selectedPatient.value) return
  demoLoading.value = true
  const key = `patient_reg_${selectedPatient.value.id}`
  try {
    const raw = localStorage.getItem(key)
    if (raw) {
      const p = JSON.parse(raw)
      demographics.value = { ...p }
    } else {
      // fallback to current registration form draft/completed state
      demographics.value = registrationCompleted.value ? ({ ...registrationForm.value } as Demographics) : null
    }
    if (!demographics.value) {
      demoLoadError.value = 'Demographics not found for selected patient.'
    }
  } catch (e) {
    console.warn('Failed to load demographics', e)
    demoLoadError.value = 'Unable to load demographics; showing current registration data'
    demographics.value = registrationCompleted.value ? ({ ...registrationForm.value } as Demographics) : null
  } finally {
    demoLoading.value = false
  }
}

// Open modal when a tab is selected and load relevant form data
watch(selectedForm, (val) => {
  if (val) {
    formDialogOpen.value = true
    if (selectedPatient.value) {
      switch (val) {
        case 'intake':
          void loadIntake();
          break;
        case 'flow':
          void loadFlowSheet();
          break;
        case 'mar':
          void loadMar();
          break;
        case 'education':
          void loadEducation();
          break;
        case 'discharge':
          void loadDischarge();
          break;
      }
    }
  }
})
// Refresh demographics when registration completes
watch(registrationCompleted, (val) => { if (val && selectedPatient.value) loadDemographics() })

// Intake & Assessment
const intakeForm = ref({
  bp: '', hr: '', rr: '', temp: '', o2: '', weight: '', height: '',
  chiefComplaint: '', painScore: 0,
  allergies: [] as Array<{ name: string; reaction: string }>,
  mentalStatus: '', fallRisk: ''
})
const mentalStatusOptions = [
  { label: 'Alert and Oriented', value: 'AAOx3' },
  { label: 'Disoriented', value: 'disoriented' },
  { label: 'Lethargic', value: 'lethargic' },
  { label: 'Unresponsive', value: 'unresponsive' }
]
const addAllergy = () => {
  intakeForm.value.allergies.push({ name: '', reaction: '' })
}
const removeAllergy = (idx: number) => {
  intakeForm.value.allergies.splice(idx, 1)
}
const resetIntake = () => {
  intakeForm.value = { bp: '', hr: '', rr: '', temp: '', o2: '', weight: '', height: '', chiefComplaint: '', painScore: 0, allergies: [], mentalStatus: '', fallRisk: '' }
}
const ensureDemographicsBeforeSubmit = (): boolean => {
  if (!demographics.value) { $q.notify({ type: 'warning', message: 'Load demographics before submitting the form.' }); return false }
  return true
}
const saveIntake = async () => {
  if (!selectedPatient.value) { $q.notify({ type: 'negative', message: 'Select a patient first' }); return }
  if (!ensureDemographicsBeforeSubmit()) return
  const required = [intakeForm.value.bp, intakeForm.value.hr, intakeForm.value.rr, intakeForm.value.temp, intakeForm.value.o2, intakeForm.value.weight, intakeForm.value.height, intakeForm.value.chiefComplaint, intakeForm.value.mentalStatus, intakeForm.value.fallRisk]
  if (required.some(v => !v)) { $q.notify({ type: 'warning', message: 'Please fill all required fields' }); return }
  try {
    const payload = {
      vitals: {
        bp: intakeForm.value.bp,
        hr: Number(intakeForm.value.hr),
        rr: Number(intakeForm.value.rr),
        temp_c: Number(intakeForm.value.temp),
        o2_sat: Number(intakeForm.value.o2),
      },
      weight_kg: Number(intakeForm.value.weight),
      height_cm: Number(intakeForm.value.height),
      chief_complaint: intakeForm.value.chiefComplaint,
      pain_score: Number(intakeForm.value.painScore),
      allergies: (intakeForm.value.allergies || []).map((a) => ({ substance: a.name, reaction: a.reaction })),
      current_medications: [],
      mental_status: intakeForm.value.mentalStatus,
      fall_risk_score: Number(intakeForm.value.fallRisk),
      assessed_at: new Date().toISOString(),
    }
    const res = await api.put(`/users/nurse/patient/${selectedPatient.value.id}/intake/`, payload)
    if (res.data?.success) {
      $q.notify({ type: 'positive', message: 'Intake saved to server' })
    } else {
      throw new Error(String(res.data?.errors || res.data?.error || 'Failed to save intake'))
    }
  } catch (err: unknown) {
    console.error('Save intake failed', err)
    let msg = 'Failed to save intake';
    if (typeof err === 'object' && err) {
      type ApiError = { response?: { data?: { errors?: unknown; error?: string } }; message?: string }
      const e = err as ApiError
      msg = e.response?.data?.errors ? JSON.stringify(e.response.data.errors) : (e.response?.data?.error || e.message || msg)
    }
    $q.notify({ type: 'negative', message: msg })
  }
}

// Flow Sheets
type FlowEntry = { timestamp: string; bp: string; hr: string; pain: number; intake: number; output: number; siteCheck: string; interventions: string }
const flowSheetEntries = ref<FlowEntry[]>([])
const newFlowEntry = ref<FlowEntry>({ timestamp: '', bp: '', hr: '', pain: 0, intake: 0, output: 0, siteCheck: '', interventions: '' })
const addFlowEntry = () => { flowSheetEntries.value.push({ ...newFlowEntry.value }); newFlowEntry.value = { timestamp: '', bp: '', hr: '', pain: 0, intake: 0, output: 0, siteCheck: '', interventions: '' } }
const removeFlowEntry = (idx: number) => { flowSheetEntries.value.splice(idx, 1) }
const saveFlowSheet = async () => {
  if (!selectedPatient.value) { $q.notify({ type: 'negative', message: 'Select a patient first' }); return }
  if (!ensureDemographicsBeforeSubmit()) return
  try {
    const entries = (flowSheetEntries.value || []).map((e: FlowEntry) => ({
      time_of_reading: e.timestamp,
      repeated_vitals: { bp: e.bp, hr: Number(e.hr), pain: Number(e.pain) },
      intake_ml: Number(e.intake),
      output_ml: Number(e.output),
      site_checks: e.siteCheck,
      nursing_interventions: String(e.interventions || '').split(',').map((s: string) => s.trim()).filter(Boolean),
    }))
    const res = await api.put(`/users/nurse/patient/${selectedPatient.value.id}/flow-sheets/`, entries)
    if (res.data?.success) {
      $q.notify({ type: 'positive', message: 'Flow sheets saved to server' })
    } else {
      throw new Error(String(res.data?.errors || res.data?.error || 'Failed to save flow sheets'))
    }
  } catch (err: unknown) {
    console.error('Save flow sheets failed', err)
    let msg = 'Failed to save flow sheets';
    if (typeof err === 'object' && err) {
      type ApiError = { response?: { data?: { errors?: unknown; error?: string } }; message?: string }
      const e = err as ApiError
      msg = e.response?.data?.errors ? JSON.stringify(e.response.data.errors) : (e.response?.data?.error || e.message || msg)
    }
    $q.notify({ type: 'negative', message: msg })
  }
}

// MAR
type MarEntry = { datetime: string; medName: string; dose: string; route: string; nurseId: string; isPRN: boolean; prnReason?: string; prnResponse?: string; notGiven: boolean; withheldReason?: string }
const marEntries = ref<MarEntry[]>([])
const newMarEntry = ref<MarEntry>({ datetime: '', medName: '', dose: '', route: '', nurseId: '', isPRN: false, prnReason: '', prnResponse: '', notGiven: false, withheldReason: '' })
const addMarEntry = () => {
  if (!newMarEntry.value.medName || !newMarEntry.value.dose || !newMarEntry.value.route || !newMarEntry.value.nurseId) { $q.notify({ type: 'warning', message: 'Fill medication, dose, route, and nurse ID' }); return }
  if (newMarEntry.value.isPRN && (!newMarEntry.value.prnReason || !newMarEntry.value.prnResponse)) { $q.notify({ type: 'warning', message: 'PRN requires reason and response' }); return }
  if (newMarEntry.value.notGiven && !newMarEntry.value.withheldReason) { $q.notify({ type: 'warning', message: 'Specify withheld reason' }); return }
  marEntries.value.push({ ...newMarEntry.value });
  newMarEntry.value = { datetime: '', medName: '', dose: '', route: '', nurseId: '', isPRN: false, prnReason: '', prnResponse: '', notGiven: false, withheldReason: '' }
}
const removeMarEntry = (idx: number) => { marEntries.value.splice(idx, 1) }
const saveMar = async () => {
  if (!selectedPatient.value) { $q.notify({ type: 'negative', message: 'Select a patient first' }); return }
  if (!ensureDemographicsBeforeSubmit()) return
  try {
    const entries = (marEntries.value || []).map((e: MarEntry) => ({
      datetime_administered: e.datetime,
      name: e.medName,
      dose: e.dose,
      route: e.route,
      nurse_initials: e.nurseId,
      prn_reason: e.isPRN ? e.prnReason : null,
      prn_response: e.isPRN ? e.prnResponse : null,
      withheld_reason: e.notGiven ? e.withheldReason : null,
    }))
    const res = await api.put(`/users/nurse/patient/${selectedPatient.value.id}/mar/`, entries)
    if (res.data?.success) {
      $q.notify({ type: 'positive', message: 'MAR saved to server' })
    } else {
      throw new Error(String(res.data?.errors || res.data?.error || 'Failed to save MAR'))
    }
  } catch (err: unknown) {
    console.error('Save MAR failed', err)
    let msg = 'Failed to save MAR';
    if (typeof err === 'object' && err) {
      type ApiError = { response?: { data?: { errors?: unknown; error?: string } }; message?: string }
      const e = err as ApiError
      msg = e.response?.data?.errors ? JSON.stringify(e.response.data.errors) : (e.response?.data?.error || e.message || msg)
    }
    $q.notify({ type: 'negative', message: msg })
  }
}

// Patient Education
const educationForm = ref({ topics: [] as string[], warningSigns: '', comprehension: '', returnDemoSuccess: false, barriers: '' })
// Note: Education form UI is currently omitted; data loaders persist for future wiring.
const educationTopicOptions: string[] = []

// Discharge
const dischargeForm = ref({
  verbalUnderstands: false,
  writtenProvided: false,
  followUpDate: '',
  followUpTime: '',
  equipmentNeeds: '',
  finalBP: '',
  finalHR: '',
  transportationStatus: '',
  nurseId: '',
  patientAcknowledged: false
})
const resetDischarge = () => {
  dischargeForm.value = { verbalUnderstands: false, writtenProvided: false, followUpDate: '', followUpTime: '', equipmentNeeds: '', finalBP: '', finalHR: '', transportationStatus: '', nurseId: '', patientAcknowledged: false }
}
const saveDischarge = async () => {
  if (!selectedPatient.value) { $q.notify({ type: 'negative', message: 'Select a patient first' }); return }
  const required = [dischargeForm.value.finalBP, dischargeForm.value.finalHR, dischargeForm.value.nurseId]
  if (required.some(v => !v)) { $q.notify({ type: 'warning', message: 'Fill discharge vitals and nurse ID' }); return }
  try {
    type DischargePayload = {
      discharge_vitals: { bp: string; hr: number }
      understanding_confirmed: boolean
      written_instructions_provided: boolean
      follow_up_appointments_made: boolean
      equipment_needs: string[]
      transportation_status: string
      nurse_signature: string
      patient_acknowledgment: boolean
      discharged_at?: string
    }
    const payload: DischargePayload = {
      discharge_vitals: { bp: dischargeForm.value.finalBP, hr: Number(dischargeForm.value.finalHR) },
      understanding_confirmed: Boolean(dischargeForm.value.verbalUnderstands),
      written_instructions_provided: Boolean(dischargeForm.value.writtenProvided),
      follow_up_appointments_made: Boolean(dischargeForm.value.followUpDate || dischargeForm.value.followUpTime),
      equipment_needs: String(dischargeForm.value.equipmentNeeds || '').split(',').map((s: string) => s.trim()).filter(Boolean),
      transportation_status: dischargeForm.value.transportationStatus,
      nurse_signature: dischargeForm.value.nurseId,
      patient_acknowledgment: Boolean(dischargeForm.value.patientAcknowledged),
    }
    if (payload.understanding_confirmed) {
      payload.discharged_at = new Date().toISOString()
    }
    const res = await api.put(`/users/nurse/patient/${selectedPatient.value.id}/discharge/`, payload)
    if (res.data?.success) {
      $q.notify({ type: 'positive', message: 'Discharge summary saved to server' })
    } else {
      throw new Error(String(res.data?.errors || res.data?.error || 'Failed to save discharge summary'))
    }
  } catch (err: unknown) {
    console.error('Save discharge failed', err)
    let msg = 'Failed to save discharge summary';
    if (typeof err === 'object' && err) {
      type ApiError = { response?: { data?: { errors?: unknown; error?: string } }; message?: string }
      const e = err as ApiError
      msg = e.response?.data?.errors ? JSON.stringify(e.response.data.errors) : (e.response?.data?.error || e.message || msg)
    }
    $q.notify({ type: 'negative', message: msg })
  }
}

// Doctors state and helpers
const doctorsLoading = ref(false)
const doctorsLoadError = ref<string | null>(null)
interface DoctorSummary {
  id?: string | number
  email?: string
  full_name?: string
  specialization?: string
  availability?: string
  status?: string
  hospital_name?: string
}
const availableDoctors = ref<DoctorSummary[]>([])
const doctorsCheckedAt = ref<string | null>(null)

// Derive a best-guess specialization from patient's condition for outpatient matching
function deriveSpecializationFromCondition(condition: string | null | undefined): string | null {
  const c = (condition || '').toLowerCase()
  if (!c) return null
  if (/(cardio|heart)/.test(c)) return 'Cardiology'
  if (/(neuro|brain|stroke)/.test(c)) return 'Neurology'
  if (/(pulmo|lung|asthma|copd)/.test(c)) return 'Pulmonology'
  if (/(endo|diabet)/.test(c)) return 'Endocrinology'
  if (/(renal|kidney)/.test(c)) return 'Nephrology'
  if (/(ortho|bone|fracture)/.test(c)) return 'Orthopedics'
  if (/(derma|skin)/.test(c)) return 'Dermatology'
  if (/(gastro|stomach|liver)/.test(c)) return 'Gastroenterology'
  if (/(obgyn|pregnan|gyne|women)/.test(c)) return 'Obstetrics & Gynecology'
  return 'General'
}

const nurseHospital = computed(() => (userProfile.value?.hospital_name || '') || (JSON.parse(localStorage.getItem('user') || '{}').hospital_name || ''))

const filteredAvailableDoctors = computed(() => {
  const spec = deriveSpecializationFromCondition(selectedPatient.value?.medical_condition)
  const currentHospital = nurseHospital.value
  
  return (availableDoctors.value || []).filter((d) => {
    // Hospital validation: ensure doctor is from the same hospital as the nurse
    const hospitalOk = currentHospital && d.hospital_name && 
      String(d.hospital_name).toLowerCase().trim() === String(currentHospital).toLowerCase().trim()
    
    // Specialization matching (optional - if patient has a specific condition)
    const specOk = spec ? (String(d.specialization || '').toLowerCase().includes(String(spec).toLowerCase())) : true
    
    // Availability check
    const availOk = (String(d.availability || d.status || '').toLowerCase() === 'available') || !d.availability
    
    return hospitalOk && specOk && availOk
  })
})

function getInitials(name: string): string {
  const parts = String(name).split(' ').filter(Boolean)
  const initials = parts.map((p: string) => p[0]).slice(0, 2).join('')
  return initials || 'U'
}

// Safe error message extractor to avoid 'any' casts
function getErrorMessage(e: unknown): string {
  if (e instanceof Error && typeof e.message === 'string') return e.message
  if (typeof e === 'object' && e !== null && 'message' in (e as Record<string, unknown>)) {
    const m = (e as { message?: unknown }).message
    if (typeof m === 'string') return m
  }
  try { return JSON.stringify(e) } catch { return String(e) }
}

async function loadAvailableDoctors() {
  doctorsLoading.value = true
  doctorsLoadError.value = null
  
  // Validate that nurse has hospital information
  const currentHospital = nurseHospital.value
  if (!currentHospital || currentHospital.trim() === '') {
    doctorsLoadError.value = 'Hospital information missing. Please update your profile with hospital details.'
    doctorsLoading.value = false
    availableDoctors.value = []
    return
  }
  
  try {
    // New secured endpoint returns only free doctors with timestamp and count
    const url = '/api/operations/availability/doctors/free/?include_email=true'
    const res = await api.get(url)

    type ApiDoctor = { id?: number|string; full_name?: string; specialization?: string; email?: string; availability?: string; hospital_name?: string }
    const doctors: ApiDoctor[] = Array.isArray(res.data?.doctors) ? res.data.doctors : []
    const checkedAt = String(res.data?.checked_at || '')

    availableDoctors.value = doctors.map((d) => ({
      id: d.id ?? '',
      full_name: d.full_name || 'Unknown Doctor',
      specialization: d.specialization || 'General',
      availability: d.availability || 'available',
      hospital_name: d.hospital_name || nurseHospital.value || ''
    })) as DoctorSummary[]

    // Cache for fallback use with timestamp
    localStorage.setItem('available_doctors', JSON.stringify(availableDoctors.value))
    if (checkedAt) {
      localStorage.setItem('available_doctors_checked_at', checkedAt)
      doctorsCheckedAt.value = checkedAt
    }
  } catch (err) {
    console.error('Failed to fetch doctors:', err)
    const msg = getErrorMessage(err)
    doctorsLoadError.value = msg || 'Unable to load doctors from your hospital'
    
    // Try to use cached data as fallback
    try {
      const cached = localStorage.getItem('available_doctors')
      if (cached) {
        availableDoctors.value = JSON.parse(cached) as DoctorSummary[]
        console.log(`Using cached doctors: ${availableDoctors.value.length} available`)
      } else {
        availableDoctors.value = []
      }
      const cachedTs = localStorage.getItem('available_doctors_checked_at')
      doctorsCheckedAt.value = cachedTs || null
    } catch {
      availableDoctors.value = []
    }
  } finally {
    doctorsLoading.value = false
  }
}

// Send dialog state and handlers
const showSendDialog = ref(false)
const sendLoading = ref(false)
const sendForm = ref<{ doctorId: string | null; message: string }>({ doctorId: null, message: '' })
const selectedPatientForSend = ref<PatientSummary | null>(null)

// Real-time availability polling handle
// polling interval id stored for cleanup (currently unused)
let doctorPoller: number | null = null

const doctorOptions = computed(() => (filteredAvailableDoctors.value || []).map(d => ({
  label: `${d.full_name}${d.specialization ? ' — ' + d.specialization : ''}`,
  value: d.id
})))

interface PatientSummary {
  id: number | string;
  user_id?: number | string;
  full_name?: string | null;
  profile_picture?: string | null;
  age?: number | null;
  gender?: string | null;
  blood_type?: string | null;
  medical_condition?: string | null;
  email?: string | null;
  hospital?: string | null;
  insurance_provider?: string | null;
}

function sendPatientRecords(patient: PatientSummary) {
  selectedPatientForSend.value = patient
  if (!availableDoctors.value.length) { void loadAvailableDoctors() }
  // If filtered list has a single match, preselect it
  const docs = filteredAvailableDoctors.value
  if (docs.length === 1) {
    const first = docs[0]
    sendForm.value.doctorId = first && first.id != null ? String(first.id) : null
  }
  showSendDialog.value = true
}

async function confirmSend() {
  if (!selectedPatientForSend.value) { $q.notify({ type: 'warning', message: 'No patient selected' }); return }
  if (!sendForm.value.doctorId) { $q.notify({ type: 'warning', message: 'Please select a doctor' }); return }
  sendLoading.value = true
  try {
    const rawPatient = selectedPatientForSend.value as unknown as { user_id?: number | string; id: number | string; medical_condition?: string | null };
    const patientUserIdNum = Number(rawPatient.user_id ?? rawPatient.id);
    if (!Number.isFinite(patientUserIdNum)) {
      throw new Error('Invalid patient user ID');
    }
    const patientProfileIdNum = Number(rawPatient.id ?? rawPatient.user_id);
    if (!Number.isFinite(patientProfileIdNum)) {
      throw new Error('Invalid patient profile ID');
    }
    const doctorIdNum = Number(sendForm.value.doctorId);
    if (!Number.isFinite(doctorIdNum)) {
      throw new Error('Invalid doctor ID');
    }
    const specialization = deriveSpecializationFromCondition(rawPatient.medical_condition) || 'General';
    await api.post('/operations/assign-patient/', {
      patient_id: patientUserIdNum,
      doctor_id: doctorIdNum,
      specialization,
    })
    $q.notify({ type: 'positive', message: 'Patient assigned to doctor' })

    // Build record bundle to transmit (prefer saved intake snapshot)
    let intakePayload: unknown = null;
    try {
      const raw = localStorage.getItem(`opd_forms_${patientProfileIdNum}_intake`);
      intakePayload = raw ? JSON.parse(raw) : { ...intakeForm.value };
    } catch {
      intakePayload = { ...intakeForm.value };
    }
    const recordBundle = {
      kind: 'intake',
      at: new Date().toISOString(),
      patientId: patientProfileIdNum,
      demographics: demographics.value,
      intake: intakePayload,
      message: sendForm.value.message || ''
    };

    // Transmit securely to the selected doctor
    await sendSecureToDoctor({ patientId: patientProfileIdNum, doctorId: doctorIdNum, recordJson: JSON.stringify(recordBundle) });
    $q.notify({ type: 'positive', message: 'Secure record transmitted to doctor' })

    // Verify persistence and mapping for this assignment
    try {
      const resp = await api.get(`/operations/verification-status/?patient_id=${patientUserIdNum}&doctor_id=${doctorIdNum}`);
      const counts = resp.data?.persistence ?? {};
      $q.notify({ type: 'info', message: `Verification: assignments ${counts.assignments_count ?? 0}, archives ${counts.archives_count ?? 0}` });
      void api.post('/operations/client-log/', {
        level: 'info',
        message: 'nurse verification fetched',
        route: 'NursePatientAssessment',
        context: { patient_id: patientUserIdNum, doctor_id: doctorIdNum, counts },
      });
    } catch (verr) {
      console.warn('Verification check failed', verr);
      void api.post('/operations/client-log/', {
        level: 'warning',
        message: 'nurse verification failed',
        route: 'NursePatientAssessment',
        context: { patient_id: patientUserIdNum, doctor_id: doctorIdNum, error: String(verr) },
      });
    }

    showSendDialog.value = false
    sendForm.value = { doctorId: null, message: '' }
    selectedPatientForSend.value = null
  } catch (err: unknown) {
    console.error('Assignment or transmission failed', err)
    let msg = 'Failed to assign patient';
    if (typeof err === 'object' && err !== null) {
      const e = err as { response?: { data?: { error?: unknown } }, message?: unknown };
      const apiMsg = e.response?.data?.error;
      if (typeof apiMsg === 'string' && apiMsg.trim()) {
        msg = apiMsg;
      } else if (typeof e.message === 'string' && e.message.trim()) {
        msg = e.message;
      }
    } else if (typeof err === 'string' && err.trim()) {
      msg = err;
    }
    $q.notify({ type: 'negative', message: msg })
    void api.post('/operations/client-log/', {
      level: 'error',
      message: 'nurse assign/transmit failed',
      route: 'NursePatientAssessment',
      context: { error: String(err), patient_id: selectedPatientForSend.value?.id ?? null, doctor_id: sendForm.value.doctorId },
    });
  } finally { sendLoading.value = false }
}

// Removed developer-only dummy assignment helper; switching to real API-driven data

// Archive action
function archivePatient(patient: PatientSummary) {
  // Prevent archiving while patient is in active forms
  if (selectedPatient.value?.id === patient.id && formDialogOpen.value) {
    $q.notify({ type: 'warning', message: 'Close active forms before archiving this patient.' });
    return;
  }
  $q.dialog({ title: 'Archive Patient Records', message: `Archive records for ${patient.full_name}?`, cancel: true, ok: 'Archive' })
    .onOk(() => {
      void (async () => {
        try {
          // Backend expects patient_id to be the User ID; fallback to profile id if needed
          await api.post('/operations/archives/create/', { patient_id: patient.user_id ?? patient.id })
          // Remove from active patients list immediately
          patients.value = patients.value.filter(p => p.id !== patient.id)
          // Clear selection if this patient was selected
          if (selectedPatient.value?.id === patient.id) { selectedPatient.value = null }
          $q.notify({ type: 'positive', message: 'Patient archived' })
          void searchArchives()
        } catch (err) {
          console.error('Archive failed', err)
          $q.notify({ type: 'negative', message: 'Failed to archive patient' })
        }
      })()
    })
}

// Patient Archive state and methods
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

const buildArchiveParams = (): Record<string, string> => {
  const params: Record<string, string> = {}
  const f = archiveFilters.value
  // Map to backend expected parameter names
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

const resetArchiveFilters = () => {
  archiveFilters.value = { query: '', patient_id: '', assessment_type: '', medical_condition: '', start_date: '', end_date: '' }
  archivedRecords.value = []
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
    a.download = 'patient_archives.json'
    a.click()
    URL.revokeObjectURL(url)
    $q.notify({ type: 'positive', message: 'Archives exported', position: 'top' })
  } catch (err) {
    console.error('Export failed:', err)
    $q.notify({ type: 'negative', message: 'Export failed', position: 'top' })
  }
}

onMounted(() => {
  console.log('🚀 NursePatientAssessment component mounted');
  void fetchUserProfile();
  void loadNotifications();
  void loadPatients();
  void loadAvailableDoctors();

  // Refresh notifications every 30 seconds
  setInterval(() => void loadNotifications(), 30000);
  // Poll doctor availability every 10 seconds to keep list fresh
  doctorPoller = window.setInterval(() => { void loadAvailableDoctors() }, 10000)
});
onUnmounted(() => {
  if (doctorPoller !== null) {
    window.clearInterval(doctorPoller);
    doctorPoller = null;
  }
});

// Secure medical record transmission helpers
const bufferToBase64 = (buf: ArrayBuffer): string => {
  const bytes = new Uint8Array(buf)
  let binary = ''
  for (const b of bytes) binary += String.fromCharCode(b)
  return btoa(binary)
}
const base64ToBuffer = (b64: string): ArrayBuffer => {
  const binary = atob(b64)
  const bytes = new Uint8Array(binary.length)
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i)
  return bytes.buffer
}
const getDoctorPublicKey = async (doctorId: number): Promise<string> => {
  const { data } = await api.get(`/operations/secure/doctor-public-key/${doctorId}/`)
  return data.public_key_pem as string
}
const generateAesKey = async (): Promise<CryptoKey> => {
  return await window.crypto.subtle.generateKey({ name: 'AES-GCM', length: 256 }, true, ['encrypt', 'decrypt'])
}
const exportRawKeyB64 = async (key: CryptoKey): Promise<string> => {
  const raw = await window.crypto.subtle.exportKey('raw', key)
  return bufferToBase64(raw)
}
const encryptRecord = async (jsonStr: string, aesKey: CryptoKey): Promise<{ ciphertext_b64: string; iv_b64: string }> => {
  const iv = window.crypto.getRandomValues(new Uint8Array(12))
  const enc = new TextEncoder().encode(jsonStr)
  const ct = await window.crypto.subtle.encrypt({ name: 'AES-GCM', iv }, aesKey, enc)
  return { ciphertext_b64: bufferToBase64(ct), iv_b64: bufferToBase64(iv.buffer) }
}
const sha256Hex = async (str: string): Promise<string> => {
  const enc = new TextEncoder().encode(str)
  const digest = await window.crypto.subtle.digest('SHA-256', enc)
  const bytes = new Uint8Array(digest)
  return Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('')
}
const generateSigningKeyPair = async () => {
  return await window.crypto.subtle.generateKey({ name: 'ECDSA', namedCurve: 'P-256' }, true, ['sign', 'verify'])
}
const exportSpkiPem = async (publicKey: CryptoKey): Promise<string> => {
  const spki = await window.crypto.subtle.exportKey('spki', publicKey)
  const b64 = bufferToBase64(spki)
  const lines = b64.match(/.{1,64}/g)?.join('\n') || b64
  return `-----BEGIN PUBLIC KEY-----\n${lines}\n-----END PUBLIC KEY-----`
}
const signPayloadB64 = async (priv: CryptoKey, dataBuffer: ArrayBuffer): Promise<string> => {
  const sig = await window.crypto.subtle.sign({ name: 'ECDSA', hash: 'SHA-256' }, priv, dataBuffer)
  return bufferToBase64(sig)
}
const importRsaFromPem = async (pem: string): Promise<CryptoKey> => {
  const pemBody = pem.replace('-----BEGIN PUBLIC KEY-----', '').replace('-----END PUBLIC KEY-----', '').replace(/\n/g, '')
  const der = base64ToBuffer(pemBody)
  return await window.crypto.subtle.importKey('spki', der, { name: 'RSA-OAEP', hash: 'SHA-256' }, true, ['encrypt'])
}
const encryptSessionKeyWithDoctorRSA = async (doctorPublicPem: string, rawKeyB64: string): Promise<string> => {
  const rsaPub = await importRsaFromPem(doctorPublicPem)
  const raw = base64ToBuffer(rawKeyB64)
  const encrypted = await window.crypto.subtle.encrypt({ name: 'RSA-OAEP' }, rsaPub, raw)
  return bufferToBase64(encrypted)
}

const sendSecureToDoctor = async (args: { patientId: number; doctorId: number; recordJson: string }) => {
  const { patientId, doctorId, recordJson } = args
  try {
    if (!patientId || !doctorId || !recordJson) {
      $q.notify({ type: 'negative', message: 'Missing required fields', position: 'top' })
      return
    }
    const doctorPublicPem = await getDoctorPublicKey(doctorId)
    const aesKey = await generateAesKey()
    const rawKeyB64 = await exportRawKeyB64(aesKey)
    const { ciphertext_b64, iv_b64 } = await encryptRecord(recordJson, aesKey)
    const checksum_hex = await sha256Hex(recordJson)
    const signingKeys = await generateSigningKeyPair()
    const dataBuf = base64ToBuffer(ciphertext_b64)
    const signature_b64 = await signPayloadB64(signingKeys.privateKey, dataBuf)
    const signing_public_key_pem = await exportSpkiPem(signingKeys.publicKey)
    const encrypted_key_b64 = await encryptSessionKeyWithDoctorRSA(doctorPublicPem, rawKeyB64)

    const confirmSend = (): Promise<boolean> => {
      return new Promise((resolve) => {
        $q.dialog({
          title: 'Confirm Send',
          message: "We’re preparing to send your health information to your doctor. This may include visit notes and test results. Do you want to continue?",
          cancel: true,
          ok: { label: 'Send' }
        })
        .onOk(() => resolve(true))
        .onCancel(() => resolve(false))
        .onDismiss(() => {})
      })
    }

    const confirmed = await confirmSend()
    if (!confirmed) return

    const payload = {
      receiver_id: doctorId,
      patient_id: patientId,
      ciphertext_b64,
      iv_b64,
      encrypted_key_b64,
      signature_b64,
      signing_public_key_pem,
      checksum_hex,
      encryption_alg: 'AES-256-GCM',
      signature_alg: 'ECDSA-P256-SHA256'
    }
    const maxRetries = 3
    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        await api.post('/operations/secure/transmissions/', payload)
        $q.notify({ type: 'positive', message: 'Secure transmission sent', position: 'top' })
        break
      } catch (err: unknown) {
        if (attempt === maxRetries - 1) {
          let msg = 'Failed to send secure transmission'
          let backendErr: unknown = null
          if (typeof err === 'object' && err !== null) {
            const e = err as { response?: { data?: { error?: unknown } }, message?: unknown }
            backendErr = e.response?.data?.error
            const apiMsg = e.response?.data?.error
            if (typeof apiMsg === 'string' && apiMsg.trim()) msg = apiMsg
            else if (typeof e.message === 'string' && e.message.trim()) msg = e.message
          }
          $q.notify({ type: 'negative', message: msg, position: 'top' })
          // Client-side diagnostic log
          void api.post('/operations/client-log/', {
            level: 'error',
            message: 'secure transmission failed',
            route: 'NursePatientAssessment',
            context: {
              error: typeof backendErr === 'string' ? backendErr : String(msg),
              patient_id: patientId,
              doctor_id: doctorId,
              fields_present: Object.entries(payload).filter((entry) => Boolean(entry[1])).map((entry) => entry[0])
            }
          })
          break
        }
        await new Promise(r => setTimeout(r, 500 * Math.pow(2, attempt + 1)))
      }
    }
  } catch (err) {
    console.error('Secure send error:', err)
    $q.notify({ type: 'negative', message: 'Secure send error', position: 'top' })
  }
}

//await sendSecureToDoctor({ patientId: selectedPatient!.id, doctorId: selectedDoctorId, recordJson: JSON.stringify(intakeForm) })
</script>

<style scoped>
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
  background: #ffffff;
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
  background: #ffffff;
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
  margin-bottom: 30px;
}

.greeting-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
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

/* Selected patient highlight */
.patient-card.selected {
  border: 2px solid #286660;
  background: rgba(40, 102, 96, 0.08);
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

/* Loading and Empty States */
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

/* Avatar Initials Styles */
.avatar-initials {
  font-size: 18px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
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
.registration-form { padding-left: 2rem; padding-right: 2rem; }
.registration-form .q-field { margin-bottom: 14px; }

/* Registration dialog visual containment */
.registration-dialog-card {
  max-height: 80vh;
  overflow-y: auto;
  background: #ffffff;
  margin-left: 2rem;
  margin-right: 2rem;
}

/* Stepper tabs sizing for clarity */
.q-stepper--horizontal .q-stepper__tab { padding: 6px 8px; }

/* Slightly darken backdrop to avoid background card bleed-through */
.q-dialog__backdrop {
  background: rgba(0, 0, 0, 0.35) !important;
}

/* Responsive tweaks */
@media (max-width: 768px) {
  .registration-dialog-card { margin-left: 1rem; margin-right: 1rem; }
  .registration-form { padding-left: 1rem; padding-right: 1rem; }
  .registration-form .q-field { margin-bottom: 12px; }
}

@media (min-width: 1280px) {
  .registration-dialog-card { margin-left: 3rem; margin-right: 3rem; }
  .registration-form { padding-left: 3rem; padding-right: 3rem; }
}
.full-width-tabs { width: 100%; }
.form-dialog-container { z-index: 2050; }
.form-dialog-card { width: 90vw; max-width: 1000px; background: #ffffff; margin-left: 16px; margin-right: 16px; }
.form-dialog-card .q-card-section { padding: 20px; }
.form-dialog-card .row { align-items: flex-start; }
.form-dialog-card :deep(.q-field) { margin-bottom: 12px; }
@media (max-width: 768px) { .form-dialog-card { width: 95vw; max-width: 95vw; margin-left: 12px; margin-right: 12px; } }
@media (min-width: 1280px) { .form-dialog-card { max-width: 1100px; margin-left: 24px; margin-right: 24px; } }
.forms-card { background: #ffffff; }

/* Section spacing for consistent vertical gaps */
.section-spacing {
  margin-bottom: 20px;
}

/* Responsive section spacing */
@media (max-width: 768px) {
  .section-spacing {
    margin-bottom: 16px;
  }
}

@media (min-width: 1280px) {
  .section-spacing {
    margin-bottom: 24px;
  }
}
</style>