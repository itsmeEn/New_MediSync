export type DepartmentOption = { label: string; value: string };

// Shared list used across PatientAppointment and Doctor settings/registration
export const departmentOptions: DepartmentOption[] = [
  { label: 'General Medicine', value: 'general-medicine' },
  { label: 'Cardiology', value: 'cardiology' },
  { label: 'Dermatology', value: 'dermatology' },
  { label: 'Orthopedics', value: 'orthopedics' },
  { label: 'Pediatrics', value: 'pediatrics' },
  { label: 'Gynecology', value: 'gynecology' },
  { label: 'Neurology', value: 'neurology' },
  { label: 'Oncology', value: 'oncology' },
  { label: 'Optometrist', value: 'optometrist' },
  { label: 'Emergency Medicine', value: 'emergency-medicine' },
  // Fallback to avoid breaking when existing values don’t match known departments
  { label: 'Other', value: 'other' },
];