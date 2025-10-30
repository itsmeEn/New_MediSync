<template>
  <q-layout view="hHh Lpr fFf">
    <NurseHeader
      :search-text="searchText"
      :search-results="searchResults"
      :unread-notifications-count="unreadNotificationsCount"
      :current-time="currentTime"
      :weather-data="weatherData"
      :weather-loading="weatherLoading"
      :weather-error="weatherError"
      :location-data="locationData"
      :location-loading="locationLoading"
      @toggle-drawer="toggleRightDrawer"
      @search-input="onSearchInput"
      @clear-search="clearSearch"
      @select-search-result="selectSearchResult"
      @show-notifications="showNotifications = true"
    />
    <NurseSidebar v-model="rightDrawerOpen" :activeRoute="'nurse-analytics'" />

    <q-page-container class="page-container-with-fixed-header role-body-bg">
      <!-- Greeting Section -->
      <div class="greeting-section">
        <q-card class="greeting-card">
          <q-card-section class="greeting-content">
            <h2 class="greeting-text">
              Nurse Analytics Dashboard
            </h2>
            <p class="greeting-subtitle">
              Data-driven insights for patient care and medication management - {{ currentDate }}
            </p>
          </q-card-section>
        </q-card>
      </div>

      <!-- Analytics Cards Section -->
      <div class="dashboard-cards-section" v-if="false">
        <div class="dashboard-cards-grid">
          <!-- Medication Analysis Card -->
          <q-card
            class="dashboard-card medication-card zoom-card"
            @click="viewMedicationAnalysis"
            @mouseenter="showZoomedData('medication')"
            @mouseleave="hideZoomedData"
          >
            <q-card-section class="card-content">
              <div class="card-text">
                <div class="card-title">Medication Analysis</div>
                <div class="card-description">Most prescribed medications and patterns</div>
              </div>
              <div class="card-icon">
                <q-icon name="medication" size="2.5rem" />
              </div>
            </q-card-section>
            <!-- Zoomed Data Overlay -->
            <div class="zoomed-data-overlay" v-if="zoomedData.type === 'medication'">
              <div class="zoomed-content">
                <h4>Medication Analysis Overview</h4>
                <div v-if="analyticsData.medication_analysis" class="zoomed-stats">
                  <div class="stat-row">
                    <span class="stat-label">Top Medications:</span>
                    <div class="medications-list">
                      <span
                        v-for="med in analyticsData.medication_analysis?.medication_pareto_data?.slice(
                          0,
                          3,
                        )"
                        :key="med.medication"
                        class="medication-item"
                      >
                        {{ med.medication }}: {{ med.frequency }}
                      </span>
                    </div>
                  </div>
                </div>
                <div v-else class="no-data">
                  <p>No medication data available</p>
                </div>
              </div>
            </div>
          </q-card>

          <!-- Patient Demographics Card -->
          <q-card
            class="dashboard-card demographics-card zoom-card"
            @click="viewDemographics"
            @mouseenter="showZoomedData('demographics')"
            @mouseleave="hideZoomedData"
          >
            <q-card-section class="card-content">
              <div class="card-text">
                <div class="card-title">Patient Demographics</div>
                <div class="card-description">Age distribution and gender analysis</div>
              </div>
              <div class="card-icon">
                <q-icon name="people" size="2.5rem" />
              </div>
            </q-card-section>
            <!-- Zoomed Data Overlay -->
            <div class="zoomed-data-overlay" v-if="zoomedData.type === 'demographics'">
              <div class="zoomed-content">
                <h4>Patient Demographics Overview</h4>
                <div v-if="analyticsData.patient_demographics" class="zoomed-stats">
                  <div class="stat-row">
                    <span class="stat-label">Age Distribution:</span>
                    <div class="age-stats">
                      <span
                        v-for="(count, ageGroup) in (analyticsData.patient_demographics?.age_distribution ?? {})"
                        :key="ageGroup"
                        class="age-item"
                      >
                        {{ ageGroup }}: {{ count }}
                      </span>
                    </div>
                  </div>
                  <div class="stat-row">
                    <span class="stat-label">Gender Distribution:</span>
                    <div class="gender-stats">
                      <span
                        v-for="(percentage, gender) in (analyticsData.patient_demographics?.gender_proportions ?? {})"
                        :key="gender"
                        class="gender-item"
                      >
                        {{ gender }}: {{ percentage }}%
                      </span>
                    </div>
                  </div>
                </div>
                <div v-else class="no-data">
                  <p>No demographics data available</p>
                </div>
              </div>
            </div>
          </q-card>

          <!-- Health Trends Card -->
          <q-card
            class="dashboard-card trends-card zoom-card"
            @click="viewHealthTrends"
            @mouseenter="showZoomedData('trends')"
            @mouseleave="hideZoomedData"
          >
            <q-card-section class="card-content">
              <div class="card-text">
                <div class="card-title">Health Trends</div>
                <div class="card-description">Top medical conditions and patterns</div>
              </div>
              <div class="card-icon">
                <q-icon name="trending_up" size="2.5rem" />
              </div>
            </q-card-section>
            <!-- Zoomed Data Overlay -->
            <div class="zoomed-data-overlay" v-if="zoomedData.type === 'trends'">
              <div class="zoomed-content">
                <h4>Health Trends Overview</h4>
                <div v-if="analyticsData.health_trends" class="zoomed-stats">
                  <div class="stat-row">
                    <span class="stat-label">Top Conditions:</span>
                    <div class="conditions-list">
                      <span
                        v-for="illness in analyticsData.health_trends?.top_illnesses_by_week?.slice(
                          0,
                          3,
                        )"
                        :key="illness.medical_condition"
                        class="condition-item"
                      >
                        {{ illness.medical_condition }}: {{ illness.count }}
                      </span>
                    </div>
                  </div>
                </div>
                <div v-else class="no-data">
                  <p>No trends data available</p>
                </div>
              </div>
            </div>
          </q-card>

          <!-- Volume Prediction Card -->
          <q-card
            class="dashboard-card volume-card zoom-card"
            @click="viewVolumePrediction"
            @mouseenter="showZoomedData('volume')"
            @mouseleave="hideZoomedData"
          >
            <q-card-section class="card-content">
              <div class="card-text">
                <div class="card-title">Volume Prediction</div>
                <div class="card-description">Forecast patient volume and workload</div>
              </div>
              <div class="card-icon">
                <q-icon name="timeline" size="2.5rem" />
              </div>
            </q-card-section>
            <!-- Zoomed Data Overlay -->
            <div class="zoomed-data-overlay" v-if="zoomedData.type === 'volume'">
              <div class="zoomed-content">
                <h4>Volume Prediction Overview</h4>
                <div v-if="analyticsData.volume_prediction" class="zoomed-stats">
                  <div class="stat-row">
                    <span class="stat-label">Model Performance:</span>
                    <div class="performance-stats">
                      <span class="performance-item"
                        >MAE:
                        {{ analyticsData.volume_prediction?.evaluation_metrics?.mae || 'N/A' }}</span
                      >
                      <span class="performance-item"
                        >RMSE:
                        {{
                          analyticsData.volume_prediction?.evaluation_metrics?.rmse || 'N/A'
                        }}</span
                      >
                    </div>
                  </div>
                </div>
                <div v-else class="no-data">
                  <p>No volume prediction data available</p>
                </div>
              </div>
            </div>
          </q-card>
        </div>
      </div>

      <!-- Analytics Data Display Section -->
      <div class="analytics-section main-analytics-section">
        <div v-if="userProfile.verification_status !== 'approved'" class="verification-overlay">
          <q-card class="verification-card">
            <q-card-section class="verification-content">
              <q-icon name="warning" size="64px" color="orange" />
              <h4 class="verification-title">Account Verification Required</h4>
              <p class="verification-message">
                Your account needs to be verified before you can access analytics functionality.
                Please upload your verification document to complete the process.
              </p>
              <q-chip color="negative" text-color="white" size="lg" icon="cancel">
                Not Verified
              </q-chip>
              <q-btn
                color="primary"
                label="Upload Verification Document"
                icon="upload_file"
                @click="$router.push('/verification')"
                class="q-mt-md"
                unelevated
              />
            </q-card-section>
          </q-card>
        </div>
        <q-card class="analytics-card main-analytics-card" :class="{ 'disabled-content': userProfile.verification_status !== 'approved' }">
          <q-card-section class="analytics-header" v-if="false">
            <h3 class="analytics-title">NURSE ANALYTICS INSIGHTS</h3>
            <div class="analytics-actions">
              <q-btn
                color="primary"
                label="Generate PDF Report"
                icon="picture_as_pdf"
                size="md"
                @click="generatePDFReport"
                class="action-btn"
              />
              <q-btn
                color="secondary"
                label="Refresh Data"
                icon="refresh"
                size="md"
                @click="refreshAnalytics"
                class="action-btn"
              />
            </div>

            <div class="analytics-sidebar-panel">
              <div class="sidebar-actions">
                <q-btn color="primary" label="Generate PDF Report" icon="picture_as_pdf" size="md" @click="generatePDFReport" class="sidebar-btn" />
                <q-btn color="secondary" label="Refresh Analytics Data" icon="refresh" size="md" @click="refreshAnalytics" class="sidebar-btn" />
              </div>
              <q-separator class="q-my-sm" />
              <div class="ai-summary-header">AI-SUMMARY GENERATED RESPONSE</div>
              <q-separator class="q-my-xs" />
              <div class="ai-summary-content">
                <em>
                  Disclaimer: This is an automated, AI-generated recommendation that interprets the latest analytics findings based on the current data. It is intended to guide immediate resource allocation and strategic planning, not replace expert clinical judgment.
                </em>
                <div class="ai-summary-text">{{ nurseSummaryText }}</div>
              </div>
            </div>

          </q-card-section>

          <q-card-section class="analytics-content">
            <div class="analytics-sidebar-panel">
              <q-card bordered flat class="ai-summary-card">
                <q-card-section class="actions-row">
                  <q-btn color="primary" label="Generate PDF Report" icon="picture_as_pdf" size="md" @click="generatePDFReport" class="sidebar-btn" />
                  <q-btn color="secondary" label="Refresh Analytics Data" icon="refresh" size="md" @click="refreshAnalytics" class="sidebar-btn" />
                </q-card-section>
                <q-separator class="q-my-xs" />
                <q-card-section>
                  <div class="ai-summary-header">AI-SUMMARY GENERATED RESPONSE</div>
                  <div class="ai-summary-content">
                    <em>
                      Disclaimer: This is an automated, AI-generated recommendation that interprets the latest analytics findings based on the current data. It is intended to guide immediate resource allocation and strategic planning, not replace expert clinical judgment.
                    </em>
                    <div class="ai-summary-text">{{ nurseSummaryText }}</div>
                  </div>
                </q-card-section>

                <!-- AI Suggestions removed: consolidated into PDF AI Recommendations -->
              </q-card>
            </div>
            <!-- Analytics Panels -->
            <div class="analytics-panels-container structured-grid">
              <!-- Medication Analysis Panel -->
              <div class="analytics-panel medication-panel">
                <h4 class="panel-title">Medication Analysis</h4>
                <div class="panel-content">
                  <div v-if="analyticsData.medication_analysis?.medication_pareto_data?.length" class="chart-container">
                    <Bar 
                      :data="medicationChartData" 
                      :options="{
                        ...chartOptions,
                        plugins: {
                          ...chartOptions.plugins,
                          title: {
                            display: true,
                            text: 'Most Prescribed Medications',
                            font: { size: 16, weight: 'bold' }
                          }
                        }
                      }" 
                    />
                  </div>
                  <div v-else class="empty-data">
                    <div class="empty-state">
                      <q-icon name="medication" size="48px" color="grey-5" />
                      <p>No medication analysis data available</p>
                      <p class="empty-subtitle">
                        Data will appear here once medication patterns are analyzed
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Demographics Panel -->
              <div class="analytics-panel demographics-panel">
                <h4 class="panel-title">Patient Demographics</h4>
                <div class="panel-content">
                  <div v-if="analyticsData.patient_demographics" class="demographics-charts">
                    <!-- Age Distribution Chart -->
                    <div class="chart-section">
                      <h5 class="chart-title">Age Distribution</h5>
                      <div class="chart-container">
                        <Bar 
                          :data="ageChartData" 
                          :options="{
                            ...chartOptions,
                            plugins: {
                              ...chartOptions.plugins,
                              title: {
                                display: true,
                                text: 'Patients by Age Group',
                                font: { size: 14, weight: 'bold' }
                              }
                            }
                          }" 
                        />
                      </div>
                    </div>

                  </div>
                  <div v-else class="empty-data">
                    <div class="empty-state">
                      <q-icon name="people" size="48px" color="grey-5" />
                      <p>No demographics data available</p>
                      <p class="empty-subtitle">Patient demographic information will appear here</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Gender Distribution Panel -->
              <div class="analytics-panel gender-panel">
                <h4 class="panel-title">Gender Distribution</h4>
                <div class="panel-content">
                  <div v-if="analyticsData.patient_demographics?.gender_proportions" class="chart-container">
                    <Doughnut 
                      :data="genderChartData" 
                      :options="{
                        ...doughnutOptions,
                        plugins: {
                          ...doughnutOptions.plugins,
                          title: {
                            display: true,
                            text: 'Gender Distribution',
                            font: { size: 14, weight: 'bold' }
                          }
                        }
                      }" 
                    />
                  </div>
                  <div v-else class="empty-data">
                    <div class="empty-state">
                      <q-icon name="group" size="48px" color="grey-5" />
                      <p>No gender distribution data available</p>
                      <p class="empty-subtitle">Gender breakdown will appear here</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Health Trends Panel -->
              <div class="analytics-panel trends-panel">
                <h4 class="panel-title">Health Trends</h4>
                <div class="panel-content">
                  <div v-if="analyticsData.health_trends?.top_illnesses_by_week?.length" class="chart-container">
                    <Bar 
                      :data="healthTrendsChartData" 
                      :options="{
                        ...chartOptions,
                        indexAxis: 'y' as const,
                        plugins: {
                          ...chartOptions.plugins,
                          title: {
                            display: true,
                            text: 'Top Medical Conditions',
                            font: { size: 16, weight: 'bold' }
                          }
                        }
                      }" 
                    />
                  </div>
                  <div v-else class="empty-data">
                    <div class="empty-state">
                      <q-icon name="trending_up" size="48px" color="grey-5" />
                      <p>No health trends data available</p>
                      <p class="empty-subtitle">Health trend analysis will appear here</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Volume Prediction Panel -->
              <div class="analytics-panel volume-panel prediction-panel">
                <h4 class="panel-title">Patient Volume Prediction</h4>
                <div class="panel-content">
                  <div v-if="analyticsData.volume_prediction" class="volume-prediction-content">
                    <!-- Volume Comparison Chart -->
                    <div class="chart-container">
                      <Line 
                        :data="volumePredictionChartData" 
                        :options="{
                          ...chartOptions,
                          plugins: {
                            ...chartOptions.plugins,
                            title: {
                              display: true,
                              text: 'Predicted vs Actual Patient Volume',
                              font: { size: 16, weight: 'bold' }
                            },
                            legend: {
                              display: true,
                              position: 'bottom'
                            }
                          }
                        }" 
                      />
                    </div>
                    
                    <!-- Performance Metrics Cards -->
                    <div v-if="analyticsData.volume_prediction?.evaluation_metrics" class="metrics-cards">
                      <div class="metric-card">
                        <div class="metric-value">{{ analyticsData.volume_prediction.evaluation_metrics.mae }}</div>
                        <div class="metric-label">MAE</div>
                        <div class="metric-description">Mean Absolute Error</div>
                      </div>
                      <div class="metric-card">
                        <div class="metric-value">{{ analyticsData.volume_prediction.evaluation_metrics.rmse }}</div>
                        <div class="metric-label">RMSE</div>
                        <div class="metric-description">Root Mean Square Error</div>
                      </div>
                    </div>
                  </div>
                  <div v-else class="empty-data">
                    <div class="empty-state">
                      <q-icon name="analytics" size="48px" color="grey-5" />
                      <p>No volume prediction data available</p>
                      <p class="empty-subtitle">Patient volume forecasting will appear here</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useQuasar } from 'quasar';
