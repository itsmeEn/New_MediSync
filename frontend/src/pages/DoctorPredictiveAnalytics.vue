<template>
  <q-layout view="hHh Lpr fFf">
    <DoctorHeader @toggle-drawer="rightDrawerOpen = !rightDrawerOpen" />

    <DoctorSidebar 
      v-model="rightDrawerOpen"
      active-route="analytics"
    />

    <q-page-container class="page-container-with-fixed-header">
      <!-- Greeting Section -->
      <div class="greeting-section">
        <q-card class="greeting-card">
          <q-card-section class="greeting-content">
            <h2 class="greeting-text">
              Predictive Analytics Dashboard,
              {{ userProfile.role.charAt(0).toUpperCase() + userProfile.role.slice(1) }}
              {{ userProfile.full_name }}
            </h2>
            <p class="greeting-subtitle">
              AI-powered insights for clinical decision making - {{ currentDate }}
            </p>
          </q-card-section>
        </q-card>
      </div>

      <!-- Analytics Cards Section -->
      <div class="dashboard-cards-section">
        <div class="dashboard-cards-grid">
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
                    <span class="stat-label">Total Patients:</span>
                    <span class="stat-value">{{
                      analyticsData.patient_demographics.total_patients || 'N/A'
                    }}</span>
                  </div>
                  <div class="stat-row">
                    <span class="stat-label">Average Age:</span>
                    <span class="stat-value"
                      >{{ analyticsData.patient_demographics.average_age || 'N/A' }} years</span
                    >
                  </div>
                  <div class="stat-row">
                    <span class="stat-label">Gender Distribution:</span>
                    <div class="gender-stats">
                      <span
                        v-for="(percentage, gender) in analyticsData.patient_demographics
                          .gender_proportions"
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

          <!-- Illness Prediction Card -->
          <q-card
            class="dashboard-card prediction-card zoom-card"
            @click="viewIllnessPrediction"
            @mouseenter="showZoomedData('prediction')"
            @mouseleave="hideZoomedData"
          >
            <q-card-section class="card-content">
              <div class="card-text">
                <div class="card-title">Illness Prediction</div>
                <div class="card-description">Statistical analysis and disease patterns</div>
              </div>
              <div class="card-icon">
                <q-icon name="psychology" size="2.5rem" />
              </div>
            </q-card-section>
            <!-- Zoomed Data Overlay -->
            <div class="zoomed-data-overlay" v-if="zoomedData.type === 'prediction'">
              <div class="zoomed-content">
                <h4>Illness Prediction Analysis</h4>
                <div v-if="analyticsData.illness_prediction" class="zoomed-stats">
                  <div class="stat-row">
                    <span class="stat-label">Chi-Square Statistic:</span>
                    <span class="stat-value">{{
                      analyticsData.illness_prediction.chi_square_statistic || 'N/A'
                    }}</span>
                  </div>
                  <div class="stat-row">
                    <span class="stat-label">P-Value:</span>
                    <span class="stat-value">{{
                      analyticsData.illness_prediction.p_value || 'N/A'
                    }}</span>
                  </div>
                  <div class="stat-row">
                    <span class="stat-label">Association Result:</span>
                    <span class="stat-value">{{
                      analyticsData.illness_prediction.association_result || 'N/A'
                    }}</span>
                  </div>
                </div>
                <div v-else class="no-data">
                  <p>No prediction data available</p>
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
                <h4>Health Trends Analysis</h4>
                <div v-if="analyticsData.health_trends" class="zoomed-stats">
                  <div class="stat-row">
                    <span class="stat-label">Top Conditions:</span>
                    <div class="conditions-list">
                      <span
                        v-for="condition in analyticsData.health_trends.top_illnesses_by_week?.slice(
                          0,
                          3,
                        )"
                        :key="condition.medical_condition"
                        class="condition-item"
                      >
                        {{ condition.medical_condition }}: {{ condition.count }}
                      </span>
                    </div>
                  </div>
                  <div class="stat-row">
                    <span class="stat-label">Trend Analysis:</span>
                    <div class="trend-items">
                      <span
                        v-for="condition in analyticsData.health_trends.trend_analysis?.increasing_conditions?.slice(
                          0,
                          2,
                        )"
                        :key="condition"
                        class="trend-item increasing"
                      >
                        {{ condition }} ↗
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

          <!-- Surge Prediction Card -->
          <q-card
            class="dashboard-card surge-card zoom-card"
            @click="viewSurgePrediction"
            @mouseenter="showZoomedData('surge')"
            @mouseleave="hideZoomedData"
          >
            <q-card-section class="card-content">
              <div class="card-text">
                <div class="card-title">Surge Prediction</div>
                <div class="card-description">Forecast illness outbreaks and capacity</div>
              </div>
              <div class="card-icon">
                <q-icon name="warning" size="2.5rem" />
              </div>
            </q-card-section>
            <!-- Zoomed Data Overlay -->
            <div class="zoomed-data-overlay" v-if="zoomedData.type === 'surge'">
              <div class="zoomed-content">
                <h4>Surge Prediction Analysis</h4>
                <div v-if="analyticsData.surge_prediction" class="zoomed-stats">
                  <div class="stat-row">
                    <span class="stat-label">Model Accuracy:</span>
                    <span class="stat-value"
                      >{{ analyticsData.surge_prediction.model_accuracy || 'N/A' }}%</span
                    >
                  </div>
                  <div class="stat-row">
                    <span class="stat-label">Risk Factors:</span>
                    <div class="risk-factors">
                      <span
                        v-for="factor in analyticsData.surge_prediction.risk_factors?.slice(0, 2)"
                        :key="factor"
                        class="risk-item"
                      >
                        {{ factor }}
                      </span>
                    </div>
                  </div>
                </div>
                <div v-else class="no-data">
                  <p>No surge prediction data available</p>
                </div>
              </div>
            </div>
          </q-card>
        </div>
      </div>

      <!-- Analytics Data Display Section -->
      <div class="analytics-section">
        <q-card class="analytics-card">
          <q-card-section class="analytics-header">
            <h3 class="analytics-title">REAL-TIME ANALYTICS INSIGHTS</h3>
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
          </q-card-section>

          <q-card-section class="analytics-content">
            <!-- Analytics Panels -->
            <div class="analytics-panels-container">
              <!-- Demographics Panel -->
              <div class="analytics-panel demographics-panel">
                <h4 class="panel-title">Patient Demographics</h4>
                <div class="panel-content">
                  <div v-if="analyticsData.patient_demographics" class="analytics-data">
                    <!-- Age Distribution Chart -->
                    <div class="chart-container">
                      <canvas ref="ageChart" width="400" height="200"></canvas>
                    </div>

                    <!-- Gender Distribution Chart -->
                    <div class="chart-container">
                      <canvas ref="genderChart" width="400" height="200"></canvas>
                    </div>

                    <!-- Summary Statistics -->
                    <div class="summary-stats">
                      <div class="stat-item">
                        <span class="stat-label">Total Patients:</span>
                        <span class="stat-value">{{
                          analyticsData.patient_demographics.total_patients
                        }}</span>
                      </div>
                      <div class="stat-item">
                        <span class="stat-label">Average Age:</span>
                        <span class="stat-value"
                          >{{ analyticsData.patient_demographics.average_age }} years</span
                        >
                      </div>
                    </div>
                  </div>
                  <div v-else class="empty-data">
                    <p>No demographics data available</p>
                  </div>
                </div>
              </div>

              <!-- Health Trends Panel -->
              <div class="analytics-panel trends-panel">
                <h4 class="panel-title">Health Trends</h4>
                <div class="panel-content">
                  <div v-if="analyticsData.health_trends" class="analytics-data">
                    <!-- Top Conditions Chart -->
                    <div class="chart-container">
                      <canvas ref="trendsChart" width="400" height="200"></canvas>
                    </div>

                    <!-- Trend Analysis -->
                    <div class="trend-analysis">
                      <div class="trend-section">
                        <h5>Increasing Conditions:</h5>
                        <div class="trend-items">
                          <span
                            v-for="condition in analyticsData.health_trends.trend_analysis
                              ?.increasing_conditions"
                            :key="condition"
                            class="trend-item increasing"
                          >
                            {{ condition }}
                          </span>
                        </div>
                      </div>
                      <div class="trend-section">
                        <h5>Decreasing Conditions:</h5>
                        <div class="trend-items">
                          <span
                            v-for="condition in analyticsData.health_trends.trend_analysis
                              ?.decreasing_conditions"
                            :key="condition"
                            class="trend-item decreasing"
                          >
                            {{ condition }}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div v-else class="empty-data">
                    <p>No health trends data available</p>
                  </div>
                </div>
              </div>

              <!-- Illness Prediction Panel -->
              <div class="analytics-panel prediction-panel">
                <h4 class="panel-title">Illness Prediction Analysis</h4>
                <div class="panel-content">
                  <div v-if="analyticsData.illness_prediction" class="analytics-data">
                    <!-- Statistical Analysis Chart -->
                    <div class="chart-container">
                      <canvas ref="predictionChart" width="400" height="200"></canvas>
                    </div>

                    <!-- Statistical Summary -->
                    <div class="statistical-summary">
                      <div class="stat-row">
                        <div class="stat-card">
                          <div class="stat-icon">📊</div>
                          <div class="stat-content">
                            <div class="stat-title">Chi-Square Statistic</div>
                            <div class="stat-value">
                              {{ analyticsData.illness_prediction.chi_square_statistic }}
                            </div>
                          </div>
                        </div>

                        <div class="stat-card">
                          <div class="stat-icon">📈</div>
                          <div class="stat-content">
                            <div class="stat-title">P-Value</div>
                            <div class="stat-value">
                              {{ analyticsData.illness_prediction.p_value }}
                            </div>
                          </div>
                        </div>
                      </div>

                      <div class="analysis-result">
                        <h5>Analysis Result:</h5>
                        <p class="result-text">
                          {{ analyticsData.illness_prediction.association_result }}
                        </p>
                      </div>

                      <div
                        v-if="analyticsData.illness_prediction.significant_factors"
                        class="significant-factors"
                      >
                        <h5>Significant Factors:</h5>
                        <div class="factors-list">
                          <div
                            v-for="factor in analyticsData.illness_prediction.significant_factors"
                            :key="factor"
                            class="factor-item"
                          >
                            {{ factor }}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div v-else class="empty-data">
                    <p>No prediction data available</p>
                  </div>
                </div>
              </div>

              <!-- Surge Prediction Panel -->
              <div class="analytics-panel surge-panel">
                <h4 class="panel-title">Surge Prediction</h4>
                <div class="panel-content">
                  <div v-if="analyticsData.surge_prediction" class="analytics-data">
                    <!-- Surge Prediction Chart -->
                    <div class="chart-container">
                      <canvas ref="surgeChart" width="400" height="200"></canvas>
                    </div>

                    <!-- Model Accuracy -->
                    <div class="model-info">
                      <div class="accuracy-item">
                        <span class="accuracy-label">Model Accuracy:</span>
                        <span class="accuracy-value"
                          >{{ analyticsData.surge_prediction.model_accuracy }}%</span
                        >
                      </div>
                    </div>

                    <!-- Risk Factors -->
                    <div class="risk-factors">
                      <h5>Risk Factors:</h5>
                      <ul>
                        <li
                          v-for="factor in analyticsData.surge_prediction.risk_factors"
                          :key="factor"
                        >
                          {{ factor }}
                        </li>
                      </ul>
                    </div>
                  </div>
                  <div v-else class="empty-data">
                    <p>No surge prediction data available</p>
                  </div>
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <router-view />
    </q-page-container>

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
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import { useQuasar } from 'quasar';
import { api } from '../boot/axios';
import { Chart, registerables } from 'chart.js';
import DoctorHeader from '../components/DoctorHeader.vue';
import DoctorSidebar from '../components/DoctorSidebar.vue';

