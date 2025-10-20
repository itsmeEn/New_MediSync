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
    <NurseSidebar v-model="rightDrawerOpen" :activeRoute="'nurse-medicine-inventory'" />

    <q-page-container class="page-container-with-fixed-header">
      <!-- Greeting Section -->
      <div class="greeting-section">
        <q-card class="greeting-card">
          <q-card-section class="greeting-content">
            <h2 class="greeting-text">Medicine Inventory</h2>
            <p class="greeting-subtitle">
              Track and manage your medicine stock, monitor expiry dates, and ensure adequate supply
              for patient care - {{ currentDate }}
            </p>
          </q-card-section>
        </q-card>
      </div>

      <div class="page-content">
        <!-- Search and Filters -->
        <q-card class="search-filters-card">
          <q-card-section>
            <div class="row q-gutter-md items-center">
              <div class="col-12 col-md-4">
                <q-input
                  v-model="searchQuery"
                  placeholder="Search medicines..."
                  outlined
                  dense
                  clearable
                >
                  <template v-slot:prepend>
                    <q-icon name="search" />
                  </template>
                </q-input>
              </div>
              <div class="col-12 col-md-3">
                <q-select
                  v-model="categoryFilter"
                  :options="medicineCategories"
                  label="Category"
                  outlined
                  dense
                  clearable
                  emit-value
                  map-options
                />
              </div>
              <div class="col-12 col-md-3">
                <q-select
                  v-model="stockFilter"
                  :options="stockLevels"
                  label="Stock Level"
                  outlined
                  dense
                  clearable
                  emit-value
                  map-options
                />
              </div>
              <div class="col-12 col-md-2">
                <q-btn
                  color="secondary"
                  label="Filter"
                  icon="filter_list"
                  @click="applyFilters"
                  class="full-width"
                />
              </div>
              <div class="col-12 col-md-2">
                <q-btn
                  color="primary"
                  label="Add Medicine"
                  icon="add"
                  @click="handleAddMedicineClick"
                  :disable="!isUserVerified"
                  class="full-width"
                />
                <q-tooltip v-if="!isUserVerified">
                  Account verification required to manage medicine inventory
                </q-tooltip>
              </div>
            </div>
          </q-card-section>
        </q-card>

        <!-- Inventory Statistics -->
        <div class="stats-section">
          <div class="stats-grid">
            <q-card class="stat-card total-medicines">
              <q-card-section class="text-center">
                <div class="stat-icon">
                  <q-icon name="medication" size="2rem" />
                </div>
                <div class="stat-number">{{ inventoryStats.totalMedicines }}</div>
                <div class="stat-label">Total Medicines</div>
              </q-card-section>
            </q-card>

            <q-card class="stat-card low-stock">
              <q-card-section class="text-center">
                <div class="stat-icon">
                  <q-icon name="warning" size="2rem" />
                </div>
                <div class="stat-number">{{ inventoryStats.lowStock }}</div>
                <div class="stat-label">Low Stock Items</div>
              </q-card-section>
            </q-card>

            <q-card class="stat-card out-of-stock">
              <q-card-section class="text-center">
                <div class="stat-icon">
                  <q-icon name="error" size="2rem" />
                </div>
                <div class="stat-number">{{ inventoryStats.outOfStock }}</div>
                <div class="stat-label">Out of Stock</div>
              </q-card-section>
            </q-card>

            <q-card class="stat-card expiring-soon">
              <q-card-section class="text-center">
                <div class="stat-icon">
                  <q-icon name="schedule" size="2rem" />
                </div>
                <div class="stat-number">{{ inventoryStats.expiringSoon }}</div>
                <div class="stat-label">Expiring Soon</div>
              </q-card-section>
            </q-card>
          </div>
        </div>

        <!-- Medicine Inventory Table -->
        <q-card class="inventory-table-card">
          <q-card-section>
            <div class="row items-center q-mb-md">
              <h6 class="text-h6 q-mb-none">Medicine Inventory</h6>
              <q-space />
              <q-btn
                color="primary"
                label="Export"
                icon="download"
                size="sm"
                @click="exportInventory"
              />
            </div>

            <q-table
              :rows="filteredMedicines"
              :columns="columns"
              row-key="id"
              :pagination="pagination"
              :loading="loading"
              class="inventory-table"
            >
              <!-- Stock Level Column -->
              <template v-slot:body-cell-stockLevel="props">
                <q-td :props="props">
                  <q-chip
                    :color="getStockLevelColor(props.value)"
                    text-color="white"
                    :label="props.value"
                    size="sm"
                  />
                </q-td>
              </template>

              <!-- Expiry Date Column -->
              <template v-slot:body-cell-expiryDate="props">
                <q-td :props="props">
                  <span :class="getExpiryDateClass(props.value)">
                    {{ formatDate(props.value) }}
                  </span>
                </q-td>
              </template>

              <!-- Actions Column -->
              <template v-slot:body-cell-actions="props">
                <q-td :props="props">
                  <div class="row q-gutter-xs">
                    <q-btn
                      round
                      flat
                      dense
                      color="primary"
                      icon="edit"
                      @click="editMedicine(props.row)"
                      size="sm"
                    >
                      <q-tooltip>Edit Medicine</q-tooltip>
                    </q-btn>
                    <q-btn
                      round
                      flat
                      dense
                      color="secondary"
                      icon="inventory"
                      @click="dispenseMedicine(props.row)"
                      size="sm"
                    >
                      <q-tooltip>Dispense</q-tooltip>
                    </q-btn>
                    <q-btn
                      round
                      flat
                      dense
                      color="accent"
                      icon="add_shopping_cart"
                      @click="restockMedicine(props.row)"
                      size="sm"
                    >
                      <q-tooltip>Restock</q-tooltip>
                    </q-btn>
                  </div>
                </q-td>
              </template>
            </q-table>
          </q-card-section>
        </q-card>

        <!-- Notifications Panel -->
        <q-card class="notifications-card q-mt-lg" v-if="notifications.length > 0">
          <q-card-section>
            <div class="row items-center q-mb-md">
              <h6 class="text-h6 q-mb-none">Stock Alerts & Notifications</h6>
              <q-space />
              <q-btn
                color="primary"
                label="Mark All Read"
                icon="check_all"
                size="sm"
                @click="markAllNotificationsRead"
              />
            </div>

            <div class="notifications-list">
              <div
                v-for="notification in notifications"
                :key="notification.id"
                class="notification-item"
                :class="{ unread: !notification.isRead, read: notification.isRead }"
                @click="viewNotification(notification)"
              >
                <div class="notification-icon">
                  <q-icon
                    :name="getNotificationIcon(notification.type)"
                    :color="getNotificationColor(notification.type)"
                    size="md"
                  />
                </div>
                <div class="notification-content">
                  <div class="notification-message">{{ notification.message }}</div>
                  <div class="notification-time">
                    {{ formatNotificationTime(notification.timestamp) }}
                  </div>
                </div>
                <div class="notification-actions">
                  <q-btn
                    round
                    flat
                    dense
                    color="primary"
                    icon="visibility"
                    @click.stop="viewNotification(notification)"
                    size="sm"
                  >
                    <q-tooltip>View Details</q-tooltip>
                  </q-btn>
                  <q-btn
                    round
                    flat
                    dense
                    color="positive"
                    icon="check"
                    @click.stop="markNotificationRead(notification)"
                    size="sm"
                    v-if="!notification.isRead"
                  >
                    <q-tooltip>Mark as Read</q-tooltip>
                  </q-btn>
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Add/Edit Medicine Dialog -->
      <q-dialog v-model="showAddDialog" persistent>
        <q-card class="medicine-modal">
          <q-card-section class="modal-header">
            <div class="modal-title">
              <q-icon name="medication" size="md" class="title-icon" />
              {{ editingMedicine ? 'Edit Medicine' : 'Add New Medicine' }}
            </div>
            <q-btn flat round icon="close" @click="cancelEdit" class="close-btn" />
          </q-card-section>

          <q-card-section class="modal-content">
            <div class="form-fields">
              <div class="form-row">
                <q-input
                  v-model="medicineForm.name"
                  label="Medicine Name"
                  outlined
                  class="form-input"
                  :rules="[(val) => !!val || 'Name is required']"
                />
              </div>
              <div class="form-row">
                <q-input
                  v-model="medicineForm.genericName"
                  label="Generic Name"
                  outlined
                  class="form-input"
                />
              </div>
              <div class="form-row">
                <q-select
                  v-model="medicineForm.category"
                  :options="medicineCategories"
                  label="Category"
                  outlined
                  class="form-input"
                  emit-value
                  map-options
                  :rules="[(val) => !!val || 'Category is required']"
                />
              </div>
              <div class="form-row">
                <q-input
                  v-model="medicineForm.dosage"
                  label="Dosage Form"
                  outlined
                  class="form-input"
                  placeholder="e.g., Tablet, Syrup, Injection"
                />
              </div>
              <div class="form-row">
                <q-input
                  v-model.number="medicineForm.strength"
                  label="Strength"
                  outlined
                  class="form-input"
                  placeholder="e.g., 500mg, 10ml"
                />
              </div>
              <div class="form-row">
                <q-input
                  v-model.number="medicineForm.quantity"
                  label="Quantity"
                  type="number"
                  outlined
                  class="form-input"
                  :rules="[(val) => val >= 0 || 'Quantity must be non-negative']"
                />
              </div>
              <div class="form-row">
                <q-input
                  v-model="medicineForm.unit"
                  label="Unit"
                  outlined
                  class="form-input"
                  placeholder="e.g., tablets, bottles, vials"
                />
              </div>
              <div class="form-row">
                <q-input
                  v-model="medicineForm.expiryDate"
                  label="Expiry Date"
                  type="date"
                  outlined
                  class="form-input"
                  :rules="[(val) => !!val || 'Expiry date is required']"
                />
              </div>
              <div class="form-row">
                <q-input
                  v-model.number="medicineForm.minStockLevel"
                  label="Minimum Stock Level"
                  type="number"
                  outlined
                  class="form-input"
                  :rules="[(val) => val >= 0 || 'Minimum stock must be non-negative']"
                />
              </div>
              <div class="form-row">
                <q-input
                  v-model.number="medicineForm.unitPrice"
                  label="Unit Price"
                  type="number"
                  outlined
                  class="form-input"
                  placeholder="0.00"
                  step="0.01"
                  :rules="[(val) => val >= 0 || 'Unit price must be non-negative']"
                />
              </div>
              <div class="form-row">
                <q-input
                  v-model="medicineForm.batchNumber"
                  label="Batch Number"
                  outlined
                  class="form-input"
                  placeholder="e.g., BATCH-2024-001"
                />
              </div>
              <div class="form-row">
                <q-input
                  v-model="medicineForm.description"
                  label="Description"
                  type="textarea"
                  outlined
                  class="form-input"
                  rows="3"
                />
              </div>
            </div>
          </q-card-section>

          <q-card-actions class="modal-actions">
            <q-btn flat label="Cancel" color="grey-7" @click="cancelEdit" class="cancel-btn" />
            <q-btn
              :label="editingMedicine ? 'Update Medicine' : 'Add Medicine'"
              color="primary"
              @click="saveMedicine"
              :loading="saving"
              class="save-btn"
              icon="save"
            />
          </q-card-actions>
        </q-card>
      </q-dialog>

      <!-- Dispense Medicine Dialog -->
      <q-dialog v-model="showDispenseDialog" persistent>
        <q-card style="min-width: 400px">
          <q-card-section>
            <div class="text-h6">Dispense Medicine</div>
          </q-card-section>

          <q-card-section>
            <div class="row q-gutter-md">
              <div class="col-12">
                <q-input
                  v-model="dispenseForm.patientName"
                  label="Patient Name"
                  outlined
                  :rules="[(val) => !!val || 'Patient name is required']"
                />
              </div>
              <div class="col-12 col-md-6">
                <q-input
                  v-model.number="dispenseForm.quantity"
                  label="Quantity to Dispense"
                  type="number"
                  outlined
                  :rules="[
                    (val) => !!val || 'Quantity is required',
                    (val) => val <= (selectedMedicine?.quantity || 0) || 'Insufficient stock',
                  ]"
                />
              </div>
              <div class="col-12 col-md-6">
                <q-input
                  v-model="dispenseForm.dosage"
                  label="Dosage Instructions"
                  outlined
                  placeholder="e.g., 1 tablet twice daily"
                />
              </div>
              <div class="col-12">
                <q-input
                  v-model="dispenseForm.notes"
                  label="Notes"
                  type="textarea"
                  outlined
                  rows="3"
                />
              </div>
            </div>
          </q-card-section>

          <q-card-actions align="right">
            <q-btn flat label="Cancel" color="primary" @click="cancelDispense" />
            <q-btn
              label="Dispense"
              color="primary"
              @click="confirmDispense"
              :loading="dispensing"
            />
          </q-card-actions>
        </q-card>
      </q-dialog>

      <!-- Restock Medicine Dialog -->
      <q-dialog v-model="showRestockDialog" persistent>
        <q-card style="min-width: 400px">
          <q-card-section>
            <div class="text-h6">Restock Medicine</div>
          </q-card-section>

          <q-card-section>
            <div class="row q-gutter-md">
              <div class="col-12 col-md-6">
                <q-input
                  v-model.number="restockForm.quantity"
                  label="Quantity to Add"
                  type="number"
                  outlined
                  :rules="[(val) => val > 0 || 'Quantity must be positive']"
                />
              </div>
              <div class="col-12 col-md-6">
                <q-input
                  v-model="restockForm.expiryDate"
                  label="New Expiry Date"
                  type="date"
                  outlined
                  :rules="[(val) => !!val || 'Expiry date is required']"
                />
              </div>
              <div class="col-12">
                <q-input v-model="restockForm.supplier" label="Supplier" outlined />
              </div>
              <div class="col-12">
                <q-input
                  v-model="restockForm.notes"
                  label="Notes"
                  type="textarea"
                  outlined
                  rows="3"
                />
              </div>
            </div>
          </q-card-section>

          <q-card-actions align="right">
            <q-btn flat label="Cancel" color="primary" @click="cancelRestock" />
            <q-btn label="Restock" color="primary" @click="confirmRestock" :loading="restocking" />
          </q-card-actions>
        </q-card>
      </q-dialog>

      <!-- Notification Detail Dialog -->
      <q-dialog v-model="showNotificationDialog" persistent>
        <q-card style="min-width: 500px">
          <q-card-section>
            <div class="text-h6">Notification Details</div>
          </q-card-section>

          <q-card-section v-if="selectedNotification">
            <div class="notification-detail">
              <div class="notification-header">
                <q-icon
                  :name="getNotificationIcon(selectedNotification.type)"
                  :color="getNotificationColor(selectedNotification.type)"
                  size="2rem"
                />
                <div class="notification-title">
                  {{ selectedNotification.medicineName }}
                </div>
              </div>

              <div class="notification-message">
                {{ selectedNotification.message }}
              </div>

              <div class="notification-time">
                {{ formatNotificationTime(selectedNotification.timestamp) }}
              </div>

              <div class="notification-actions q-mt-md">
                <q-btn
                  color="primary"
                  label="View Medicine"
                  icon="visibility"
                  @click="viewMedicineFromNotification"
                />
                <q-btn
                  color="secondary"
                  label="Restock"
                  icon="add_shopping_cart"
                  @click="restockFromNotification"
                />
              </div>
            </div>
          </q-card-section>

          <q-card-actions align="right">
            <q-btn flat label="Close" color="primary" @click="showNotificationDialog = false" />
          </q-card-actions>
        </q-card>
      </q-dialog>
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useQuasar } from 'quasar';
import { api } from 'src/boot/axios';
import NurseHeader from 'src/components/NurseHeader.vue';
import NurseSidebar from 'src/components/NurseSidebar.vue';
import { showVerificationToastOnce } from 'src/utils/verificationToast';

