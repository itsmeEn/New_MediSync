import random
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import List, Dict, Tuple

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from backend.analytics.models import AnalyticsResult, PatientRecord
from backend.users.models import User, NurseProfile
from backend.operations.models import MedicineInventory


# --- Inventory catalog with categories ---
MEDICINE_CATALOG: Dict[str, List[Tuple[str, str, Decimal]]] = {
    "analgesics": [
        ("Paracetamol 500mg Tablet", "Analgesic and antipyretic; take as needed for pain/fever.", Decimal("0.50")),
        ("Ibuprofen 400mg Tablet", "NSAID; take with food; avoid long-term use.", Decimal("0.70")),
        ("Diclofenac 50mg Tablet", "NSAID; take with food.", Decimal("0.65")),
        ("Aspirin 81mg Tablet", "Antiplatelet; once daily.", Decimal("0.35")),
        ("Naproxen 250mg Tablet", "NSAID; take with food.", Decimal("0.85")),
    ],
    "antibiotics": [
        ("Amoxicillin 500mg Capsule", "Antibiotic; complete full course as prescribed.", Decimal("1.20")),
        ("Cefuroxime 500mg Tablet", "Antibiotic; complete full course as prescribed.", Decimal("1.80")),
        ("Azithromycin 500mg Tablet", "Antibiotic; once daily; complete course.", Decimal("2.20")),
        ("Doxycycline 100mg Capsule", "Antibiotic; twice daily; complete course.", Decimal("1.30")),
        ("Amoxicillin/Clavulanate 625mg", "Antibiotic; take with food; complete course.", Decimal("2.80")),
    ],
    "antihypertensives": [
        ("Amlodipine 5mg Tablet", "Antihypertensive; once daily dosing.", Decimal("0.80")),
        ("Losartan 50mg Tablet", "Antihypertensive; monitor BP regularly.", Decimal("0.90")),
        ("Hydrochlorothiazide 25mg Tablet", "Diuretic; monitor electrolytes.", Decimal("0.75")),
    ],
    "antidiabetics": [
        ("Metformin 500mg Tablet", "Antidiabetic; take with meals; monitor blood sugar.", Decimal("0.60")),
        ("Insulin Glargine 100U/mL", "Basal insulin; dose per protocol.", Decimal("12.00")),
    ],
    "respiratory": [
        ("Salbutamol Inhaler 100mcg", "Bronchodilator; 2 puffs as needed.", Decimal("5.50")),
        ("Budesonide/Formoterol Inhaler", "ICS/LABA; maintenance inhaler.", Decimal("9.50")),
        ("Guaifenesin 100mg/5mL Syrup", "Expectorant; dose per label.", Decimal("2.00")),
        ("Dextromethorphan 15mg/5mL Syrup", "Antitussive; nighttime.", Decimal("2.10")),
    ],
    "gi": [
        ("Omeprazole 20mg Capsule", "Proton pump inhibitor; take before meals.", Decimal("0.85")),
        ("Ranitidine 150mg Tablet", "H2 blocker; twice daily.", Decimal("0.55")),
        ("ORS Packet", "Oral rehydration salts; dissolve in clean water.", Decimal("0.30")),
        ("Loperamide 2mg Capsule", "Antidiarrheal; as needed.", Decimal("0.40")),
    ],
    "cardiovascular": [
        ("Atorvastatin 20mg Tablet", "Statin; take at night; monitor lipids.", Decimal("1.40")),
        ("Clopidogrel 75mg Tablet", "Antiplatelet; once daily.", Decimal("1.10")),
        ("Warfarin 5mg Tablet", "Anticoagulant; monitor INR.", Decimal("0.95")),
    ],
    "supplements": [
        ("Folic Acid 5mg Tablet", "Supplement; daily.", Decimal("0.25")),
        ("Vitamin B Complex Tablet", "Supplement; daily.", Decimal("0.40")),
        ("Vitamin D3 1000IU Capsule", "Supplement; daily.", Decimal("0.50")),
        ("Calcium Carbonate 500mg Tablet", "Supplement; with meals.", Decimal("0.55")),
        ("Iron (Ferrous Sulfate) 325mg", "Supplement; may cause GI upset.", Decimal("0.45")),
        ("Magnesium Oxide 400mg Tablet", "Supplement; daily.", Decimal("0.60")),
        ("Multivitamins Syrup", "Supplement; pediatric dosing per label.", Decimal("3.50")),
    ],
}