// Register Chart.js components
Chart.register(...registerables);

const $q = useQuasar();

const rightDrawerOpen = ref(false);
const showNotifications = ref(false);

// Chart refs
const ageChart = ref<HTMLCanvasElement | null>(null);
const genderChart = ref<HTMLCanvasElement | null>(null);
const trendsChart = ref<HTMLCanvasElement | null>(null);
const surgeChart = ref<HTMLCanvasElement | null>(null);
const predictionChart = ref<HTMLCanvasElement | null>(null);

// Chart instances
let ageChartInstance: Chart | null = null;
let genderChartInstance: Chart | null = null;
let trendsChartInstance: Chart | null = null;
let surgeChartInstance: Chart | null = null;
let predictionChartInstance: Chart | null = null;

// Analytics data interfaces
interface PatientDemographics {
  age_distribution?: { [key: string]: number };
  gender_proportions?: { [key: string]: number };
  total_patients?: number;
  average_age?: number;
}

interface IllnessPrediction {
  association_result?: string;
  chi_square_statistic?: number;
  p_value?: number;
  confidence_level?: number;
  significant_factors?: string[];
}

interface HealthTrends {
  top_illnesses_by_week?: Array<{
    medical_condition: string;
    count: number;
    date_of_admission: string;
  }>;
  trend_analysis?: {
    increasing_conditions?: string[];
    decreasing_conditions?: string[];
    stable_conditions?: string[];
  };
}