const $q = useQuasar();

// Sidebar and navigation
const rightDrawerOpen = ref(false);

// Search functionality
const searchText = ref('');
const searchResults = ref<
  {
    id: string;
    type: string;
    title: string;
    subtitle: string;
    data: Record<string, string | number>;
  }[]
>([]);

// Notification system
const showNotifications = ref(false);
const unreadNotificationsCount = ref(0);

// Location data
const locationData = ref<{
  city: string;
  region: string;
  country: string;
} | null>(null);
const locationLoading = ref(false);
const locationError = ref(false);

// Time and weather
const currentTime = ref('');
const currentDate = computed(() => {
  const now = new Date();
  return now.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
});
const weatherData = ref<{
  temperature: number;
  condition: string;
  location: string;
} | null>(null);
const weatherLoading = ref(false);
const weatherError = ref(false);
let timeInterval: NodeJS.Timeout | null = null;


// User verification
const userProfile = ref<{
  first_name?: string;
  last_name?: string;
  full_name?: string;
  role?: string;
  is_verified?: boolean;
  verification_status?: string;
  profile_picture?: string | null;
  email?: string;
}>({});

const isUserVerified = computed(() => {
  return userProfile.value.verification_status === 'approved';
});



// Page state
const loading = ref(false);
const saving = ref(false);
const dispensing = ref(false);
const restocking = ref(false);