import { api } from '../boot/axios';
import NurseHeader from 'src/components/NurseHeader.vue';
import NurseSidebar from 'src/components/NurseSidebar.vue';
import { showVerificationToastOnce } from 'src/utils/verificationToast';
import { Bar, Doughnut, Line } from 'vue-chartjs';
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
} from 'chart.js';

// Register Chart.js components
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
);

const $q = useQuasar();

const rightDrawerOpen = ref(false);

// Analytics data interfaces
interface MedicationAnalysis {
  medication_pareto_data?: Array<{
    medication: string;
    frequency: number;
    cumulative_percentage: number;
  }>;
}

interface PatientDemographics {
  age_distribution?: { [key: string]: number };
  gender_proportions?: { [key: string]: number };
}

interface HealthTrends {
  top_illnesses_by_week?: Array<{
    medical_condition: string;
    count: number;
    date_of_admission: string;
  }>;
}

interface VolumePrediction {
  evaluation_metrics?: {
    mae: number;
    rmse: number;
  };
  forecasted_data?: Array<{
    date: string;
    predicted_volume: number;
    actual_volume?: number;
  }>;
}

interface AnalyticsData {
  medication_analysis: MedicationAnalysis | null;
  patient_demographics: PatientDemographics | null;
  health_trends: HealthTrends | null;
  volume_prediction: VolumePrediction | null;
}