interface SurgePrediction {
  forecasted_monthly_cases?: Array<{
    date: string;
    total_cases: number;
  }>;
  model_accuracy?: number;
  risk_factors?: string[];
}

interface AnalyticsData {
  patient_demographics: PatientDemographics | null;
  illness_prediction: IllnessPrediction | null;
  health_trends: HealthTrends | null;
  surge_prediction: SurgePrediction | null;
}

// Analytics data
const analyticsData = ref<AnalyticsData>({
  patient_demographics: null,
  illness_prediction: null,
  health_trends: null,
  surge_prediction: null,
});

// Zoom functionality
const zoomedData = ref<{
  type: string | null;
  visible: boolean;
}>({
  type: null,
  visible: false,
});

// Real-time features are now handled by DoctorHeader component

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

// User profile data
const userProfile = ref<{
  full_name: string;
  specialization?: string;
  role: string;
  profile_picture: string | null;
  verification_status: string;
}>({
  full_name: 'Loading...',
  specialization: 'Loading specialization...',
  role: 'doctor',
  profile_picture: null,
  verification_status: 'not_submitted',
});

const currentDate = computed(() => {
  const now = new Date();
  return now.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
});



const fetchDoctorAnalytics = async () => {
  try {
    const response = await api.get('/analytics/doctor/');
    analyticsData.value = response.data.data;
    console.log('Doctor analytics loaded:', analyticsData.value);

    // Create charts after data is loaded
    await createAllCharts();
  } catch (error) {
    console.error('Failed to fetch doctor analytics:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to load analytics data',
      position: 'top',
      timeout: 3000,
    });
  }
};