// Notification system
const notifications = ref<
  {
    id: number;
    type: 'low_stock' | 'expiring_soon' | 'out_of_stock';
    message: string;
    medicineName: string;
    timestamp: Date;
    isRead: boolean;
  }[]
>([]);

// Notification interface
interface Notification {
  id: number;
  type: 'low_stock' | 'out_of_stock' | 'expiring_soon';
  message: string;
  medicineName: string;
  timestamp: Date;
  isRead: boolean;
}

// Show notification dialog
const showNotificationDialog = ref(false);
const selectedNotification = ref<Notification | null>(null);

// Search and filters
const searchQuery = ref('');
const categoryFilter = ref(null);
const stockFilter = ref(null);

// Dialog states
const showAddDialog = ref(false);
const showDispenseDialog = ref(false);
const showRestockDialog = ref(false);

// Form data
const editingMedicine = ref<Medicine | null>(null);
const selectedMedicine = ref<Medicine | null>(null);

const medicineForm = ref({
  name: '',
  genericName: '',
  category: '',
  dosage: '',
  strength: '',
  quantity: 0,
  unit: '',
  expiryDate: '',
  minStockLevel: 0,
  description: '',
  unitPrice: 0,
  batchNumber: '',
});

const dispenseForm = ref({
  patientName: '',
  quantity: 0,
  dosage: '',
  notes: '',
});

