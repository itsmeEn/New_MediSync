export type MedicineRecord = {
  id: number;
  name: string;
  genericName: string;
  category:
    | 'analgesics'
    | 'antibiotics'
    | 'antihypertensives'
    | 'antidiabetics'
    | 'cardiovascular'
    | 'respiratory'
    | 'gastrointestinal'
    | 'psychiatric'
    | 'dermatology'
    | 'ophthalmic'
    | 'ent'
    | 'emergency'
    | 'supplements'
    | 'vaccines'
    | 'other';
  dosage: string;
  strength: string | number;
  quantity: number;
  unit: string;
  expiryDate: string;
  minStockLevel: number;
  description: string;
  stockLevel: 'in_stock' | 'low_stock' | 'out_of_stock';
  unitPrice?: number;
  batchNumber?: string;
};

function toIsoDaysFromNow(days: number): string {
  const d = new Date();
  d.setDate(d.getDate() + days);
  return d.toISOString();
}

function computeStockLevel(qty: number, min: number): 'in_stock' | 'low_stock' | 'out_of_stock' {
  if (qty <= 0) return 'out_of_stock';
  if (qty < min) return 'low_stock';
  return 'in_stock';
}

export function generateMockMedicines(): MedicineRecord[] {
  const base: Array<{
    name: string;
    genericName: string;
    category: MedicineRecord['category'];
    dosage: string;
    strength: string;
    unit: string;
    quantity: number;
    minStockLevel: number;
    expiryDays: number; // negative = expired, 0-30 = expiring soon, >30 = healthy
    unitPrice: number;
    batchSuffix: string;
    description: string;
  }> = [
    {
      name: 'Amoxicillin', genericName: 'Amoxicillin', category: 'antibiotics', dosage: 'Capsule', strength: '500 mg', unit: 'capsules', quantity: 180, minStockLevel: 60, expiryDays: 180, unitPrice: 12.5, batchSuffix: 'AMX', description: 'Broad-spectrum antibiotic',
    },
    {
      name: 'Azithromycin', genericName: 'Azithromycin', category: 'antibiotics', dosage: 'Tablet', strength: '500 mg', unit: 'tablets', quantity: 40, minStockLevel: 70, expiryDays: 25, unitPrice: 14.0, batchSuffix: 'AZI', description: 'Macrolide antibiotic for respiratory infections',
    },
    {
      name: 'Ceftriaxone', genericName: 'Ceftriaxone', category: 'antibiotics', dosage: 'Injection', strength: '1 g', unit: 'vials', quantity: 0, minStockLevel: 30, expiryDays: 120, unitPrice: 45.0, batchSuffix: 'CEF', description: 'Third-generation cephalosporin',
    },
    {
      name: 'Paracetamol', genericName: 'Acetaminophen', category: 'analgesics', dosage: 'Tablet', strength: '500 mg', unit: 'tablets', quantity: 35, minStockLevel: 60, expiryDays: 10, unitPrice: 5.0, batchSuffix: 'PARA', description: 'Pain reliever and fever reducer',
    },
    {
      name: 'Ibuprofen', genericName: 'Ibuprofen', category: 'analgesics', dosage: 'Tablet', strength: '400 mg', unit: 'tablets', quantity: 12, minStockLevel: 40, expiryDays: -5, unitPrice: 6.75, batchSuffix: 'IBU', description: 'NSAID for pain and inflammation',
    },
    {
      name: 'Morphine Sulfate', genericName: 'Morphine', category: 'emergency', dosage: 'Injection', strength: '10 mg/mL', unit: 'vials', quantity: 8, minStockLevel: 20, expiryDays: 90, unitPrice: 30.0, batchSuffix: 'MOR', description: 'Opioid analgesic for severe pain',
    },
    {
      name: 'Metformin', genericName: 'Metformin HCl', category: 'antidiabetics', dosage: 'Tablet', strength: '850 mg', unit: 'tablets', quantity: 0, minStockLevel: 100, expiryDays: 365, unitPrice: 7.25, batchSuffix: 'MET', description: 'Controls blood sugar for Type 2 diabetes',
    },
    {
      name: 'Insulin Glargine', genericName: 'Insulin Glargine', category: 'antidiabetics', dosage: 'Injection', strength: '100 IU/mL', unit: 'pens', quantity: 22, minStockLevel: 30, expiryDays: 7, unitPrice: 55.0, batchSuffix: 'GLAR', description: 'Long-acting insulin for diabetes',
    },
    {
      name: 'Amlodipine', genericName: 'Amlodipine Besylate', category: 'antihypertensives', dosage: 'Tablet', strength: '10 mg', unit: 'tablets', quantity: 220, minStockLevel: 80, expiryDays: 270, unitPrice: 10.0, batchSuffix: 'AML', description: 'Calcium channel blocker for hypertension',
    },
    {
      name: 'Losartan', genericName: 'Losartan Potassium', category: 'antihypertensives', dosage: 'Tablet', strength: '50 mg', unit: 'tablets', quantity: 65, minStockLevel: 80, expiryDays: 15, unitPrice: 9.0, batchSuffix: 'LOS', description: 'ARB for hypertension management',
    },
    {
      name: 'Warfarin', genericName: 'Warfarin', category: 'cardiovascular', dosage: 'Tablet', strength: '5 mg', unit: 'tablets', quantity: 50, minStockLevel: 40, expiryDays: -10, unitPrice: 8.0, batchSuffix: 'WAR', description: 'Anticoagulant therapy',
    },
    {
      name: 'Atorvastatin', genericName: 'Atorvastatin', category: 'cardiovascular', dosage: 'Tablet', strength: '20 mg', unit: 'tablets', quantity: 190, minStockLevel: 70, expiryDays: 420, unitPrice: 11.0, batchSuffix: 'ATOR', description: 'Statin for cholesterol reduction',
    },
    {
      name: 'Salbutamol', genericName: 'Albuterol', category: 'respiratory', dosage: 'Inhaler', strength: '100 mcg', unit: 'inhalers', quantity: 28, minStockLevel: 30, expiryDays: 20, unitPrice: 18.0, batchSuffix: 'SALB', description: 'Bronchodilator for asthma relief',
    },
    {
      name: 'Budesonide/Formoterol', genericName: 'Budesonide/Formoterol', category: 'respiratory', dosage: 'Inhaler', strength: '160/4.5 mcg', unit: 'inhalers', quantity: 12, minStockLevel: 25, expiryDays: 45, unitPrice: 32.0, batchSuffix: 'SYMB', description: 'Combination ICS/LABA for asthma control',
    },
    {
      name: 'Omeprazole', genericName: 'Omeprazole', category: 'gastrointestinal', dosage: 'Capsule', strength: '20 mg', unit: 'capsules', quantity: 75, minStockLevel: 60, expiryDays: 28, unitPrice: 9.5, batchSuffix: 'OME', description: 'Proton pump inhibitor for acid reflux',
    },
    {
      name: 'Pantoprazole', genericName: 'Pantoprazole', category: 'gastrointestinal', dosage: 'Tablet', strength: '40 mg', unit: 'tablets', quantity: 120, minStockLevel: 50, expiryDays: 300, unitPrice: 10.5, batchSuffix: 'PANT', description: 'PPI for GERD management',
    },
    {
      name: 'Sertraline', genericName: 'Sertraline', category: 'psychiatric', dosage: 'Tablet', strength: '50 mg', unit: 'tablets', quantity: 90, minStockLevel: 40, expiryDays: 200, unitPrice: 13.0, batchSuffix: 'SERT', description: 'SSRI for depression and anxiety',
    },
    {
      name: 'Olanzapine', genericName: 'Olanzapine', category: 'psychiatric', dosage: 'Tablet', strength: '10 mg', unit: 'tablets', quantity: 15, minStockLevel: 30, expiryDays: 12, unitPrice: 22.0, batchSuffix: 'OLAN', description: 'Atypical antipsychotic',
    },
    {
      name: 'Hydrocortisone Cream', genericName: 'Hydrocortisone', category: 'dermatology', dosage: 'Cream', strength: '1%', unit: 'tubes', quantity: 55, minStockLevel: 20, expiryDays: 60, unitPrice: 7.0, batchSuffix: 'HYD', description: 'Topical steroid for inflammation',
    },
    {
      name: 'Mupirocin Ointment', genericName: 'Mupirocin', category: 'dermatology', dosage: 'Ointment', strength: '2%', unit: 'tubes', quantity: 5, minStockLevel: 15, expiryDays: 18, unitPrice: 12.0, batchSuffix: 'MUP', description: 'Topical antibiotic for skin infections',
    },
    {
      name: 'Timolol Eye Drops', genericName: 'Timolol', category: 'ophthalmic', dosage: 'Drops', strength: '0.5%', unit: 'bottles', quantity: 0, minStockLevel: 10, expiryDays: 35, unitPrice: 16.0, batchSuffix: 'TIM', description: 'Beta-blocker for glaucoma',
    },
    {
      name: 'Ofloxacin Ear Drops', genericName: 'Ofloxacin', category: 'ent', dosage: 'Drops', strength: '0.3%', unit: 'bottles', quantity: 9, minStockLevel: 12, expiryDays: -2, unitPrice: 8.5, batchSuffix: 'OFL', description: 'Fluoroquinolone for ear infections',
    },
    {
      name: 'Adrenaline', genericName: 'Epinephrine', category: 'emergency', dosage: 'Injection', strength: '1 mg/mL', unit: 'amps', quantity: 25, minStockLevel: 20, expiryDays: 90, unitPrice: 20.0, batchSuffix: 'EPI', description: 'First-line for anaphylaxis',
    },
    {
      name: 'Activated Charcoal', genericName: 'Activated Charcoal', category: 'emergency', dosage: 'Suspension', strength: '50 g', unit: 'bottles', quantity: 14, minStockLevel: 20, expiryDays: 400, unitPrice: 5.5, batchSuffix: 'CHAR', description: 'Poisoning management',
    },
    {
      name: 'Vitamin D3', genericName: 'Cholecalciferol', category: 'supplements', dosage: 'Capsule', strength: '2000 IU', unit: 'capsules', quantity: 300, minStockLevel: 80, expiryDays: 500, unitPrice: 4.0, batchSuffix: 'VD3', description: 'Vitamin supplement',
    },
    {
      name: 'Iron + Folic Acid', genericName: 'Ferrous Sulfate + Folic Acid', category: 'supplements', dosage: 'Tablet', strength: '325 mg + 0.5 mg', unit: 'tablets', quantity: 28, minStockLevel: 60, expiryDays: 45, unitPrice: 3.5, batchSuffix: 'IFA', description: 'Supplement for anemia prevention',
    },
    {
      name: 'Influenza Vaccine', genericName: 'Inactivated Influenza Vaccine', category: 'vaccines', dosage: 'Injection', strength: '0.5 mL', unit: 'vials', quantity: 60, minStockLevel: 50, expiryDays: 25, unitPrice: 25.0, batchSuffix: 'FLU', description: 'Seasonal flu vaccine',
    },
    {
      name: 'Hepatitis B Vaccine', genericName: 'Recombinant Hepatitis B Vaccine', category: 'vaccines', dosage: 'Injection', strength: '10 mcg/mL', unit: 'vials', quantity: 0, minStockLevel: 40, expiryDays: 15, unitPrice: 28.0, batchSuffix: 'HEPB', description: 'Hepatitis B immunization',
    },
    {
      name: 'Dexamethasone', genericName: 'Dexamethasone', category: 'other', dosage: 'Tablet', strength: '4 mg', unit: 'tablets', quantity: 48, minStockLevel: 40, expiryDays: 22, unitPrice: 6.0, batchSuffix: 'DEX', description: 'Corticosteroid for inflammation',
    },
    {
      name: 'Clopidogrel', genericName: 'Clopidogrel', category: 'cardiovascular', dosage: 'Tablet', strength: '75 mg', unit: 'tablets', quantity: 85, minStockLevel: 50, expiryDays: 365, unitPrice: 12.0, batchSuffix: 'CLOP', description: 'Antiplatelet agent',
    },
    {
      name: 'Nitroglycerin', genericName: 'Glyceryl Trinitrate', category: 'cardiovascular', dosage: 'Sublingual', strength: '0.4 mg', unit: 'tablets', quantity: 18, minStockLevel: 25, expiryDays: 5, unitPrice: 9.0, batchSuffix: 'NITRO', description: 'Antianginal therapy',
    },
    {
      name: 'Levetiracetam', genericName: 'Levetiracetam', category: 'other', dosage: 'Tablet', strength: '500 mg', unit: 'tablets', quantity: 70, minStockLevel: 30, expiryDays: 250, unitPrice: 15.0, batchSuffix: 'LEV', description: 'Antiepileptic medication',
    },
  ];

  return base.map((b, idx) => {
    const stockLevel = computeStockLevel(b.quantity, b.minStockLevel);
    const expiryDate = toIsoDaysFromNow(b.expiryDays);
    return {
      id: idx + 1,
      name: b.name,
      genericName: b.genericName,
      category: b.category,
      dosage: b.dosage,
      strength: b.strength,
      quantity: b.quantity,
      unit: b.unit,
      expiryDate,
      minStockLevel: b.minStockLevel,
      description: b.description,
      stockLevel,
      unitPrice: b.unitPrice,
      batchNumber: `${b.batchSuffix}-${new Date().getFullYear()}-${String(idx + 1).padStart(2, '0')}`,
    };
  });
}