const viewDemographics = () => {
  $q.notify({
    type: 'info',
    message: 'Viewing Patient Demographics...',
    position: 'top',
    timeout: 2000,
  });
};

/**
 * Shows notification when illness prediction card is clicked
 * @returns {void}
 *
 * How it works:
 * 1. Displays an info notification to the user
 * 2. Indicates that illness prediction analysis is being viewed
 * 3. Auto-dismisses after 2 seconds
 *
 * Future enhancement: Could navigate to detailed prediction view
 */
const viewIllnessPrediction = () => {
  $q.notify({
    type: 'info',
    message: 'Viewing Illness Prediction Analysis...',
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
 * Shows notification when surge prediction card is clicked
 * @returns {void}
 *
 * How it works:
 * 1. Displays an info notification to the user
 * 2. Indicates that surge prediction is being viewed
 * 3. Auto-dismisses after 2 seconds
 *
 * Future enhancement: Could navigate to detailed surge prediction view
 */
const viewSurgePrediction = () => {
  $q.notify({
    type: 'info',
    message: 'Viewing Surge Prediction...',
    position: 'top',
    timeout: 2000,
  });
};

/**
 * Generates and downloads a PDF report of doctor analytics
 * @returns {Promise<void>}
 *
 * How it works:
 * 1. Makes API call to /analytics/pdf/?type=doctor with blob response type
 * 2. Creates a Blob object from the response data
 * 3. Creates a temporary URL for the blob
 * 4. Creates a temporary anchor element for download
 * 5. Sets the filename with current date
 * 6. Programmatically clicks the anchor to trigger download
 * 7. Cleans up by removing the anchor and revoking the URL
 * 8. Shows success/error notifications
 *
 * The PDF contains comprehensive analytics data formatted for doctors
 */
const generatePDFReport = async () => {
  try {
    const response = await api.get('/analytics/pdf/?type=doctor', {
      responseType: 'blob',
    });

    const blob = new Blob([response.data], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `doctor_analytics_report_${new Date().toISOString().split('T')[0]}.pdf`;
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
 * 2. Calls fetchDoctorAnalytics to get latest data from API
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

  await fetchDoctorAnalytics();

  $q.notify({
    type: 'positive',
    message: 'Analytics data refreshed!',
    position: 'top',
    timeout: 2000,
  });
};

/**
 * Creates age distribution chart
 * @returns {void}
 *
 * How it works:
 * 1. Gets the canvas element for age chart
 * 2. Destroys existing chart if it exists
 * 3. Creates new Chart.js bar chart with age distribution data
 * 4. Uses responsive design and proper styling
 */
const createAgeChart = () => {
  if (!ageChart.value || !analyticsData.value.patient_demographics?.age_distribution) return;

  if (ageChartInstance) {
    ageChartInstance.destroy();
  }

  const ctx = ageChart.value.getContext('2d');
  if (!ctx) return;

  const data = analyticsData.value.patient_demographics.age_distribution;

  ageChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: Object.keys(data),
      datasets: [
        {
          label: 'Number of Patients',
          data: Object.values(data),
          backgroundColor: [
            'rgba(54, 162, 235, 0.8)',
            'rgba(255, 99, 132, 0.8)',
            'rgba(255, 205, 86, 0.8)',
            'rgba(75, 192, 192, 0.8)',
            'rgba(153, 102, 255, 0.8)',
          ],
          borderColor: [
            'rgba(54, 162, 235, 1)',
            'rgba(255, 99, 132, 1)',
            'rgba(255, 205, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)',
          ],
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: 'Patient Age Distribution',
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1,
          },
        },
      },
    },
  });
};

/**
 * Creates gender distribution chart
 * @returns {void}
 *
 * How it works:
 * 1. Gets the canvas element for gender chart
 * 2. Destroys existing chart if it exists
 * 3. Creates new Chart.js pie chart with gender distribution data
 * 4. Uses responsive design and proper styling
 */
const createGenderChart = () => {
  if (!genderChart.value || !analyticsData.value.patient_demographics?.gender_proportions) return;

  if (genderChartInstance) {
    genderChartInstance.destroy();
  }

  const ctx = genderChart.value.getContext('2d');
  if (!ctx) return;

  const data = analyticsData.value.patient_demographics.gender_proportions;

  genderChartInstance = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: Object.keys(data),
      datasets: [
        {
          data: Object.values(data),
          backgroundColor: ['rgba(54, 162, 235, 0.8)', 'rgba(255, 99, 132, 0.8)'],
          borderColor: ['rgba(54, 162, 235, 1)', 'rgba(255, 99, 132, 1)'],
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: 'Gender Distribution',
        },
      },
    },
  });
};