const restockForm = ref({
  quantity: 0,
  expiryDate: '',
  supplier: '',
  notes: '',
});

// Table pagination
const pagination = ref({
  sortBy: 'name',
  descending: false,
  page: 1,
  rowsPerPage: 10,
});

// Options for dropdowns
const medicineCategories = [
  { label: 'Analgesics', value: 'analgesics' },
  { label: 'Antibiotics', value: 'antibiotics' },
  { label: 'Antihypertensives', value: 'antihypertensives' },
  { label: 'Antidiabetics', value: 'antidiabetics' },
  { label: 'Cardiovascular', value: 'cardiovascular' },
  { label: 'Respiratory', value: 'respiratory' },
  { label: 'Gastrointestinal', value: 'gastrointestinal' },
  { label: 'Psychiatric', value: 'psychiatric' },
  { label: 'Other', value: 'other' },
];

const stockLevels = [
  { label: 'In Stock', value: 'in_stock' },
  { label: 'Low Stock', value: 'low_stock' },
  { label: 'Out of Stock', value: 'out_of_stock' },
];

// Table columns
const columns = [
  {
    name: 'name',
    required: true,
    label: 'Medicine Name',
    align: 'left' as const,
    field: 'name',
    sortable: true,
  },
  {
    name: 'category',
    label: 'Category',
    align: 'left' as const,
    field: 'category',
    sortable: true,
  },
  {
    name: 'strength',
    label: 'Strength',
    align: 'left' as const,
    field: 'strength',
  },
  {
    name: 'quantity',
    label: 'Quantity',
    align: 'center' as const,
    field: 'quantity',
    sortable: true,
  },
  {
    name: 'stockLevel',
    label: 'Stock Level',
    align: 'center' as const,
    field: 'stockLevel',
  },
  {
    name: 'expiryDate',
    label: 'Expiry Date',
    align: 'center' as const,
    field: 'expiryDate',
    sortable: true,
  },
  {
    name: 'actions',
    label: 'Actions',
    align: 'center' as const,
    field: 'actions',
  },
];

// Empty inventory data - nurses will input their stock
const medicines = ref<Medicine[]>([]);

// Computed properties
const filteredMedicines = computed(() => {
  let filtered = medicines.value;

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(
      (medicine) =>
        medicine.name.toLowerCase().includes(query) ||
        medicine.genericName.toLowerCase().includes(query),
    );
  }

  // Category filter
  if (categoryFilter.value) {
    filtered = filtered.filter((medicine) => medicine.category === categoryFilter.value);
  }

  // Stock level filter
  if (stockFilter.value) {
    filtered = filtered.filter((medicine) => medicine.stockLevel === stockFilter.value);
  }

  return filtered;
});

const inventoryStats = computed(() => {
  const total = medicines.value.length;
  const lowStock = medicines.value.filter((m) => m.stockLevel === 'low_stock').length;
  const outOfStock = medicines.value.filter((m) => m.stockLevel === 'out_of_stock').length;
  const expiringSoon = medicines.value.filter((m) => {
    const expiryDate = new Date(m.expiryDate);
    const today = new Date();
    const daysUntilExpiry = Math.ceil(
      (expiryDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24),
    );
    return daysUntilExpiry <= 30 && daysUntilExpiry > 0;
  }).length;

  return {
    totalMedicines: total,
    lowStock,
    outOfStock,
    expiringSoon,
  };
});

// Methods

const handleAddMedicineClick = () => {
  if (!isUserVerified.value) {
    $q.notify({
      type: 'warning',
      message:
        'Account verification required to manage medicine inventory. Please complete verification first.',
      position: 'top',
      timeout: 4000,
    });
    return;
  }
  showAddDialog.value = true;
};

const applyFilters = () => {
  // Filters are applied automatically through computed property
  console.log('Filters applied');
};

const getStockLevelColor = (level: string) => {
  switch (level) {
    case 'in_stock':
      return 'positive';
    case 'low_stock':
      return 'warning';
    case 'out_of_stock':
      return 'negative';
    default:
      return 'grey';
  }
};

const getExpiryDateClass = (date: string) => {
  const expiryDate = new Date(date);
  const today = new Date();
  const daysUntilExpiry = Math.ceil(
    (expiryDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24),
  );

  if (daysUntilExpiry < 0) return 'text-negative';
  if (daysUntilExpiry <= 30) return 'text-warning';
  return 'text-positive';
};

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString();
};

interface Medicine {
  id: number;
  name: string;
  genericName: string;
  category: string;
  dosage: string;
  strength: string;
  quantity: number;
  unit: string;
  expiryDate: string;
  minStockLevel: number;
  description: string;
  stockLevel: string;
  unitPrice?: number;
  batchNumber?: string;
}

