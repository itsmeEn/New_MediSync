// Utility to transform archived assessment data into human-readable sections
// Handles both flat records and nested structures under `assessment` or `nursing_intake_assessment`

export type Section = Record<string, string | number | boolean | string[]>;

export interface HumanReadableAssessment {
  overview: Section;
  participants: Section;
  vitals: Section;
  metrics: Section; // scores and status
  notes: Section; // comments/messages
  lists: Record<string, string[]>; // arrays like allergies, education records, etc.
  other: Record<string, string>; // any remaining primitive fields not covered
}

type AnyObj = Record<string, unknown>;

const isPrimitive = (v: unknown): v is string | number | boolean =>
  typeof v === 'string' || typeof v === 'number' || typeof v === 'boolean';

const safeStr = (v: unknown): string => {
  if (v === null || v === undefined) return '';
  if (Array.isArray(v)) return v.map((x) => safeStr(x)).join(', ');
  if (typeof v === 'object') {
    try { return JSON.stringify(v, null, 2); } catch { return '[Unserializable Object]'; }
  }
  if (typeof v === 'string' || typeof v === 'number' || typeof v === 'boolean') return String(v);
  if (typeof v === 'bigint') return v.toString();
  if (typeof v === 'function') return '[Function]';
  return '[Unsupported Type]';
};

const pick = (obj: AnyObj | undefined, key: string): unknown => obj ? obj[key] : undefined;

export function normalizeAssessmentData(input: unknown): HumanReadableAssessment {
  const raw: AnyObj = (typeof input === 'object' && input) ? (input as AnyObj) : {};
  // Support nested structure
  const assessment: AnyObj = (typeof raw.assessment === 'object' && raw.assessment)
    ? (raw.assessment as AnyObj)
    : raw;

  // Nursing intake sub-structure (if present)
  const intake: AnyObj | undefined = (typeof assessment.nursing_intake_assessment === 'object')
    ? (assessment.nursing_intake_assessment as AnyObj)
    : undefined;

  const vitals: AnyObj | undefined = (intake && typeof intake.vitals === 'object')
    ? (intake.vitals as AnyObj)
    : undefined;

  // Overview
  const overview: Section = {
    'Assessment Name': safeStr(pick(assessment, 'assessment_name') || pick(assessment, 'type') || ''),
    'Archived': Boolean(pick(assessment, 'archived')),
    'Archived At': safeStr(pick(assessment, 'archived_at')),
    'Archived By': safeStr(pick(assessment, 'archived_by')),
    'Assessed At': safeStr(pick(assessment, 'assessed_at') || pick(raw, 'last_assessed_at')),
  };

  // Participants
  const patient: AnyObj | undefined = (typeof assessment.patient === 'object') ? (assessment.patient as AnyObj) : undefined;
  const participants: Section = {
    'Actor': safeStr(pick(assessment, 'actor')),
    'Nurse': safeStr(pick(assessment, 'nurse_name')),
    'Patient Name': safeStr(pick(patient, 'full_name') || pick(raw, 'patient_name')),
    'Patient ID': safeStr(pick(patient, 'id') || pick(raw, 'patient_id')),
    'Gender': safeStr(pick(patient, 'gender')),
    'Email': safeStr(pick(patient, 'email')),
    'Date of Birth': safeStr(pick(patient, 'date_of_birth')),
    'MRN': safeStr(pick(patient, 'mrn')),
  };

  // Vitals
  const vitalsSection: Section = {
    'Blood Pressure': safeStr(pick(assessment, 'bp') || pick(vitals, 'bp')),
    'Heart Rate': safeStr(pick(assessment, 'hr') || pick(vitals, 'hr')),
    'Respiratory Rate': safeStr(pick(assessment, 'rr') || pick(vitals, 'rr')),
    'O2 Saturation': safeStr(pick(assessment, 'o2') || pick(vitals, 'o2_sat')),
    'Temperature': safeStr(pick(assessment, 'temp') || pick(vitals, 'temp_c')),
    'Height': safeStr(pick(assessment, 'height') || pick(intake, 'height_cm')),
    'Weight': safeStr(pick(assessment, 'weight') || pick(intake, 'weight_kg')),
  };

  // Metrics (scores and statuses)
  const metrics: Section = {
    'Pain Score': safeStr(pick(assessment, 'painScore') || pick(intake, 'pain_score')),
    'Fall Risk': safeStr(pick(assessment, 'fallRisk') || pick(intake, 'fall_risk_score')),
    'Mental Status': safeStr(pick(assessment, 'mentalStatus') || pick(intake, 'mental_status')),
  };

  // Notes/comments
  const notes: Section = {
    'Chief Complaint': safeStr(pick(assessment, 'chiefComplaint') || pick(intake, 'chief_complaint')),
    'Message': safeStr(pick(assessment, 'message')),
  };

  // Lists/arrays
  const allergies: unknown = pick(assessment, 'allergies') || pick(intake, 'allergies');
  const lists: Record<string, string[]> = {
    Allergies: Array.isArray(allergies) ? allergies.map((a) => safeStr(a)) : [],
    'Education Records': Array.isArray(assessment.patient_education_record) ? assessment.patient_education_record.map((x) => safeStr(x)) : [],
    'Progress Notes': Array.isArray(assessment.progress_notes) ? assessment.progress_notes.map((x) => safeStr(x)) : [],
    'Orders': Array.isArray(assessment.provider_order_sheets) ? assessment.provider_order_sheets.map((x) => safeStr(x)) : [],
    'MAR': Array.isArray(assessment.medication_administration_records) ? assessment.medication_administration_records.map((x) => safeStr(x)) : [],
    'Op Reports': Array.isArray(assessment.operative_procedure_reports) ? assessment.operative_procedure_reports.map((x) => safeStr(x)) : [],
    'Graphic Sheets': Array.isArray(assessment.graphic_flow_sheets) ? assessment.graphic_flow_sheets.map((x) => safeStr(x)) : [],
  };

  // Compute other primitive fields not already captured
  const usedKeys = new Set<string>([
    'assessment','nursing_intake_assessment','vitals','actor','nurse_name','patient','allergies',
    'archived','archived_at','archived_by','assessed_at','bp','hr','rr','o2','temp','height','weight',
    'chiefComplaint','message','painScore','fallRisk','mentalStatus','patient_education_record','progress_notes',
    'provider_order_sheets','medication_administration_records','operative_procedure_reports','graphic_flow_sheets',
  ]);

  const other: Record<string, string> = {};
  Object.entries(assessment).forEach(([k, v]) => {
    if (!usedKeys.has(k) && isPrimitive(v)) {
      other[k] = safeStr(v);
    }
  });

  return { overview, participants, vitals: vitalsSection, metrics, notes, lists, other };
}

export function formatSectionRows(section: Section): Array<{ label: string; value: string }> {
  return Object.entries(section)
    .filter(([, v]) => (v !== '' && v !== undefined && v !== null))
    .map(([label, value]) => ({
      label,
      value: Array.isArray(value)
        ? value.map((x) => (typeof x === 'object' ? JSON.stringify(x, null, 2) : String(x))).join(', ')
        : (typeof value === 'object' ? JSON.stringify(value as object, null, 2) : String(value))
    }));
}