/**
 * Creates health trends chart
 * @returns {void}
 *
 * How it works:
 * 1. Gets the canvas element for trends chart
 * 2. Destroys existing chart if it exists
 * 3. Creates new Chart.js bar chart with top medical conditions data
 * 4. Uses responsive design and proper styling
 */
const createTrendsChart = () => {
  if (!trendsChart.value || !analyticsData.value.health_trends?.top_illnesses_by_week) return;

  if (trendsChartInstance) {
    trendsChartInstance.destroy();
  }

  const ctx = trendsChart.value.getContext('2d');
  if (!ctx) return;

  const data = analyticsData.value.health_trends.top_illnesses_by_week.slice(0, 5);

  trendsChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: data.map((item) => item.medical_condition),
      datasets: [
        {
          label: 'Number of Cases',
          data: data.map((item) => item.count),
          backgroundColor: 'rgba(75, 192, 192, 0.8)',
          borderColor: 'rgba(75, 192, 192, 1)',
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: 'Top Medical Conditions',
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1,
          },
        },
      },
    },
  });
};

/**
 * Creates surge prediction chart
 * @returns {void}
 *
 * How it works:
 * 1. Gets the canvas element for surge chart
 * 2. Destroys existing chart if it exists
 * 3. Creates new Chart.js line chart with forecasted cases data
 * 4. Uses responsive design and proper styling
 */