// Search result interfaces
interface MedicineSearchResult {
  id: number | string;
  medicine_name?: string;
  name?: string;
  stock_quantity?: number;
  current_stock?: number;
  manufacturer?: string;
}

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

const editMedicine = (medicine: Medicine) => {
  editingMedicine.value = medicine;
  medicineForm.value = {
    name: medicine.name,
    genericName: medicine.genericName,
    category: medicine.category,
    dosage: medicine.dosage,
    strength: medicine.strength,
    quantity: medicine.quantity,
    unit: medicine.unit,
    expiryDate: medicine.expiryDate,
    minStockLevel: medicine.minStockLevel,
    description: medicine.description,
    unitPrice: medicine.unitPrice || 0,
    batchNumber: medicine.batchNumber || '',
  };
  showAddDialog.value = true;
};

const dispenseMedicine = (medicine: Medicine) => {
  selectedMedicine.value = medicine;
  dispenseForm.value = {
    patientName: '',
    quantity: 0,
    dosage: '',
    notes: '',
  };
  showDispenseDialog.value = true;
};

const restockMedicine = (medicine: Medicine) => {
  selectedMedicine.value = medicine;
  restockForm.value = {
    quantity: 0,
    expiryDate: '',
    supplier: '',
    notes: '',
  };
  showRestockDialog.value = true;
};

const cancelEdit = () => {
  editingMedicine.value = null;
  medicineForm.value = {
    name: '',
    genericName: '',
    category: '',
    dosage: '',
    strength: '',
    quantity: 0,
    unit: '',
    expiryDate: '',
    minStockLevel: 0,
    description: '',
    unitPrice: 0,
    batchNumber: '',
  };
  showAddDialog.value = false;
};

// Function to check stock levels and generate notifications
const checkStockLevels = () => {
  const today = new Date();
  const thirtyDaysFromNow = new Date(today.getTime() + 30 * 24 * 60 * 60 * 1000);

  medicines.value.forEach((medicine) => {
    // Check for low stock
    if (medicine.quantity <= medicine.minStockLevel && medicine.quantity > 0) {
      const existingNotification = notifications.value.find(
        (n) => n.medicineName === medicine.name && n.type === 'low_stock' && !n.isRead,
      );

      if (!existingNotification) {
        notifications.value.unshift({
          id: Date.now(),
          type: 'low_stock',
          message: `${medicine.name} is running low on stock. Current quantity: ${medicine.quantity} ${medicine.unit}`,
          medicineName: medicine.name,
          timestamp: new Date(),
          isRead: false,
        });
      }
    }

    // Check for out of stock
    if (medicine.quantity === 0) {
      const existingNotification = notifications.value.find(
        (n) => n.medicineName === medicine.name && n.type === 'out_of_stock' && !n.isRead,
      );

      if (!existingNotification) {
        notifications.value.unshift({
          id: Date.now(),
          type: 'out_of_stock',
          message: `${medicine.name} is out of stock. Please restock immediately.`,
          medicineName: medicine.name,
          timestamp: new Date(),
          isRead: false,
        });
      }
    }

    // Check for expiring soon (within 30 days)
    const expiryDate = new Date(medicine.expiryDate);
    if (expiryDate <= thirtyDaysFromNow && expiryDate >= today) {
      const daysUntilExpiry = Math.ceil(
        (expiryDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24),
      );

      const existingNotification = notifications.value.find(
        (n) => n.medicineName === medicine.name && n.type === 'expiring_soon' && !n.isRead,
      );

      if (!existingNotification) {
        notifications.value.unshift({
          id: Date.now(),
          type: 'expiring_soon',
          message: `${medicine.name} will expire in ${daysUntilExpiry} days. Current quantity: ${medicine.quantity} ${medicine.unit}`,
          medicineName: medicine.name,
          timestamp: new Date(),
          isRead: false,
        });
      }
    }
  });
};

const saveMedicine = async () => {
  saving.value = true;

  try {
    if (editingMedicine.value) {
      // Update existing medicine
      const response = await api.put(
        `/operations/medicine-inventory/${editingMedicine.value.id}/update/`,
        {
          name: medicineForm.value.name,
          quantity: medicineForm.value.quantity,
          //unit_price: medicineForm.value.unitPrice || 0,
          minimum_stock_level: medicineForm.value.minStockLevel,
          expiry_date: medicineForm.value.expiryDate,
          //batch_number: medicineForm.value.batchNumber || `BATCH-${Date.now()}`,
          usage_pattern: medicineForm.value.description || '',
        },
      );

      // Update local state with backend response
      const index = medicines.value.findIndex((m) => m.id === editingMedicine.value?.id);
      if (index !== -1 && editingMedicine.value && medicines.value[index]) {
        const currentMedicine = medicines.value[index];
        medicines.value[index] = {
          id: currentMedicine.id,
          name: response.data.medicine_name,
          genericName: currentMedicine.genericName,
          category: currentMedicine.category,
          dosage: currentMedicine.dosage,
          strength: currentMedicine.strength,
          quantity: response.data.current_stock,
          unit: currentMedicine.unit,
          expiryDate: response.data.expiry_date,
          minStockLevel: response.data.minimum_stock_level,
          description: response.data.usage_pattern,
          stockLevel: response.data.stock_level,
          // unitPrice: response.data.unit_price,
          //batchNumber: response.data.batch_number
        };
      }
    } else {
      // Add new medicine
      const response = await api.post('/operations/medicine-inventory/add/', {
        name: medicineForm.value.name,
        quantity: medicineForm.value.quantity,
        //unit_price: medicineForm.value.unitPrice || 0,
        minimum_stock_level: medicineForm.value.minStockLevel,
        expiry_date: medicineForm.value.expiryDate,
        //batch_number: medicineForm.value.batchNumber || `BATCH-${Date.now()}`,
        usage_pattern: medicineForm.value.description || '',
      });

      // Add to local state
      const newMedicine: Medicine = {
        id: response.data.id,
        name: response.data.medicine_name,
        genericName: medicineForm.value.genericName,
        category: medicineForm.value.category,
        dosage: medicineForm.value.dosage,
        strength: medicineForm.value.strength,
        quantity: response.data.current_stock,
        unit: medicineForm.value.unit,
        expiryDate: response.data.expiry_date,
        minStockLevel: response.data.minimum_stock_level,
        description: response.data.usage_pattern,
        stockLevel: response.data.stock_level,
        //unitPrice: response.data.unit_price,
        //batchNumber: response.data.batch_number
      };
      medicines.value.push(newMedicine);
    }

    // Check stock levels after saving
    checkStockLevels();

    $q.notify({
      type: 'positive',
      message: `Medicine ${editingMedicine.value ? 'updated' : 'added'} successfully!`,
      position: 'top',
    });

    cancelEdit();
  } catch (error) {
    console.error('Error saving medicine:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to save medicine. Please try again.',
      position: 'top',
    });
  } finally {
    saving.value = false;
  }
};