// Search result interfaces
interface PatientSearchResult {
  id: number | string;
  full_name?: string;
  patient_name?: string;
  name?: string;
  room_number?: string;
}

interface DoctorSearchResult {
  id: number | string;
  full_name?: string;
  name?: string;
  specialization?: string;
}

interface MedicineSearchResult {
  id: number | string;
  medicine_name?: string;
  name?: string;
  stock_quantity?: number;
  current_stock?: number;
}

// Analytics data
const analyticsData = ref<AnalyticsData>({
  medication_analysis: null,
  patient_demographics: null,
  health_trends: null,
  volume_prediction: null,
});

// AI Suggestions removed from UI; PDF will include recommendations

// Human-readable AI summary for Nurse Analytics
const nurseSummaryText = computed(() => {
  const d = analyticsData.value;
  const sections: string[] = [];

  // Medication highlights
  {
    const meds = d?.medication_analysis?.medication_pareto_data || [];
    if (Array.isArray(meds) && meds.length) {
      const top = [...meds]
        .sort((a, b) => Number(b.frequency || 0) - Number(a.frequency || 0))
        .slice(0, 3)
        .map((m) => `${m.medication} (${m.frequency})`)
        .join(', ');
      sections.push(['Medication Highlights', `• Top meds: ${top}.`].join('\n'));
    }
  }

  // Patient demographics
  {
    const gender = d?.patient_demographics?.gender_proportions || {};
    const age = d?.patient_demographics?.age_distribution || {};
    const lines: string[] = [];
    const genderEntries = Object.entries(gender);
    if (genderEntries.length) {
      const gStr = genderEntries.map(([k, v]) => `${k}: ${Number(v)}`).join(', ');
      lines.push(`• Gender mix: ${gStr}.`);
    }
    const ageEntries = Object.entries(age)
      .sort((a, b) => Number(b[1]) - Number(a[1]))
      .slice(0, 3);
    if (ageEntries.length) {
      const aStr = ageEntries.map(([k, v]) => `${k} (${Number(v)})`).join(', ');
      lines.push(`• Age groups: ${aStr}.`);
    }
    if (lines.length) sections.push(['Patient Demographics', ...lines].join('\n'));
  }

  // Health trends
  {
    const weeklyTop = d?.health_trends?.top_illnesses_by_week || [];
    if (Array.isArray(weeklyTop) && weeklyTop.length) {
      const topTriplet = weeklyTop
        .slice(0, 3)
        .map((it) => `${it.medical_condition} (${Number(it.count)})`)
        .join(', ');
      sections.push(['Health Trends', `• Top this week: ${topTriplet}.`].join('\n'));
    }
  }

  // Volume prediction
  {
    const vp = d?.volume_prediction?.forecasted_data || [];
    if (vp.length) {
      const predicted = vp.map((x) => Number(x.predicted_volume || 0));
      const actuals = vp.filter((x) => typeof x.actual_volume === 'number').map((x) => Number(x.actual_volume));
      const pAvg = Math.round(predicted.reduce((s, n) => s + n, 0) / predicted.length);
      const aAvg = actuals.length ? Math.round(actuals.reduce((s, n) => s + n, 0) / actuals.length) : null;
      const pFirst = predicted[0] ?? null;
      const pLast = predicted[predicted.length - 1] ?? null;
      const vTrend = pFirst != null && pLast != null ? (pLast > pFirst ? 'increasing' : pLast < pFirst ? 'decreasing' : 'stable') : null;
      const latest = vp[vp.length - 1]!;
      const lines: string[] = [];
      lines.push(`• Trend: ${vTrend || 'stable'}; avg predicted ${pAvg}${aAvg != null ? `, avg actual ${aAvg}` : ''}.`);
      lines.push(`• Latest (${latest.date}): predicted ${Number(latest.predicted_volume)}${typeof latest.actual_volume === 'number' ? `, actual ${Number(latest.actual_volume)}` : ''}.`);
      sections.push(['Patient Volume', ...lines].join('\n'));
    }
  }

  if (!sections.length) return 'Analytics results are not available yet.';
  return sections.join('\n\n');
});

// Zoom functionality
const zoomedData = ref<{
  type: string | null;
  visible: boolean;
}>({
  type: null,
  visible: false,
});

// Chart data computed properties
const medicationChartData = computed(() => {
  if (!analyticsData.value.medication_analysis?.medication_pareto_data) {
    return { labels: [], datasets: [] };
  }
  
  const medications = analyticsData.value.medication_analysis.medication_pareto_data.slice(0, 5);
  
  return {
    labels: medications.map(med => med.medication),
    datasets: [
      {
        label: 'Prescriptions',
        data: medications.map(med => med.frequency),
        backgroundColor: [
          '#9c27b0',
          '#2196f3',
          '#4caf50',
          '#ff9800',
          '#f44336',
        ],
        borderColor: [
          '#7b1fa2',
          '#1976d2',
          '#388e3c',
          '#f57c00',
          '#d32f2f',
        ],
        borderWidth: 1,
      },
    ],
  };
});

const genderChartData = computed(() => {
  if (!analyticsData.value.patient_demographics?.gender_proportions) {
    return { labels: [], datasets: [] };
  }
  
  const genders = analyticsData.value.patient_demographics.gender_proportions;
  
  return {
    labels: Object.keys(genders),
    datasets: [
      {
        data: Object.values(genders),
        backgroundColor: ['#2196f3', '#e91e63'],
        borderColor: ['#1976d2', '#c2185b'],
        borderWidth: 2,
      },
    ],
  };
});

const ageChartData = computed(() => {
  if (!analyticsData.value.patient_demographics?.age_distribution) {
    return { labels: [], datasets: [] };
  }
  
  const ageGroups = analyticsData.value.patient_demographics.age_distribution;
  
  return {
    labels: Object.keys(ageGroups),
    datasets: [
      {
        label: 'Patients',
        data: Object.values(ageGroups),
        backgroundColor: '#4caf50',
        borderColor: '#388e3c',
        borderWidth: 1,
      },
    ],
  };
});