def _rand_expiry_scenario() -> Tuple[date, str]:
    scenario = random.choice(["expired", "expiring_soon", "normal_long"])
    today = date.today()
    if scenario == "expired":
        return today - timedelta(days=random.randint(7, 60)), scenario
    elif scenario == "expiring_soon":
        return today + timedelta(days=random.randint(7, 21)), scenario
    return today + timedelta(days=random.randint(180, 540)), scenario


def _rand_stock_scenario(min_level: int) -> Tuple[int, int]:
    scenario = random.choice(["out_of_stock", "low_stock", "in_stock", "overstock"])
    if scenario == "out_of_stock":
        current = 0
    elif scenario == "low_stock":
        current = random.randint(0, max(1, min_level))
    elif scenario == "in_stock":
        current = random.randint(min_level + 5, min_level + 40)
    else:
        current = random.randint(min_level + 50, min_level + 200)
    return current, current


def _gen_batch_number(idx: int) -> str:
    return f"BN-{timezone.now().strftime('%Y%m%d')}-{idx:04d}-{random.randint(1000,9999)}"


class Command(BaseCommand):
    help = "Populate dummy data for analytics dashboards and medicine inventory (server-side)."

    def add_arguments(self, parser):
        # Volume and date range
        parser.add_argument("--records", type=int, default=200, help="Number of patient records to generate.")
        parser.add_argument("--start-date", type=str, default=None, help="Start date (YYYY-MM-DD) for time-based analytics.")
        parser.add_argument("--end-date", type=str, default=None, help="End date (YYYY-MM-DD) for time-based analytics.")

        # Inventory options
        parser.add_argument(
            "--inventory-categories",
            type=str,
            default="analgesics,antibiotics,antihypertensives,antidiabetics,respiratory,gi,cardiovascular,supplements",
            help="Comma-separated inventory categories to seed",
        )
        parser.add_argument("--inventory-count", type=int, default=40, help="Approximate medicines per nurse.")
        parser.add_argument("--nurse-email", type=str, default=None, help="Target a specific nurse by email.")

        # Cleanup toggles
        parser.add_argument("--clear-analytics", action="store_true", help="Clear existing AnalyticsResult before seeding.")
        parser.add_argument("--clear-records", action="store_true", help="Clear existing PatientRecord before seeding.")
        parser.add_argument("--purge-inventory", action="store_true", help="Purge existing MedicineInventory before seeding.")

    @transaction.atomic
    def handle(self, *args, **options):
        records = options["records"]
        start_date_str = options.get("start_date")
        end_date_str = options.get("end_date")

        # Date range parsing
        end_dt = datetime.strptime(end_date_str, "%Y-%m-%d") if end_date_str else datetime.now()
        default_start = end_dt - timedelta(days=365)
        start_dt = datetime.strptime(start_date_str, "%Y-%m-%d") if start_date_str else default_start
        if start_dt > end_dt:
            raise CommandError("start-date must be before end-date")

        # Cleanup based on flags
        if options.get("clear_analytics"):
            AnalyticsResult.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared existing analytics results"))
        if options.get("clear_records"):
            PatientRecord.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared existing patient records"))

        # Build category pool
        raw_categories = [c.strip().lower() for c in options["inventory_categories"].split(",") if c.strip()]
        unknown = [c for c in raw_categories if c not in MEDICINE_CATALOG]
        if unknown:
            raise CommandError(f"Unknown inventory categories: {', '.join(unknown)}")
        categories = raw_categories or list(MEDICINE_CATALOG.keys())

        # Seed patient records
        created_records = self._seed_patient_records(records, start_dt, end_dt)

        # Create analytics results inferred from records
        self._create_analytics_results(start_dt, end_dt)

        # Seed medicine inventory
        self._seed_medicine_inventory(categories, options["inventory_count"], options.get("nurse_email"), options.get("purge_inventory"))

        self.stdout.write(self.style.SUCCESS(
            f"Demo data populated: patient_records={created_records}, analytics_results=created, inventory=seeded"
        ))

    # --- Patient Records ---
    def _seed_patient_records(self, count: int, start_dt: datetime, end_dt: datetime) -> int:
        patients = User.objects.filter(role="patient")
        if not patients.exists():
            self.stdout.write(self.style.ERROR("No patient users found. Create patient accounts first."))
            return 0

        medical_conditions = [
            "Hypertension", "Diabetes", "Heart Disease", "Asthma", "Arthritis",
            "Depression", "Anxiety", "Obesity", "High Cholesterol", "Migraine",
            "Pneumonia", "Bronchitis", "Flu", "Cold", "Fever",
            "Gastroenteritis", "Appendicitis", "Fracture", "Sprain", "Burn"
        ]
        medications = [
            "Metformin", "Lisinopril", "Atorvastatin", "Omeprazole", "Albuterol",
            "Sertraline", "Lorazepam", "Ibuprofen", "Acetaminophen", "Aspirin",
            "Amoxicillin", "Ciprofloxacin", "Prednisone", "Warfarin", "Insulin",
            "Furosemide", "Digoxin", "Morphine", "Codeine", "Tramadol"
        ]

        self.stdout.write(f"Creating {count} patient records from {start_dt.date()} to {end_dt.date()}...")
        created = 0
        total_days = max(1, (end_dt - start_dt).days)
        for i in range(count):
            try:
                patient = random.choice(list(patients))
                # Distribute dates with slight weekly peaks
                offset = random.randint(0, total_days)
                random_dt = start_dt + timedelta(days=offset, hours=random.randint(0, 23), minutes=random.randint(0, 59))

                PatientRecord.objects.create(
                    patient=patient,
                    date_of_admission=random_dt,
                    medical_condition=random.choice(medical_conditions),
                    age=random.randint(18, 85),
                    gender=random.choices(["Male", "Female", "Other"], weights=[48, 48, 4])[0],
                    medication=random.choice(medications) if random.random() > 0.25 else None,
                    severity=random.choices(["Low", "Medium", "High", "Critical"], weights=[35, 40, 20, 5])[0],
                    treatment_outcome=random.choices(["Recovered", "Ongoing", "Transferred", "Deceased"], weights=[64, 25, 8, 3])[0],
                )
                created += 1
            except Exception as e:
                self.stdout.write(f"Error creating record {i}: {str(e)}")
        return created

    # --- Analytics ---
    def _create_analytics_results(self, start_dt: datetime, end_dt: datetime) -> None:
        # Aggregate demographics
        qs = PatientRecord.objects.filter(date_of_admission__range=(start_dt, end_dt))
        total = qs.count()
        age_groups = {"0-18": 0, "19-35": 0, "36-50": 0, "51-65": 0, "65+": 0}
        genders = {"Male": 0, "Female": 0, "Other": 0}
        for r in qs.values("age", "gender"):
            a = r["age"] or 0
            if a <= 18:
                age_groups["0-18"] += 1
            elif a <= 35:
                age_groups["19-35"] += 1
            elif a <= 50:
                age_groups["36-50"] += 1
            elif a <= 65:
                age_groups["51-65"] += 1
            else:
                age_groups["65+"] += 1
            g = r["gender"] or "Other"
            genders[g] = genders.get(g, 0) + 1

        demographics_data = {
            "age_distribution": age_groups,
            "gender_proportions": genders,
            "total_patients": total,
            "average_age": round(sum([r["age"] for r in qs.values("age") if r["age"]]) / max(1, total), 1) if total else 0,
        }
        AnalyticsResult.objects.create(
            analysis_type="patient_demographics",
            status="completed",
            results=demographics_data,
        )

        # Medication analysis (Pareto-like top meds)
        med_counts: Dict[str, int] = {}
        for r in qs.values_list("medication", flat=True):
            if r:
                med_counts[r] = med_counts.get(r, 0) + 1
        pareto = sorted([{"medication": k, "prescriptions": v} for k, v in med_counts.items()], key=lambda x: x["prescriptions"], reverse=True)
        medication_data = {
            "medication_pareto_data": pareto[:20],
            "medication_usage": pareto,
        }
        AnalyticsResult.objects.create(
            analysis_type="medication_analysis",
            status="completed",
            results=medication_data,
        )

        # Patient volume prediction (simple synthetic forecast from daily counts)
        # Build daily series
        daily_counts: Dict[str, int] = {}
        for r in qs.values_list("date_of_admission", flat=True):
            key = (r.date()).strftime("%Y-%m-%d")
            daily_counts[key] = daily_counts.get(key, 0) + 1
        days_sorted = sorted(daily_counts.items())
        forecasted = []
        base_mae = 0.0
        base_rmse = 0.0
        if days_sorted:
            # naive forecast: next 8 days around recent average
            avg = sum([c for _, c in days_sorted[-30:]]) / max(1, min(30, len(days_sorted)))
            today = end_dt.date()
            for i in range(1, 9):
                jitter = random.uniform(-0.3, 0.3)
                value = max(0, int(round(avg * (1 + jitter))))
                forecasted.append({
                    "date": (today + timedelta(days=i)).strftime("%Y-%m-%d"),
                    "predicted": value,
                    "actual": None,
                })
            # basic metrics
            actual_vals = [c for _, c in days_sorted[-8:]]
            preds = [item[1] for item in days_sorted[-8:]]
            if actual_vals and preds:
                base_mae = round(sum(abs(a - p) for a, p in zip(actual_vals, preds)) / len(actual_vals), 2)
                base_rmse = round((sum((a - p) ** 2 for a, p in zip(actual_vals, preds)) / len(actual_vals)) ** 0.5, 2)

        volume_data = {
            "forecasted_data": forecasted,
            "evaluation_metrics": {"mae": base_mae or round(random.uniform(0.5, 2.5), 2), "rmse": base_rmse or round(random.uniform(0.8, 3.2), 2)},
            "comparison_data": [{"date": d, "predicted": p, "actual": a} for (d, a), (_, p) in zip(days_sorted[-8:], days_sorted[-8:])],
        }
        AnalyticsResult.objects.create(
            analysis_type="patient_volume_prediction",
            status="completed",
            results=volume_data,
        )

        # Health trends (top conditions weekly sample)
        cond_counts: Dict[str, int] = {}
        for r in qs.values_list("medical_condition", flat=True):
            cond_counts[r] = cond_counts.get(r, 0) + 1
        common_conditions = [c for c, _ in sorted(cond_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
        trends_data = {
            "top_illnesses_by_week": [
                {"medical_condition": c, "count": random.randint(5, 25), "week": f"Week {i+1}"}
                for i, c in enumerate(common_conditions)
            ],
            "trend_analysis": {
                "increasing_conditions": common_conditions[:2],
                "decreasing_conditions": common_conditions[2:4],
                "stable_conditions": common_conditions[4:5],
            },
        }
        AnalyticsResult.objects.create(
            analysis_type="patient_health_trends",
            status="completed",
            results=trends_data,
        )

    # --- Inventory ---
    def _seed_medicine_inventory(self, categories: List[str], count: int, nurse_email: str | None, purge: bool) -> None:
        # Resolve target nurses
        if nurse_email:
            targets = list(NurseProfile.objects.filter(user__email=nurse_email))
            if not targets:
                raise CommandError(f"No NurseProfile found for email: {nurse_email}")
        else:
            targets = list(NurseProfile.objects.all())
            if not targets:
                raise CommandError("No NurseProfile records found. Create at least one nurse user first.")

        for nurse in targets:
            if purge:
                deleted, _ = MedicineInventory.objects.filter(inventory=nurse).delete()
                self.stdout.write(self.style.WARNING(f"Purged {deleted} inventory records for nurse {nurse.user.email}"))

            # Build pool from selected categories
            pool: List[Tuple[str, str, Decimal]] = []
            for c in categories:
                pool.extend(MEDICINE_CATALOG.get(c, []))
            random.shuffle(pool)
            if count > len(pool):
                pool = (pool * ((count // len(pool)) + 1))[:count]
            else:
                pool = pool[:count]

            created_total = 0
            updated_total = 0
            for idx, (name, usage, unit_price) in enumerate(pool, start=1):
                min_level = random.randint(10, 50)
                current_stock, stock_number = _rand_stock_scenario(min_level)
                expiry_date, expiry_kind = _rand_expiry_scenario()
                batch_number = _gen_batch_number(idx)

                defaults = {
                    "inventory": nurse,
                    "medicine_name": name,
                    "stock_number": stock_number,
                    "current_stock": current_stock,
                    "unit_price": unit_price,
                    "minimum_stock_level": min_level,
                    "expiry_date": expiry_date,
                    "usage_pattern": f"{usage} Stock scenario: {expiry_kind}.",
                }

                obj, created = MedicineInventory.objects.update_or_create(
                    batch_number=batch_number,
                    defaults=defaults,
                )
                if created:
                    created_total += 1
                else:
                    updated_total += 1

            self.stdout.write(self.style.SUCCESS(
                f"Seeded inventory for nurse {nurse.user.email}: {created_total} created, {updated_total} updated."
            ))