const cancelDispense = () => {
  selectedMedicine.value = null;
  showDispenseDialog.value = false;
};

const confirmDispense = () => {
  dispensing.value = true;

  try {
    // Update medicine quantity
    const medicine = medicines.value.find((m) => m.id === selectedMedicine.value?.id);
    if (medicine && selectedMedicine.value) {
      medicine.quantity -= dispenseForm.value.quantity;

      // Update stock level
      if (medicine.quantity <= 0) {
        medicine.stockLevel = 'out_of_stock';
      } else if (medicine.quantity <= medicine.minStockLevel) {
        medicine.stockLevel = 'low_stock';
      } else {
        medicine.stockLevel = 'in_stock';
      }
    }

    // Check stock levels after dispensing
    checkStockLevels();

    $q.notify({
      type: 'positive',
      message: 'Medicine dispensed successfully!',
      position: 'top',
    });

    cancelDispense();
  } catch (error) {
    console.error('Error dispensing medicine:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to dispense medicine. Please try again.',
      position: 'top',
    });
  } finally {
    dispensing.value = false;
  }
};

const cancelRestock = () => {
  selectedMedicine.value = null;
  showRestockDialog.value = false;
};

const confirmRestock = () => {
  restocking.value = true;

  try {
    // Update medicine quantity
    const medicine = medicines.value.find((m) => m.id === selectedMedicine.value?.id);
    if (medicine && selectedMedicine.value) {
      medicine.quantity += restockForm.value.quantity;

      // Update expiry date if provided
      if (restockForm.value.expiryDate) {
        medicine.expiryDate = restockForm.value.expiryDate;
      }

      // Update stock level
      if (medicine.quantity > medicine.minStockLevel) {
        medicine.stockLevel = 'in_stock';
      } else if (medicine.quantity > 0) {
        medicine.stockLevel = 'low_stock';
      }
    }

    // Check stock levels after restocking
    checkStockLevels();

    $q.notify({
      type: 'positive',
      message: 'Medicine restocked successfully!',
      position: 'top',
    });

    cancelRestock();
  } catch (error) {
    console.error('Error restocking medicine:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to restock medicine. Please try again.',
      position: 'top',
    });
  } finally {
    restocking.value = false;
  }
};

const exportInventory = () => {
  // Mock export functionality
  $q.notify({
    type: 'info',
    message: 'Inventory export feature coming soon!',
    position: 'top',
  });
};

// Notification helper functions
const getNotificationIcon = (type: string) => {
  switch (type) {
    case 'low_stock':
      return 'warning';
    case 'out_of_stock':
      return 'error';
    case 'expiring_soon':
      return 'schedule';
    default:
      return 'info';
  }
};

const getNotificationColor = (type: string) => {
  switch (type) {
    case 'low_stock':
      return 'warning';
    case 'out_of_stock':
      return 'negative';
    case 'expiring_soon':
      return 'orange';
    default:
      return 'primary';
  }
};

const formatNotificationTime = (timestamp: Date) => {
  const now = new Date();
  const diff = now.getTime() - timestamp.getTime();
  const minutes = Math.floor(diff / (1000 * 60));
  const hours = Math.floor(diff / (1000 * 60 * 60));
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));

  if (minutes < 60) {
    return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
  } else if (hours < 24) {
    return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
  } else {
    return `${days} day${days !== 1 ? 's' : ''} ago`;
  }
};

const viewNotification = (notification: Notification) => {
  selectedNotification.value = notification;
  showNotificationDialog.value = true;
};

const markNotificationRead = (notification: Notification) => {
  notification.isRead = true;
  $q.notify({
    type: 'positive',
    message: 'Notification marked as read',
    position: 'top',
  });
};

const markAllNotificationsRead = () => {
  notifications.value.forEach((notification) => {
    notification.isRead = true;
  });
  $q.notify({
    type: 'positive',
    message: 'All notifications marked as read',
    position: 'top',
  });
};

const viewMedicineFromNotification = () => {
  if (selectedNotification.value) {
    const medicine = medicines.value.find(
      (m) => m.name === selectedNotification.value!.medicineName,
    );
    if (medicine) {
      editMedicine(medicine);
      showNotificationDialog.value = false;
    }
  }
};

const restockFromNotification = () => {
  if (selectedNotification.value) {
    const medicine = medicines.value.find(
      (m) => m.name === selectedNotification.value!.medicineName,
    );
    if (medicine) {
      restockMedicine(medicine);
      showNotificationDialog.value = false;
    }
  }
};