const createSurgeChart = () => {
  if (!surgeChart.value || !analyticsData.value.surge_prediction?.forecasted_monthly_cases) return;

  if (surgeChartInstance) {
    surgeChartInstance.destroy();
  }

  const ctx = surgeChart.value.getContext('2d');
  if (!ctx) return;

  const data = analyticsData.value.surge_prediction.forecasted_monthly_cases;

  surgeChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.map((item) => item.date),
      datasets: [
        {
          label: 'Forecasted Cases',
          data: data.map((item) => item.total_cases),
          borderColor: 'rgba(255, 99, 132, 1)',
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          borderWidth: 2,
          fill: true,
          tension: 0.4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: 'Surge Prediction Forecast',
        },
      },
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  });
};

/**
 * Creates illness prediction chart
 * @returns {void}
 *
 * How it works:
 * 1. Gets the canvas element for prediction chart
 * 2. Destroys existing chart if it exists
 * 3. Creates new Chart.js radar chart with statistical data
 * 4. Uses responsive design and proper styling
 */
const createPredictionChart = () => {
  if (!predictionChart.value || !analyticsData.value.illness_prediction) return;

  if (predictionChartInstance) {
    predictionChartInstance.destroy();
  }

  const ctx = predictionChart.value.getContext('2d');
  if (!ctx) return;

  const data = analyticsData.value.illness_prediction;

  // Create a radar chart showing statistical confidence
  const confidenceData = [
    data.confidence_level || 95,
    (1 - (data.p_value || 0.05)) * 100, // Convert p-value to confidence
    Math.min((data.chi_square_statistic || 0) / 10, 100), // Normalize chi-square
    85, // Model accuracy (assumed)
    90, // Data quality (assumed)
  ];

  predictionChartInstance = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: [
        'Confidence Level',
        'Statistical Significance',
        'Chi-Square Strength',
        'Model Accuracy',
        'Data Quality',
      ],
      datasets: [
        {
          label: 'Statistical Analysis',
          data: confidenceData,
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          borderColor: 'rgba(255, 99, 132, 1)',
          borderWidth: 2,
          pointBackgroundColor: 'rgba(255, 99, 132, 1)',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgba(255, 99, 132, 1)',
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: 'Statistical Analysis Overview',
        },
      },
      scales: {
        r: {
          beginAtZero: true,
          max: 100,
          ticks: {
            stepSize: 20,
          },
        },
      },
    },
  });
};

const createAllCharts = async () => {
  await nextTick();

  try {
    createAgeChart();
    createGenderChart();
    createTrendsChart();
    createSurgeChart();
    createPredictionChart();
  } catch (error) {
    console.error('Error creating charts:', error);
  }
};


const loadNotifications = async (): Promise<void> => {
  try {
    console.log('📬 Loading doctor notifications...');

    const response = await api.get('/operations/notifications/');
    notifications.value = response.data || [];

    console.log('✅ Doctor notifications loaded:', notifications.value.length);
  } catch (error: unknown) {
    console.error('❌ Error loading doctor notifications:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to load notifications',
    });
  }
};

const handleNotificationClick = (notification: Notification): void => {
  // Mark as read
  notification.is_read = true;

  // Update on backend
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

const formatTime = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });
};

onMounted(() => {
  // Load notifications
  void loadNotifications();

  // Refresh notifications every 30 seconds
  setInterval(() => void loadNotifications(), 30000);
});

onUnmounted(() => {
 
});
</script>

<style scoped>
/* Safe Area Support */
.safe-area-top {
  padding-top: env(safe-area-inset-top);
}

.safe-area-bottom {
  padding-bottom: env(safe-area-inset-bottom);
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
  font-size: 14px;
}

/* Prototype Sidebar Styles */
.prototype-sidebar {
  background: white;
  border-right: 1px solid #e0e0e0;
}

