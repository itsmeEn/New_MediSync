import { describe, it, expect } from 'vitest'
import { normalizeAssessmentData } from 'src/utils/archiveFormat'

describe('normalizeAssessmentData', () => {
  it('handles nested assessment with nursing intake vitals', () => {
    const input = {
      assessment: {
        actor: 'nurse',
        nurse_name: 'Test Nurse',
        archived: true,
        archived_at: '2025-11-11T09:28:37.031083+00:00',
        archived_by: 4,
        patient: {
          id: 2,
          full_name: 'John Doe',
          gender: 'male',
          email: 'john@example.com',
          date_of_birth: '2000-01-01',
          mrn: 'MRN-001'
        },
        nursing_intake_assessment: {
          assessed_at: '2025-11-11T09:28:26.261Z',
          chief_complaint: 'Cough',
          pain_score: 2,
          fall_risk_score: 0,
          mental_status: 'alert',
          height_cm: 170,
          weight_kg: 60,
          vitals: {
            bp: '120/80',
            hr: 70,
            o2_sat: 98,
            rr: 16,
            temp_c: 36.6
          }
        }
      },
      last_assessed_at: '2025-11-11T09:28:37.254481+00:00',
      patient_name: 'John Doe',
      patient_id: 2
    }

    const sections = normalizeAssessmentData(input)
    expect(sections.overview['Archived']).toBe(true)
    expect(String(sections.overview['Assessed At'])).toContain('2025-11-11')
    expect(sections.participants['Actor']).toBe('nurse')
    expect(sections.participants['Patient Name']).toBe('John Doe')
    expect(sections.vitals['Blood Pressure']).toBe('120/80')
    expect(sections.vitals['Heart Rate']).toBe('70')
    expect(sections.metrics['Pain Score']).toBe('2')
    expect(sections.metrics['Mental Status']).toBe('alert')
    expect(sections.notes['Chief Complaint']).toBe('Cough')
  })

  it('handles flat assessment fields without nesting', () => {
    const input = {
      actor: 'nurse',
      nurse_name: 'Flat Nurse',
      archived: true,
      bp: '110/70',
      hr: 65,
      rr: 18,
      o2: 97,
      temp: 36.5,
      height: '160',
      weight: '55',
      painScore: 1,
      fallRisk: 'low',
      mentalStatus: 'alert',
      message: 'stable',
      patient: { id: 1, full_name: 'Jane Roe' }
    }
    const sections = normalizeAssessmentData(input)
    expect(sections.participants['Nurse']).toBe('Flat Nurse')
    expect(sections.vitals['Blood Pressure']).toBe('110/70')
    expect(sections.metrics['Fall Risk']).toBe('low')
    expect(sections.notes['Message']).toBe('stable')
  })
})