const fetchUserProfile = async () => {
  try {
    const response = await api.get('/users/profile/');
    const userData = response.data.user; // The API returns nested user data

    // Check for verification status change
    const previousStatus = userProfile.value.verification_status;
    const newStatus = userData.verification_status;

    userProfile.value = {
      first_name: userData.first_name,
      last_name: userData.last_name,
      full_name: userData.full_name,
      role: userData.role,
      is_verified: userData.is_verified,
      verification_status: userData.verification_status,
      profile_picture: userData.profile_picture || localStorage.getItem('profile_picture'),
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
  }
};

// Sidebar and navigation functions
const toggleRightDrawer = () => {
  rightDrawerOpen.value = !rightDrawerOpen.value;
};



// Search functionality methods
const onSearchInput = async (value: string | number | null) => {
  const stringValue = String(value || '');
  searchText.value = stringValue;
  if (stringValue.trim() && stringValue.length > 2) {
    try {
      // Search for patients, doctors, and medicines using real API endpoints
      const [patientsResponse, doctorsResponse, medicinesResponse] = await Promise.all([
        api.get(`/users/nurse/patients/?search=${encodeURIComponent(stringValue)}`),
        api.get(`/operations/available-doctors/?search=${encodeURIComponent(stringValue)}`),
        api.get(`/operations/medicine-inventory/?search=${encodeURIComponent(stringValue)}`),
      ]);

      const results = [];

      // Add medicine results first (most relevant for this page)
      if (medicinesResponse.data) {
        results.push(
          ...medicinesResponse.data.map((item: MedicineSearchResult) => ({
            id: `medicine-${item.id}`,
            type: 'medicine',
            title: item.medicine_name || item.name || 'Unknown Medicine',
            subtitle: `Stock: ${item.stock_quantity || item.current_stock || 0} - ${item.manufacturer || 'Unknown Manufacturer'}`,
            data: item,
          })),
        );
      }

      // Add patient results
      if (patientsResponse.data.patients) {
        results.push(
          ...patientsResponse.data.patients.map((item: PatientSearchResult) => ({
            id: `patient-${item.id}`,
            type: 'patient',
            title: item.full_name || item.patient_name || item.name || 'Unknown Patient',
            subtitle: `Patient - Room: ${item.room_number || 'N/A'}`,
            data: item,
          })),
        );
      }

      // Add doctor results
      if (doctorsResponse.data) {
        results.push(
          ...doctorsResponse.data.map((item: DoctorSearchResult) => ({
            id: `doctor-${item.id}`,
            type: 'doctor',
            title: item.full_name || item.name || 'Unknown Doctor',
            subtitle: `Doctor - ${item.specialization || 'General'}`,
            data: item,
          })),
        );
      }

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

const selectSearchResult = (result: {
  id: string;
  type: string;
  title: string;
  subtitle: string;
  data: Record<string, string | number>;
}) => {
  // Handle search result selection
  console.log('Selected search result:', result);
  clearSearch();
};

// Location functionality
const fetchLocation = async () => {
  locationLoading.value = true;
  locationError.value = false;

  try {
    // Simulate API call for location data
    await new Promise((resolve) => setTimeout(resolve, 1000));
    locationData.value = {
      city: 'Manila',
      region: 'Metro Manila',
      country: 'Philippines',
    };
  } catch (error) {
    console.error('Error fetching location:', error);
    locationError.value = true;
  } finally {
    locationLoading.value = false;
  }
};

// Time and weather functions
const updateTime = () => {
  const now = new Date();

  // Convert to 12-hour format with AM/PM beside the time
  const hour = now.getHours();
  const ampm = hour >= 12 ? 'PM' : 'AM';
  const hour12 = hour % 12 || 12;
  const minute = now.getMinutes().toString().padStart(2, '0');
  const second = now.getSeconds().toString().padStart(2, '0');

  currentTime.value = `${hour12}:${minute}:${second} ${ampm}`;
};

const fetchWeather = async () => {
  weatherLoading.value = true;
  weatherError.value = false;

  try {
    // Mock weather data for now
    await new Promise((resolve) => setTimeout(resolve, 1000));
    weatherData.value = {
      temperature: 22,
      condition: 'clear',
      location: 'Manila, PH',
    };
  } catch (error) {
    console.error('Weather fetch failed:', error);
    weatherError.value = true;
  } finally {
    weatherLoading.value = false;
  }
};

// Load medicine inventory from backend
const loadMedicineInventory = async () => {
  try {
    loading.value = true;
    const response = await api.get('/operations/medicine-inventory/');

    // Transform backend data to frontend format
    medicines.value = response.data.map(
      (medicine: {
        id: number;
        medicine_name: string;
        current_stock: number;
        expiry_date: string;
        minimum_stock_level: number;
        usage_pattern: string;
        stock_level: string;
        unit_price: number;
        batch_number: string;
      }) => ({
        id: medicine.id,
        name: medicine.medicine_name,
        genericName: medicine.medicine_name, // Use same name for now
        category: 'General', // Default category
        dosage: 'As prescribed',
        strength: 'Standard',
        quantity: medicine.current_stock,
        unit: 'units',
        expiryDate: medicine.expiry_date,
        minStockLevel: medicine.minimum_stock_level,
        description: medicine.usage_pattern || '',
        stockLevel: medicine.stock_level,
        unitPrice: medicine.unit_price,
        batchNumber: medicine.batch_number,
      }),
    );

    // Check stock levels on initial load
    checkStockLevels();
  } catch (error) {
    console.error('Failed to load medicine inventory:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to load medicine inventory',
      position: 'top',
      timeout: 3000,
    });
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  // Load user profile first
  void fetchUserProfile();

  // Initialize real-time features
  updateTime(); // Set initial time
  timeInterval = setInterval(updateTime, 1000); // Update every second

  // Fetch weather data
  void fetchWeather();

  // Fetch location data
  void fetchLocation();

  // Load inventory data from backend
  void loadMedicineInventory();

  // Refresh user profile every 30 seconds to check for verification status updates
  setInterval(() => {
    void fetchUserProfile();
  }, 30000);

  // More frequent verification status check (every 10 seconds)
  setInterval(() => {
    void fetchUserProfile();
  }, 10000);
});

// Removed profile picture storage sync: initials-only avatar

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval);
  }
});
</script>