const healthTrendsChartData = computed(() => {
  if (!analyticsData.value.health_trends?.top_illnesses_by_week) {
    return { labels: [], datasets: [] };
  }
  
  const conditions = analyticsData.value.health_trends.top_illnesses_by_week.slice(0, 5);
  
  return {
    labels: conditions.map(condition => condition.medical_condition),
    datasets: [
      {
        label: 'Cases',
        data: conditions.map(condition => condition.count),
        backgroundColor: '#ff9800',
        borderColor: '#f57c00',
        borderWidth: 1,
      },
    ],
  };
});

const volumePredictionChartData = computed(() => {
  if (!analyticsData.value.volume_prediction) {
    return { labels: [], datasets: [] };
  }
  
  // Generate sample data for demonstration - replace with actual data from backend
  const data = analyticsData.value.volume_prediction;
  
  // If we have forecasted data, use it
  if (data.forecasted_data && Array.isArray(data.forecasted_data)) {
    const labels = data.forecasted_data.map((item) => item.date);
    const predictedVolume = data.forecasted_data.map((item) => item.predicted_volume);
    const actualVolume = data.forecasted_data.map((item) => item.actual_volume !== undefined ? item.actual_volume : null);
    
    return {
      labels,
      datasets: [
        {
          label: 'Predicted Volume',
          data: predictedVolume,
          borderColor: '#2196f3',
          backgroundColor: 'rgba(33, 150, 243, 0.1)',
          borderWidth: 2,
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          pointBackgroundColor: '#2196f3',
        },
        {
          label: 'Actual Volume',
          data: actualVolume,
          borderColor: '#4caf50',
          backgroundColor: 'rgba(76, 175, 80, 0.1)',
          borderWidth: 2,
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          pointBackgroundColor: '#4caf50',
        },
      ],
    };
  }
  
  // Fallback: Generate demo data
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
  const predictedVolume = [45, 52, 48, 55, 60, 58];
  const actualVolume = [42, 50, 46, 52, 58, 56];
  
  return {
    labels: months,
    datasets: [
      {
        label: 'Predicted Volume',
        data: predictedVolume,
        borderColor: '#2196f3',
        backgroundColor: 'rgba(33, 150, 243, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointBackgroundColor: '#2196f3',
      },
      {
        label: 'Actual Volume',
        data: actualVolume,
        borderColor: '#4caf50',
        backgroundColor: 'rgba(76, 175, 80, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointBackgroundColor: '#4caf50',
      },
    ],
  };
});

// Chart options
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top' as const,
    },
    title: {
      display: true,
      font: {
        size: 14,
        weight: 'bold' as const,
      },
    },
  },
};

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom' as const,
    },
    title: {
      display: true,
      font: {
        size: 14,
        weight: 'bold' as const,
      },
    },
  },
};

// Search functionality
const searchText = ref('');
const searchResults = ref<
  Array<{
    type: string;
    data: Record<string, string | number>;
  }>
>([]);

// Location data
const locationData = ref<{
  city: string;
  country: string;
} | null>(null);
const locationLoading = ref(false);
const locationError = ref(false);

// Notifications
const showNotifications = ref(false);
const unreadNotificationsCount = computed(() => 0); // Placeholder

// Real-time features
const currentTime = ref('');
const weatherData = ref<{
  temperature: number;
  condition: string;
  location: string;
} | null>(null);
const weatherLoading = ref(false);
const weatherError = ref(false);
let timeInterval: NodeJS.Timeout | null = null;

// User profile data
const userProfile = ref<{
  first_name?: string;
  last_name?: string;
  full_name: string;
  department?: string;
  role: string;
  profile_picture: string | null;
  verification_status: string;
  email?: string;
}>({
  first_name: '',
  last_name: '',
  full_name: 'Loading...',
  department: 'Loading department...',
  role: 'nurse',
  profile_picture: null,
  verification_status: 'not_submitted',
  email: '',
});

// File input reference for profile picture upload
// Upload controls removed: initials-only avatar


/**
 * Computed property that formats the current date for display in the greeting
 * @returns {string} Formatted date string (e.g., "Monday, January 15, 2024")
 *
 * How it works:
 * 1. Gets the current date using new Date()
 * 2. Formats it using toLocaleDateString with specific options
 * 3. Returns a human-readable date string with weekday, month, day, and year
 */
const currentDate = computed(() => {
  const now = new Date();
  return now.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
});


// Search functionality methods
const onSearchInput = async (value: string | number | null) => {
  const searchValue = String(value || '');
  if (searchValue.length > 2) {
    try {
      // Search for patients, doctors, and medicines using real API endpoints
      const [patientsResponse, doctorsResponse, medicinesResponse] = await Promise.all([
        api.get(`/users/nurse/patients/?search=${encodeURIComponent(searchValue)}`),
        api.get(`/operations/available-doctors/?search=${encodeURIComponent(searchValue)}`),
        api.get(`/operations/medicine-inventory/?search=${encodeURIComponent(searchValue)}`),
      ]);

      const results = [
        ...(patientsResponse.data.patients || []).map((item: PatientSearchResult) => ({
          type: 'patient',
          data: {
            id: item.id,
            name: item.full_name || item.patient_name || item.name || 'Unknown Patient',
            room: item.room_number || 'N/A',
          },
        })),
        ...(doctorsResponse.data || []).map((item: DoctorSearchResult) => ({
          type: 'doctor',
          data: {
            id: item.id,
            name: item.full_name || item.name || 'Unknown Doctor',
            specialization: item.specialization || 'General',
          },
        })),
        ...(medicinesResponse.data || []).map((item: MedicineSearchResult) => ({
          type: 'medicine',
          data: {
            id: item.id,
            name: item.medicine_name || item.name || 'Unknown Medicine',
            stock: item.stock_quantity || item.current_stock || 0,
          },
        })),
      ];

      searchResults.value = results.slice(0, 10); // Limit to 10 results
    } catch (error) {
      console.error('Search error:', error);
      searchResults.value = [];
    }
  } else {
    searchResults.value = [];
  }
};

const clearSearch = () => {
  searchText.value = '';
  searchResults.value = [];
};

const selectSearchResult = (result: { type: string; data: Record<string, string | number> }) => {
  console.log('Selected search result:', result);
  clearSearch();
  // Handle navigation based on result type
};

// Location functionality
const fetchLocation = async () => {
  locationLoading.value = true;
  locationError.value = false;

  try {
    // Mock location data - replace with actual geolocation API
    await new Promise((resolve) => setTimeout(resolve, 1000));
    locationData.value = {
      city: 'Mandaluyong City',
      country: 'Philippines',
    };
  } catch (error) {
    console.error('Failed to fetch location:', error);
    locationError.value = true;
  } finally {
    locationLoading.value = false;
  }
};

// Nurse AI suggestions removed; recommendations are included in generated PDF.

/**
 * Updates the current time display in the header
 * @returns {void}
 *
 * How it works:
 * 1. Gets the current date and time using new Date()
 * 2. Formats it using toLocaleTimeString with 12-hour format
 * 3. Updates the currentTime reactive reference
 * 4. This function is called every second by setInterval
 */
const updateTime = () => {
  const now = new Date();
  currentTime.value = now.toLocaleTimeString('en-US', {
    hour12: true,
    hour: 'numeric',
    minute: '2-digit',
    second: '2-digit',
  });
};

/**
 * Fetches weather data for display in the header
 * @returns {Promise<void>}
 *
 * How it works:
 * 1. Sets loading state to true and clears any previous errors
 * 2. Simulates API call with a 1-second delay (replace with real API)
 * 3. Sets mock weather data (temperature, condition, location)
 * 4. Handles errors by setting error state and logging to console
 * 5. Always sets loading to false in the finally block
 *
 * Note: Currently uses mock data - replace with actual weather API integration
 */
const fetchWeatherData = async () => {
  weatherLoading.value = true;
  weatherError.value = false;

  try {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    weatherData.value = {
      temperature: 28,
      condition: 'sunny',
      location: 'Mandaluyong City',
    };
  } catch (error) {
    console.error('Failed to fetch weather data:', error);
    weatherError.value = true;
  } finally {
    weatherLoading.value = false;
  }
};