.sidebar-content {
  height: 100%;
  display: flex;
  flex-direction: column;
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

.upload-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  transform: translate(25%, 25%);
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

/* Page Container with Off-White Background */
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
  max-width: 1200px;
  margin: 0 auto;
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
.demographics-card .card-icon {
  color: #2196f3;
}
.prediction-card .card-icon {
  color: #ff9800;
}
.trends-card .card-icon {
  color: #4caf50;
}
.surge-card .card-icon {
  color: #f44336;
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

.gender-stats,
.conditions-list,
.trend-items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.gender-item,
.condition-item {
  background: rgba(40, 102, 96, 0.1);
  color: #286660;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.trend-item {
  background: rgba(76, 175, 80, 0.1);
  color: #4caf50;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.trend-item.increasing {
  background: rgba(76, 175, 80, 0.1);
  color: #4caf50;
}

.risk-factors {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.risk-item {
  background: rgba(244, 67, 54, 0.1);
  color: #f44336;
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
}

.analytics-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.05);
  max-width: 1200px;
  margin: 0 auto;
}

.analytics-header {
  text-align: center;
  margin-bottom: 32px;
  padding: 24px 24px 0 24px;
}

.analytics-content {
  padding: 0 24px 24px 24px;
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
}

.analytics-panel {
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e9ecef;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 20px;
  min-height: 300px;
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
}

/* Chart Styles */
.chart-container {
  position: relative;
  height: 300px;
  margin: 20px 0;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 15px;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-top: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 15px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  text-align: center;
}

.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 5px;
}

.stat-value {
  font-size: 18px;
  font-weight: bold;
  color: #286660;
}

.trend-analysis {
  margin-top: 20px;
}

.trend-section {
  margin-bottom: 15px;
}

.trend-section h5 {
  color: #286660;
  margin-bottom: 10px;
  font-size: 14px;
}

.trend-items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.trend-item {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.trend-item.increasing {
  background: rgba(255, 99, 132, 0.2);
  color: #ff6384;
  border: 1px solid rgba(255, 99, 132, 0.3);
}

.trend-item.decreasing {
  background: rgba(75, 192, 192, 0.2);
  color: #4bc0c0;
  border: 1px solid rgba(75, 192, 192, 0.3);
}

.model-info {
  margin-top: 15px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.accuracy-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.accuracy-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.accuracy-value {
  font-size: 16px;
  font-weight: bold;
  color: #286660;
}

.risk-factors {
  margin-top: 15px;
}

.risk-factors h5 {
  color: #286660;
  margin-bottom: 10px;
  font-size: 14px;
}

.risk-factors ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.risk-factors li {
  padding: 8px 12px;
  margin: 5px 0;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
  border-left: 3px solid #ff6384;
}

/* Statistical Summary Styles */
.statistical-summary {
  margin-top: 20px;
}

.stat-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 15px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.stat-card:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 24px;
  margin-right: 15px;
}

.stat-content {
  flex: 1;
}

.stat-title {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 5px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 18px;
  font-weight: bold;
  color: #286660;
}

.analysis-result {
  margin: 20px 0;
  padding: 15px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  border-left: 4px solid #286660;
}

.analysis-result h5 {
  color: #286660;
  margin-bottom: 10px;
  font-size: 14px;
}

.result-text {
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  line-height: 1.5;
  margin: 0;
}

.significant-factors {
  margin-top: 15px;
}

.significant-factors h5 {
  color: #286660;
  margin-bottom: 10px;
  font-size: 14px;
}

.factors-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.factor-item {
  padding: 6px 12px;
  background: rgba(40, 102, 96, 0.2);
  color: #286660;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid rgba(40, 102, 96, 0.3);
}

/* Responsive Chart Styles */
@media (max-width: 768px) {
  .chart-container {
    height: 250px;
    margin: 15px 0;
    padding: 10px;
  }

  .summary-stats {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .stat-item {
    padding: 10px;
  }

  .trend-items {
    flex-direction: column;
  }

  .stat-row {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .stat-card {
    padding: 12px;
  }

  .factors-list {
    flex-direction: column;
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

/* Desktop Layout - Show desktop header, hide mobile */
@media (min-width: 769px) {
  .mobile-header-layout {
    display: none;
  }

  .prototype-header .header-toolbar {
    display: flex;
  }
}

/* Mobile Layout - Hide desktop header, show mobile */
@media (max-width: 768px) {
  .prototype-header {
    padding-top: max(env(safe-area-inset-top), 8px);
  }

  .header-toolbar {
    display: none;
  }

  .mobile-header-layout {
    padding: 8px 12px;
    padding-top: max(env(safe-area-inset-top), 8px);
  }

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
}

@media (max-width: 480px) {
  .prototype-header {
    padding-top: max(env(safe-area-inset-top), 12px);
  }

  .mobile-header-layout {
    padding: 6px 8px;
    padding-top: max(env(safe-area-inset-top), 12px);
  }

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