<style scoped>
/* Page Container with Background */
.page-container-with-fixed-header {
  background: #f5f5f5;
  min-height: 100vh;
  padding-top: 64px; /* Account for fixed header */
}

/* Greeting Section */
.greeting-section {
  padding: 24px;
  background: transparent;
}

.greeting-card {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
}

.greeting-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
  pointer-events: none;
}

.greeting-content {
  position: relative;
  z-index: 1;
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

.page-header {
  background: white;
  color: #333;
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.back-btn {
  color: white;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

.page-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.search-filters-card,
.inventory-table-card {
  margin-bottom: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stats-section {
  margin-bottom: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  margin-bottom: 10px;
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
}

/* Card-specific colors */
.total-medicines .stat-icon {
  color: #2196f3;
}

.low-stock .stat-icon {
  color: #ff9800;
}

.out-of-stock .stat-icon {
  color: #f44336;
}

.expiring-soon .stat-icon {
  color: #e91e63;
}

.inventory-table {
  border-radius: 8px;
}

/* Notifications Styles */
.notifications-card {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.notifications-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.notification-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  border-radius: 8px;
  background: #f8f9fa;
  border-left: 4px solid #2196f3;
  transition: all 0.2s ease;
  cursor: pointer;
}

.notification-item:hover {
  background: #e3f2fd;
  transform: translateX(5px);
}

.notification-item.unread {
  background: #fff3e0;
  border-left-color: #ff9800;
}

.notification-item.unread:hover {
  background: #ffe0b2;
}

.notification-item.read {
  opacity: 0.7;
}

.notification-icon {
  flex-shrink: 0;
}

.notification-content {
  flex: 1;
}

.notification-message {
  font-weight: 500;
  color: #333;
  margin-bottom: 5px;
}

.notification-time {
  font-size: 12px;
  color: #666;
}

.notification-actions {
  display: flex;
  gap: 5px;
}

.notification-detail {
  padding: 10px 0;
}

.notification-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.notification-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.notification-message {
  font-size: 14px;
  color: #666;
  line-height: 1.5;
  margin-bottom: 10px;
}

.notification-time {
  font-size: 12px;
  color: #999;
  margin-bottom: 15px;
}

.notification-actions {
  display: flex;
  gap: 10px;
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

/* Responsive adjustments */
@media (max-width: 768px) {
  .page-content {
    padding: 8px;
  }

  .q-card {
    margin: 8px 0;
    border-radius: 12px;
  }

  .q-card__section {
    padding: 16px;
  }

  .header-content {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
    padding: 16px;
  }

  .header-right {
    align-self: flex-end;
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

  .notification-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    padding: 12px;
  }

  .notification-actions {
    align-self: flex-end;
  }

  .medicine-card {
    margin-bottom: 16px;
  }

  .medicine-card h6 {
    font-size: 16px;
    margin-bottom: 8px;
  }

  .medicine-info .text-caption {
    font-size: 12px;
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

  .q-btn {
    padding: 10px 16px;
    font-size: 14px;
    border-radius: 6px;
  }

  .q-table {
    font-size: 12px;
  }

  .q-table th,
  .q-table td {
    padding: 8px;
  }
}

/* Header Styles */
.prototype-header {
  background: #286660;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-toolbar {
  padding: 0 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

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

/* Sidebar Styles */
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


.user-info {
  text-align: center;
}

.user-name {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.user-role {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #666;
}

.navigation-menu {
  flex: 1;
  padding: 8px 0;
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

/* Medicine Modal Styles */
.medicine-modal {
  min-width: 750px;
  max-width: 950px;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.modal-header {
  background: linear-gradient(135deg, #286660 0%, #1e7668 100%);
  color: white;
  padding: 20px 24px;
  border-radius: 16px 16px 0 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 600;
}

.title-icon {
  color: white;
}

.close-btn {
  color: white !important;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.modal-actions {
  padding: 20px 24px;
  background: #f8f9fa;
  border-radius: 0 0 16px 16px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.cancel-btn {
  padding: 8px 24px;
  border-radius: 8px;
}

.save-btn {
  padding: 8px 24px;
  border-radius: 8px;
  font-weight: 600;
}

/* Form Field Styles */
.modal-content {
  padding: 24px;
}

.form-fields {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row {
  width: 100%;
}

.form-input {
  width: 100%;
  min-width: 400px;
}

.form-input .q-field__control {
  min-height: 48px;
}

.form-input .q-field__native {
  font-size: 14px;
  padding: 12px 16px;
}

/* Enhanced Header Styles */
.search-results-dropdown {
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

.search-result-item {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.search-result-item:hover {
  background-color: #f5f5f5;
}

.search-result-item:last-child {
  border-bottom: none;
}

.search-result-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-result-icon {
  color: #286660;
}

.search-result-text {
  flex: 1;
}

.search-result-title {
  font-weight: 500;
  color: #333;
  margin-bottom: 2px;
}

.search-result-subtitle {
  font-size: 12px;
  color: #666;
}

/* Pill-style displays for time, weather, and location */
.time-display {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.weather-display {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.location-display {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
  font-size: 14px;
  font-weight: 500;
  padding: 6px 12px;
  border-radius: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.location-loading,
.location-error {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  gap: 6px;
  color: white;
  font-size: 14px;
  font-weight: 500;
  padding: 6px 12px;
  border-radius: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.location-error .q-icon {
  color: #ff6b6b;
}

/* Mobile responsive adjustments */
@media (max-width: 768px) {
  .header-right {
    gap: 8px;
  }

  .time-display,
  .weather-display,
  .location-display {
    font-size: 12px;
    padding: 4px 8px;
  }

  .search-container {
    min-width: 200px;
  }
}
</style>