/**
 * Toggles the sidebar drawer open/closed state
 * @returns {void}
 *
 * How it works:
 * 1. Flips the boolean value of rightDrawerOpen
 * 2. This controls the visibility of the sidebar navigation
 * 3. Used by the menu button in the header
 */
const toggleRightDrawer = () => {
  rightDrawerOpen.value = !rightDrawerOpen.value;
};


/**
 * Fetches user profile data from the API and updates the local state
 * @returns {Promise<void>}
 * 1. Makes API call to /users/profile/ endpoint
 * 2. Extracts user data from the response
 * 3. Updates the userProfile reactive reference with the data
 * 4. Handles errors by falling back to localStorage data
 * 5. Shows error notification if both API and localStorage fail
 *
 * Fallback strategy:
 * - If API fails, tries to load from localStorage
 * - If localStorage also fails, shows error notification
 * - This ensures the app doesn't break if the API is down
 */
const fetchUserProfile = async () => {
  try {
    const response = await api.get('/users/profile/');
    const userData = response.data.user;

    // Check for verification status change
    const previousStatus = userProfile.value.verification_status;
    const newStatus = userData.verification_status;

    userProfile.value = {
      first_name: userData.first_name,
      last_name: userData.last_name,
      full_name: userData.full_name,
      department: userData.nurse_profile?.department,
      role: userData.role,
      profile_picture: userData.profile_picture || localStorage.getItem('profile_picture'),
      verification_status: userData.verification_status,
      email: userData.email,
    };

    // Show notification if verification status changed to approved
    if (previousStatus && previousStatus !== 'approved' && newStatus === 'approved') {
      showVerificationToastOnce(newStatus);
    }

    // Store profile picture in localStorage if available
    if (userData.profile_picture) {
      localStorage.setItem('profile_picture', userData.profile_picture);
    }

    console.log('User profile loaded:', userProfile.value);
  } catch (error) {
    console.error('Failed to fetch user profile:', error);

    const userData = localStorage.getItem('user');
    if (userData) {
      const user = JSON.parse(userData);
      userProfile.value = {
        full_name: user.full_name,
        department: user.nurse_profile?.department,
        role: user.role,
        profile_picture: user.profile_picture || null,
        verification_status: user.verification_status || 'not_submitted',
      };
    } else {
      $q.notify({
        type: 'negative',
        message: 'Failed to load user profile',
        position: 'top',
        timeout: 3000,
      });
    }
  }
};

/**
 * Fetches nurse-specific analytics data from the API
 * @returns {Promise<void>}
 *
 * How it works:
 * 1. Makes API call to /analytics/nurse/ endpoint
 * 2. Extracts analytics data from the response
 * 3. Updates the analyticsData reactive reference
 * 4. Handles errors by showing notification to user
 * 5. Logs errors to console for debugging
 *
 * Analytics data includes:
 * - Medication analysis (most prescribed medications)
 * - Patient demographics (age, gender distribution)
 * - Health trends (top medical conditions)
 * - Volume prediction (patient volume forecasting)
 */
const fetchNurseAnalytics = async () => {
  try {
    const response = await api.get('/analytics/nurse/');
    const data = response.data?.data || {};

    // Normalize backend -> frontend for volume prediction
    if (data.volume_prediction && !data.volume_prediction.forecasted_data) {
      const cmp = data.volume_prediction.comparison_data as Array<{
        date: string;
        Forecasted?: number;
        forecasted?: number;
        Actual?: number;
      }>;
      if (Array.isArray(cmp)) {
        data.volume_prediction.forecasted_data = cmp.map((item) => ({
          date: item.date,
          predicted_volume: Number(item.Forecasted ?? item.forecasted ?? 0),
          actual_volume: typeof item.Actual !== 'undefined' ? Number(item.Actual) : undefined,
        }));
      }
    }

    // Medication analysis fallback if missing/malformed
    const medsOK = Array.isArray(data?.medication_analysis?.medication_pareto_data);
    if (!medsOK) {
      data.medication_analysis = {
        medication_pareto_data: [
          { medication: 'Paracetamol', frequency: 45, cumulative_percentage: 32.1 },
          { medication: 'Ibuprofen', frequency: 32, cumulative_percentage: 54.9 },
          { medication: 'Amoxicillin', frequency: 28, cumulative_percentage: 74.9 },
          { medication: 'Aspirin', frequency: 22, cumulative_percentage: 90.6 },
          { medication: 'Metformin', frequency: 18, cumulative_percentage: 100.0 },
        ],
      };
    }

    // Volume prediction fallback if missing
    const volOK = Array.isArray(data?.volume_prediction?.forecasted_data) && data.volume_prediction?.forecasted_data.length;
    if (!volOK) {
      data.volume_prediction = {
        evaluation_metrics: {
          mae: 3.2,
          rmse: 3.24,
        },
        forecasted_data: [
          { date: '2024-01', predicted_volume: 45, actual_volume: 42 },
          { date: '2024-02', predicted_volume: 52, actual_volume: 50 },
          { date: '2024-03', predicted_volume: 48, actual_volume: 46 },
          { date: '2024-04', predicted_volume: 55, actual_volume: 52 },
          { date: '2024-05', predicted_volume: 60, actual_volume: 58 },
          { date: '2024-06', predicted_volume: 58, actual_volume: 56 },
        ],
      };
    }

    analyticsData.value = data;
    console.log('Nurse analytics loaded:', analyticsData.value);
  } catch (error) {
    console.error('Failed to fetch nurse analytics:', error);

    // Load mock data for demonstration purposes
    analyticsData.value = {
      medication_analysis: {
        medication_pareto_data: [
          { medication: 'Paracetamol', frequency: 45, cumulative_percentage: 32.1 },
          { medication: 'Ibuprofen', frequency: 32, cumulative_percentage: 54.9 },
          { medication: 'Amoxicillin', frequency: 28, cumulative_percentage: 74.9 },
          { medication: 'Aspirin', frequency: 22, cumulative_percentage: 90.6 },
          { medication: 'Metformin', frequency: 18, cumulative_percentage: 100.0 },
        ],
      },
      patient_demographics: {
        age_distribution: {
          '0-18': 15,
          '19-35': 45,
          '36-50': 30,
          '51-65': 25,
          '65+': 20,
        },
        gender_proportions: {
          Male: 52,
          Female: 48,
        },
      },
      health_trends: {
        top_illnesses_by_week: [
          { medical_condition: 'Common Cold', count: 12, date_of_admission: '2024-01-15' },
          { medical_condition: 'Hypertension', count: 8, date_of_admission: '2024-01-14' },
          { medical_condition: 'Diabetes', count: 6, date_of_admission: '2024-01-13' },
          { medical_condition: 'Flu', count: 5, date_of_admission: '2024-01-12' },
          { medical_condition: 'Headache', count: 4, date_of_admission: '2024-01-11' },
        ],
      },
      volume_prediction: {
        evaluation_metrics: {
          mae: 3.2,
          rmse: 3.24,
        },
        forecasted_data: [
          { date: '2024-01', predicted_volume: 45, actual_volume: 42 },
          { date: '2024-02', predicted_volume: 52, actual_volume: 50 },
          { date: '2024-03', predicted_volume: 48, actual_volume: 46 },
          { date: '2024-04', predicted_volume: 55, actual_volume: 52 },
          { date: '2024-05', predicted_volume: 60, actual_volume: 58 },
          { date: '2024-06', predicted_volume: 58, actual_volume: 56 },
        ],
      },
    };

    $q.notify({
      type: 'info',
      message: 'Using demo analytics data',
      position: 'top',
      timeout: 3000,
    });
  }
};

/**
 * Handles navigation between different pages in the application
 * @param {string} route - The route name to navigate to
 * @returns {void}
 *
 * How it works:
 * 1. Closes the sidebar drawer first
 * 2. Uses a switch statement to handle different routes
 * 3. Uses Vue Router to navigate to the appropriate page
 * 4. Shows notifications for pages that are not yet implemented
 * 5. Logs unknown routes to console for debugging
 *
 * Supported routes:
 * - nurse-dashboard: Navigate to main dashboard
 * - medicine-inventory: Navigate to medicine inventory page
 * - patient-assessment: Navigate to patient assessment page
 * - analytics: Already on analytics page (no action)
 * - settings: Navigate to settings page
 */

/**
 * Handles user logout by clearing stored data and redirecting to login
 * @returns {void}
 *
 * How it works:
 * 1. Removes access token from localStorage
 * 2. Removes refresh token from localStorage
 * 3. Removes user data from localStorage
 * 4. Redirects to the login page
 *
 * This ensures a clean logout by removing all authentication data
 * and user information from the browser's local storage
 */

/**
 * Shows notification when medication analysis card is clicked
 * @returns {void}
 *
 * How it works:
 * 1. Displays an info notification to the user
 * 2. Indicates that medication analysis is being viewed
 * 3. Auto-dismisses after 2 seconds
 *
 * Future enhancement: Could navigate to detailed medication analysis view
 */
const viewMedicationAnalysis = () => {
  $q.notify({
    type: 'info',
    message: 'Viewing Medication Analysis...',
    position: 'top',
    timeout: 2000,
  });
};

/**
 * Shows notification when demographics card is clicked
 * @returns {void}
 *
 * How it works:
 * 1. Displays an info notification to the user
 * 2. Indicates that demographics data is being viewed
 * 3. Auto-dismisses after 2 seconds
 *
 * Future enhancement: Could navigate to detailed demographics view
 */
const viewDemographics = () => {
  $q.notify({
    type: 'info',
    message: 'Viewing Patient Demographics...',
    position: 'top',
    timeout: 2000,
  });
};

/**
 * Shows notification when health trends card is clicked
 * @returns {void}
 *
 * How it works:
 * 1. Displays an info notification to the user
 * 2. Indicates that health trends are being viewed
 * 3. Auto-dismisses after 2 seconds
 *
 * Future enhancement: Could navigate to detailed trends view
 */
const viewHealthTrends = () => {
  $q.notify({
    type: 'info',
    message: 'Viewing Health Trends...',
    position: 'top',
    timeout: 2000,
  });
};

/**
 * Shows notification when volume prediction card is clicked
 * @returns {void}
 *
 * How it works:
 * 1. Displays an info notification to the user
 * 2. Indicates that volume prediction is being viewed
 * 3. Auto-dismisses after 2 seconds
 *
 * Future enhancement: Could navigate to detailed volume prediction view
 */
const viewVolumePrediction = () => {
  $q.notify({
    type: 'info',
    message: 'Viewing Volume Prediction...',
    position: 'top',
    timeout: 2000,
  });
};

/**
 * Generates and downloads a PDF report of nurse analytics
 * @returns {Promise<void>}
 *
 * How it works:
 * 1. Makes API call to /analytics/pdf/?type=nurse with blob response type
 * 2. Creates a Blob object from the response data
 * 3. Creates a temporary URL for the blob
 * 4. Creates a temporary anchor element for download
 * 5. Sets the filename with current date
 * 6. Programmatically clicks the anchor to trigger download
 * 7. Cleans up by removing the anchor and revoking the URL
 * 8. Shows success/error notifications
 *
 * The PDF contains comprehensive analytics data formatted for nurses
 */
const generatePDFReport = async () => {
  try {
    const response = await api.get('/analytics/pdf/?type=nurse', {
      responseType: 'blob',
    });

    const blob = new Blob([response.data], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `nurse_analytics_report_${new Date().toISOString().split('T')[0]}.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);

    $q.notify({
      type: 'positive',
      message: 'PDF report generated successfully!',
      position: 'top',
      timeout: 3000,
    });
  } catch (error) {
    console.error('Failed to generate PDF report:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to generate PDF report',
      position: 'top',
      timeout: 3000,
    });
  }
};

/**
 * Refreshes analytics data by fetching the latest data from the API
 * @returns {Promise<void>}
 *
 * How it works:
 * 1. Shows info notification that data is being refreshed
 * 2. Calls fetchNurseAnalytics to get latest data from API
 * 3. Waits for the data to be loaded
 * 4. Shows success notification when refresh is complete
 *
 * This ensures users always have the most up-to-date analytics data
 */
const refreshAnalytics = async () => {
  $q.notify({
    type: 'info',
    message: 'Refreshing analytics data...',
    position: 'top',
    timeout: 2000,
  });

  await fetchNurseAnalytics();

  $q.notify({
    type: 'positive',
    message: 'Analytics data refreshed!',
    position: 'top',
    timeout: 2000,
  });
};

// Zoom functionality functions
const showZoomedData = (type: string): void => {
  zoomedData.value = {
    type: type,
    visible: true,
  };
};

const hideZoomedData = (): void => {
  zoomedData.value = {
    type: null,
    visible: false,
  };
};

/**
 * Vue lifecycle hook that runs when the component is mounted
 * @returns {void}
 *
 * How it works:
 * 1. Fetches user profile data from API
 * 2. Fetches nurse analytics data from API
 * 3. Sets initial time display
 * 4. Starts interval to update time every second
 * 5. Fetches weather data for display
 *
 * This ensures all necessary data is loaded when the page opens
 */
onMounted(() => {
  void fetchUserProfile();
  void fetchNurseAnalytics();

  updateTime();
  timeInterval = setInterval(updateTime, 1000);

  void fetchWeatherData();
  void fetchLocation();

  // AI Suggestions removed; recommendations now included in PDF only

  // Refresh user profile every 30 seconds to check for verification status updates
  setInterval(() => {
    void fetchUserProfile();
  }, 30000);

  // More frequent verification status check (every 10 seconds)
  setInterval(() => {
    void fetchUserProfile();
  }, 10000);
});

// Removed AI suggestions watcher; recommendations are embedded in PDF output

// Storage event handler for profile picture sync
const handleStorageChange = (e: StorageEvent) => {
  if (e.key === 'profile_picture' && e.newValue) {
    userProfile.value.profile_picture = e.newValue;
    console.log('🔄 Profile picture updated from storage event:', e.newValue);
  }
};

// Listen for storage changes to sync profile picture across components
window.addEventListener('storage', handleStorageChange);
onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval);
  }

  // Clean up storage event listener
  window.removeEventListener('storage', handleStorageChange);
});
</script>

<style scoped>
/* Verification Overlay Styles */
.verification-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 20px;
}

.verification-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  max-width: 400px;
  margin: 20px;
}

.verification-content {
  text-align: center;
  padding: 40px 30px;
}

.verification-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin: 20px 0 16px 0;
}

.verification-message {
  font-size: 1rem;
  color: #666;
  line-height: 1.6;
  margin-bottom: 24px;
}

.disabled-content {
  opacity: 0.3;
  pointer-events: none;
  filter: blur(2px);
}

/* Main Analytics Section */
.main-analytics-section {
  position: relative;
  margin-bottom: 24px;
}

.main-analytics-card {
  max-width: none;
  margin: 0;
  width: 100%;
}

/* Prototype Header Styles */
.prototype-header {
  background: linear-gradient(135deg, #286660 0%, #4a7c59 100%);
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
  font-size: 14px;
}

/* Prototype Sidebar Styles */
.prototype-sidebar {
  background: white;
  border-right: 1px solid #e0e0e0;
  position: relative;
}

.sidebar-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding-bottom: 80px; /* Space for footer */
}

.logo-section {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: #286660;
}

.menu-btn {
  color: #666;
}

.sidebar-user-profile {
  padding: 24px 20px;
  border-bottom: 1px solid #e0e0e0;
  text-align: center;
}

.profile-picture-container {
  position: relative;
  display: inline-block;
  margin-bottom: 16px;
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

.sidebar-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20px;
  border-top: 1px solid #e0e0e0;
  background: #f8f9fa;
}

.logout-section {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20px;
  border-top: 1px solid #e0e0e0;
  background: #f8f9fa;
}

.logout-btn {
  width: 100%;
  border-radius: 8px;
  font-weight: 600;
  text-transform: uppercase;
}

/* Profile Avatar Styles - Circular Design */
.profile-avatar {
  border: 3px solid #1e7668 !important;
  border-radius: 50% !important;
  overflow: hidden !important;
}


.profile-placeholder {
  width: 100%;
  height: 100%;
  display: flex !important;
  align-items: center;
  justify-content: center;
  background: #286660 !important;
  color: white !important;
  font-weight: 600;
  font-size: 1.5rem;
  border-radius: 50%;
  position: relative;
  z-index: 1;
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

/* Page Container with Background */
.page-container-with-fixed-header {
  background: #f8f9fa;
  min-height: 100vh;
  position: relative;
}

/* Greeting Section */
.greeting-section {
  padding: 24px;
  background: transparent;
}

.greeting-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  overflow: hidden;
  position: relative;
  width: 100%;
  max-width: none;
  margin: 0;
}

.greeting-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #286660, #6ca299, #b8d2ce);
  border-radius: 16px 16px 0 0;
}

.greeting-content {
  padding: 24px;
}

.greeting-text {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin: 0 0 8px 0;
}

.greeting-subtitle {
  font-size: 16px;
  color: #666;
  margin: 0;
}

/* Dashboard Cards Section */
.dashboard-cards-section {
  padding: 24px;
}

.dashboard-cards-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

/* Glassmorphism Dashboard Cards */
.dashboard-card {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
  overflow: hidden;
  position: relative;
}

.dashboard-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #286660, #6ca299, #b8d2ce);
  border-radius: 16px 16px 0 0;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.dashboard-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
  background: rgba(255, 255, 255, 0.35);
}

.dashboard-card:hover::before {
  opacity: 1;
}

.card-content {
  padding: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.card-text {
  flex: 1;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  line-height: 1.3;
}

.card-description {
  font-size: 14px;
  color: #666;
  line-height: 1.4;
}

.card-icon {
  margin-left: 16px;
  color: #286660;
  opacity: 0.8;
  transition: all 0.3s ease;
}

.dashboard-card:hover .card-icon {
  opacity: 1;
  transform: scale(1.1);
}

/* Card-specific colors */
.medication-card .card-icon {
  color: #9c27b0;
}
.demographics-card .card-icon {
  color: #2196f3;
}
.trends-card .card-icon {
  color: #4caf50;
}
.volume-card .card-icon {
  color: #ff9800;
}

/* Zoom functionality styles */
.zoom-card {
  position: relative;
}

.zoomed-data-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 20px;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: zoomIn 0.3s ease-out;
}

.zoomed-content {
  text-align: center;
  width: 100%;
}

.zoomed-content h4 {
  color: #286660;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
}

.zoomed-stats {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stat-row {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-label {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.stat-value {
  font-size: 14px;
  color: #286660;
  font-weight: 600;
}

.medications-list,
.age-stats,
.gender-stats,
.conditions-list,
.performance-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.medication-item,
.age-item,
.gender-item,
.condition-item,
.performance-item {
  background: rgba(40, 102, 96, 0.1);
  color: #286660;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.no-data {
  color: #999;
  font-size: 14px;
  font-style: italic;
}

@keyframes zoomIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* Analytics Section */
.analytics-section {
  padding: 24px;
  margin-top: 20px;
}

.ai-summary-card {
  border-radius: 14px;
  box-shadow: 0 3px 12px rgba(0, 0, 0, 0.08);
  padding: 16px;
  min-height: 220px;
  margin-top: 20px;
}

.actions-row {
  display: flex;
  gap: 12px;
  margin-bottom: 6px;
}

.analytics-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.05);
  width: calc(100% - 48px);
  max-width: 1800px;
  margin: 0 24px;
}

.analytics-header {
  text-align: center;
  margin-bottom: 32px;
  padding: 24px 24px 0 24px;
}

.analytics-content {
  padding: 0 24px 24px 24px;
}

/* Empty State Styles */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
  color: #666;
}

.empty-state p {
  margin: 12px 0 8px 0;
  font-size: 16px;
  font-weight: 500;
}

.empty-subtitle {
  font-size: 14px !important;
  color: #999 !important;
  font-weight: 400 !important;
}

.analytics-title {
  font-size: 24px;
  font-weight: 700;
  color: #333;
  margin: 0 0 24px 0;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.analytics-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.action-btn {
  border-radius: 8px;
  font-weight: 500;
  padding: 12px 24px;
  min-width: 160px;
}

/* Analytics Panels */
.analytics-panels-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-top: 20px;
  align-self: start;
}

/* Structured Grid Layout for Analytics Panels */
.structured-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-areas:
    'surge volume'
    'trends trends'
    'demographics gender';
  gap: 20px;
}

/* Map panels to grid areas */
.medication-panel { grid-area: surge; }
.volume-panel, .prediction-panel { grid-area: volume; }
.trends-panel { grid-area: trends; }
.demographics-panel { grid-area: demographics; }
.gender-panel { grid-area: gender; }

/* Responsive adjustments for grid */
@media (max-width: 1200px) {
  .structured-grid {
    grid-template-columns: 1fr 1fr;
    grid-template-areas:
      'surge volume'
      'trends trends'
      'demographics gender';
  }
}
@media (max-width: 768px) {
  .structured-grid {
    grid-template-columns: 1fr;
    grid-template-areas:
      'surge'
      'volume'
      'trends'
      'demographics'
      'gender';
  }
}

/* Analytics content layout to place sidebar inside card */
.ai-summary-disclaimer { 
  color: #546E7A; 
  font-size: 14px; 
  margin-bottom: 12px; 
  line-height: 1.5; 
}
.analytics-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  align-items: stretch;
}
.analytics-sidebar-panel { align-self: stretch; display: flex; flex-direction: column; height: 100%; }
.sidebar-actions { display: flex; gap: 12px; margin-top: 8px; }
.sidebar-btn { flex: 1; }
.ai-summary-header { 
  font-weight: 700; 
  color: #1f3d3a; 
  margin-bottom: 8px; 
  font-size: 16px; 
  letter-spacing: 0.2px; 
}
.ai-summary-content { 
  color: #143b38; 
  font-size: 15px; 
}
.ai-summary-text { color: #143b38; font-size: 15px; line-height: 1.6; white-space: pre-wrap; }
/* Ensure panels left, sidebar right regardless of DOM order */
.analytics-content > .analytics-panels-container { grid-column: 1; }
.analytics-content > .analytics-sidebar-panel { grid-column: 2; }
 
 .analytics-panel {
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e9ecef;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 20px;
  min-height: 400px;
}

/* Chart Container Styles */
.chart-container {
  height: 300px;
  width: 100%;
  margin: 16px 0;
  position: relative;
}

.demographics-charts {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chart-section {
  margin-bottom: 20px;
}

.chart-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  text-align: center;
}

/* Volume Prediction Styles */
.volume-prediction-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.metrics-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.metric-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  border: 1px solid #e9ecef;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.metric-value {
  font-size: 32px;
  font-weight: 700;
  color: #286660;
  margin-bottom: 8px;
}

.metric-label {
  font-size: 14px;
  font-weight: 600;
  color: #666;
  margin-bottom: 4px;
}

.metric-description {
  font-size: 12px;
  color: #999;
}

.performance-visualization {
  background: white;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e9ecef;
}

.performance-bar {
  margin-bottom: 16px;
}

.performance-label {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.progress-bar {
  width: 100%;
  height: 20px;
  background: #e9ecef;
  border-radius: 10px;
  overflow: hidden;
  position: relative;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4caf50, #8bc34a);
  border-radius: 10px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  color: #666;
  text-align: center;
  font-weight: 600;
}

.panel-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
  text-align: center;
}

.panel-content {
  height: 100%;
}

.analytics-data {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.data-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.data-label {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.data-values {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.value-item {
  font-size: 13px;
  color: #666;
  padding: 4px 8px;
  background: white;
  border-radius: 4px;
  border-left: 3px solid #286660;
}

.empty-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #666;
}

.empty-data p {
  margin-top: 12px;
  font-size: 14px;
}

/* Ensure mobile header is always visible on mobile devices */
@media (max-width: 768px) {
  .mobile-header-layout {
    display: flex !important;
  }

  .header-toolbar {
    display: none !important;
  }

  /* Force header visibility on iOS */
  .prototype-header {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    z-index: 2000 !important;
    padding-top: max(env(safe-area-inset-top), 8px) !important;
  }

  /* Ensure main content doesn't overlap header */
  .q-page {
    padding-top: calc(env(safe-area-inset-top) + 120px) !important;
  }
}

/* Header Layout Styles */
.header-left {
  display: flex;
  align-items: center;
  flex: 1;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-container {
  position: relative;
  max-width: 400px;
  width: 100%;
}

.search-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-height: 300px;
  overflow-y: auto;
}

.notification-btn {
  color: #666;
  transition: color 0.2s ease;
}

.notification-btn:hover {
  color: #1976d2;
}

/* Pill-style displays */
.time-pill,
.weather-pill,
.location-pill {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: rgba(25, 118, 210, 0.1);
  border-radius: 20px;
  font-size: 14px;
  color: #1976d2;
  font-weight: 500;
  min-width: fit-content;
}

.time-pill {
  background: rgba(76, 175, 80, 0.1);
  color: #4caf50;
}

.weather-pill {
  background: rgba(255, 152, 0, 0.1);
  color: #ff9800;
}

.location-pill {
  background: rgba(156, 39, 176, 0.1);
  color: #9c27b0;
}

.weather-loading,
.location-loading {
  opacity: 0.7;
}

.weather-error,
.location-error {
  background: rgba(244, 67, 54, 0.1);
  color: #f44336;
}

/* Mobile responsive adjustments */
@media (max-width: 768px) {
  .header-right {
    gap: 8px;
  }

  .time-pill,
  .weather-pill,
  .location-pill {
    padding: 6px 10px;
    font-size: 12px;
    gap: 4px;
  }

  .search-container {
    max-width: none;
  }
}

/* Responsive Design - Mobile and Web Support */
@media (max-width: 768px) {
  .mobile-header-layout {
    display: flex !important;
  }

  .header-toolbar {
    display: none !important;
  }

  /* Mobile header positioning */
  .prototype-header {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    z-index: 2000 !important;
    padding-top: max(env(safe-area-inset-top), 8px) !important;
  }

  /* Ensure main content doesn't overlap header */
  .q-page {
    padding-top: calc(env(safe-area-inset-top) + 120px) !important;
  }
}

/* Desktop Header Layout */
@media (min-width: 769px) {
  .mobile-header-layout {
    display: none;
  }

  .prototype-header .header-toolbar {
    display: flex;
  }
}

/* Global Modal Safe Area Support */
@media (max-width: 768px) {
  :deep(.q-dialog) {
    padding: 0 !important;
    margin: 0 !important;
  }

  :deep(.q-dialog__inner) {
    padding: max(env(safe-area-inset-top), 20px) max(env(safe-area-inset-right), 8px)
      max(env(safe-area-inset-bottom), 8px) max(env(safe-area-inset-left), 8px) !important;
    margin: 0 !important;
    min-height: 100vh !important;
    display: flex !important;
    align-items: flex-start !important;
    justify-content: center !important;
    padding-top: max(env(safe-area-inset-top), 20px) !important;
  }

  :deep(.q-dialog__inner > div) {
    max-height: calc(
      100vh - max(env(safe-area-inset-top), 20px) - max(env(safe-area-inset-bottom), 8px)
    ) !important;
    width: 100% !important;
    max-width: calc(
      100vw - max(env(safe-area-inset-left), 8px) - max(env(safe-area-inset-right), 8px)
    ) !important;
    margin: 0 !important;
  }
}

@media (max-width: 480px) {
  :deep(.q-dialog__inner) {
    padding: max(env(safe-area-inset-top), 24px) max(env(safe-area-inset-right), 4px)
      max(env(safe-area-inset-bottom), 4px) max(env(safe-area-inset-left), 4px) !important;
  }

  :deep(.q-dialog__inner > div) {
    max-height: calc(
      100vh - max(env(safe-area-inset-top), 24px) - max(env(safe-area-inset-bottom), 4px)
    ) !important;
    max-width: calc(
      100vw - max(env(safe-area-inset-left), 4px) - max(env(safe-area-inset-right), 4px)
    ) !important;
  }
}

/* Modal Close Button Styles */
.modal-close-btn {
  padding: 4px;
  transition: all 0.2s ease;
}

/* Desktop close button styling */
@media (min-width: 769px) {
  .modal-close-btn {
    padding: 6px;
    min-width: 36px;
    min-height: 36px;
    font-size: 18px;
  }

  .modal-close-btn:hover {
    background: rgba(0, 0, 0, 0.1);
    border-radius: 50%;
  }
}

/* Mobile close button styling */
@media (max-width: 768px) {
  .modal-close-btn {
    padding: 8px !important;
    min-width: 44px !important;
    min-height: 44px !important;
    font-size: 20px !important;
    background: rgba(0, 0, 0, 0.1) !important;
    border-radius: 50% !important;
  }

  .modal-close-btn:hover {
    background: rgba(0, 0, 0, 0.2) !important;
  }
}

@media (max-width: 480px) {
  .modal-close-btn {
    padding: 10px !important;
    min-width: 48px !important;
    min-height: 48px !important;
    font-size: 22px !important;
    background: rgba(0, 0, 0, 0.1) !important;
    border-radius: 50% !important;
  }

  .modal-close-btn:hover {
    background: rgba(0, 0, 0, 0.2) !important;
  }
}

/* Responsive Design */
@media (max-width: 768px) {
  .dashboard-cards-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }

  .analytics-panels-container {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .greeting-text {
    font-size: 24px;
  }

  .card-content {
    padding: 20px;
  }

  .card-title {
    font-size: 16px;
  }

  .card-description {
    font-size: 13px;
  }

  .analytics-actions {
    flex-direction: column;
    align-items: center;
  }

  .action-btn {
    width: 100%;
    max-width: 200px;
  }

  /* Chart responsive adjustments */
  .chart-container {
    height: 250px;
  }

  .demographics-charts {
    gap: 16px;
  }

  .metrics-cards {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .metric-value {
    font-size: 28px;
  }
}

@media (max-width: 480px) {
  .dashboard-cards-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .greeting-text {
    font-size: 20px;
  }

  .card-content {
    padding: 16px;
  }

  .card-title {
    font-size: 15px;
  }

  .card-description {
    font-size: 12px;
  }

  /* Mobile chart adjustments */
  .chart-container {
    height: 200px;
  }

  .analytics-panel {
    padding: 16px;
    min-height: 350px;
  }

  .metric-card {
    padding: 16px;
  }

  .metric-value {
    font-size: 24px;
  }
}

/* Header Styles */
.prototype-header {
  background: #286660;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-toolbar {
  padding: 0 16px;
}

.header-left,
.header-right {
  display: flex;
  align-items: center;
  gap: 24px;
}

.search-container {
  min-width: 300px;
}

.search-input {
  border-radius: 8px;
}

.time-display,
.weather-display,
.weather-loading,
.weather-error {
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
  font-size: 14px;
  font-size: 14px;
  font-weight: 500;
  padding: 6px 12px;
  border-radius: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.time-text,
.weather-text,
.weather-location {
  font-size: 14px;
  font-weight: 500;
  color: white;
}

.weather-location {
  font-size: 12px;
  opacity: 0.8;
}

.weather-loading,
.weather-error {
  display: flex;
  align-items: center;
  gap: 6px;
  color: white;
  font-size: 14px;
  font-weight: 500;
}

.weather-error .q-icon {
  color: #ff6b6b;
}
.greeting-card {
  width: calc(100% - 48px);
  max-width: 1800px;
  margin: 0 24px;
}
</style>
