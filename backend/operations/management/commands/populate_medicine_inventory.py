import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from backend.operations.models import MedicineInventory
from backend.users.models import NurseProfile


COMMON_MEDICINES = [
    # name, usage notes, typical unit price
    ("Paracetamol 500mg Tablet", "Analgesic and antipyretic; take as needed for pain/fever.", Decimal("0.50")),
    ("Amoxicillin 500mg Capsule", "Antibiotic; complete full course as prescribed.", Decimal("1.20")),
    ("Ibuprofen 400mg Tablet", "NSAID; take with food; avoid long-term use.", Decimal("0.70")),
    ("Metformin 500mg Tablet", "Antidiabetic; take with meals; monitor blood sugar.", Decimal("0.60")),
    ("Amlodipine 5mg Tablet", "Antihypertensive; once daily dosing.", Decimal("0.80")),
    ("Losartan 50mg Tablet", "Antihypertensive; monitor BP regularly.", Decimal("0.90")),
    ("Omeprazole 20mg Capsule", "Proton pump inhibitor; take before meals.", Decimal("0.85")),
    ("Salbutamol Inhaler 100mcg", "Bronchodilator; 2 puffs as needed.", Decimal("5.50")),
    ("Cefuroxime 500mg Tablet", "Antibiotic; complete full course as prescribed.", Decimal("1.80")),
    ("Azithromycin 500mg Tablet", "Antibiotic; once daily; complete course.", Decimal("2.20")),
    ("Atorvastatin 20mg Tablet", "Statin; take at night; monitor lipids.", Decimal("1.40")),
    ("Hydrochlorothiazide 25mg Tablet", "Diuretic; monitor electrolytes.", Decimal("0.75")),
    ("Diclofenac 50mg Tablet", "NSAID; take with food.", Decimal("0.65")),
    ("Prednisone 10mg Tablet", "Corticosteroid; taper as directed.", Decimal("0.90")),
    ("Warfarin 5mg Tablet", "Anticoagulant; monitor INR.", Decimal("0.95")),
    ("Insulin Glargine 100U/mL", "Basal insulin; dose per protocol.", Decimal("12.00")),
    ("Ranitidine 150mg Tablet", "H2 blocker; twice daily.", Decimal("0.55")),
    ("Cetirizine 10mg Tablet", "Antihistamine; once daily.", Decimal("0.50")),
    ("Doxycycline 100mg Capsule", "Antibiotic; twice daily; complete course.", Decimal("1.30")),
    ("Acetylcysteine 200mg Sachet", "Expectorant; dissolve in water.", Decimal("1.00")),
    ("Clopidogrel 75mg Tablet", "Antiplatelet; once daily.", Decimal("1.10")),
    ("Budesonide/Formoterol Inhaler", "ICS/LABA; maintenance inhaler.", Decimal("9.50")),
    ("Loperamide 2mg Capsule", "Antidiarrheal; as needed.", Decimal("0.40")),
    ("ORS Packet", "Oral rehydration salts; dissolve in clean water.", Decimal("0.30")),
    ("Amoxicillin/Clavulanate 625mg", "Antibiotic; take with food; complete course.", Decimal("2.80")),
    ("Fluconazole 150mg Capsule", "Antifungal; single dose typical.", Decimal("1.70")),
    ("Guaifenesin 100mg/5mL Syrup", "Expectorant; dose per label.", Decimal("2.00")),
    ("Dextromethorphan 15mg/5mL Syrup", "Antitussive; nighttime.", Decimal("2.10")),
    ("Aspirin 81mg Tablet", "Antiplatelet; once daily.", Decimal("0.35")),
    ("Naproxen 250mg Tablet", "NSAID; take with food.", Decimal("0.85")),
    ("Levothyroxine 50mcg Tablet", "Thyroid hormone; daily before breakfast.", Decimal("0.75")),
    ("Folic Acid 5mg Tablet", "Supplement; daily.", Decimal("0.25")),
    ("Vitamin B Complex Tablet", "Supplement; daily.", Decimal("0.40")),
    ("Vitamin D3 1000IU Capsule", "Supplement; daily.", Decimal("0.50")),
    ("Calcium Carbonate 500mg Tablet", "Supplement; with meals.", Decimal("0.55")),
    ("Iron (Ferrous Sulfate) 325mg", "Supplement; may cause GI upset.", Decimal("0.45")),
    ("Magnesium Oxide 400mg Tablet", "Supplement; daily.", Decimal("0.60")),
    ("Multivitamins Syrup", "Supplement; pediatric dosing per label.", Decimal("3.50")),
    ("Cough Cold Combo Tablet", "Symptomatic relief; drowsiness possible.", Decimal("0.65")),
]


def rand_expiry_scenario():
    """Pick an expiry scenario and return a date accordingly."""
    scenario = random.choice(["expired", "expiring_soon", "normal_long"])
    today = date.today()
    if scenario == "expired":
        # Already expired 7–60 days ago
        return today - timedelta(days=random.randint(7, 60)), scenario
    elif scenario == "expiring_soon":
        # Expiring within 7–21 days
        return today + timedelta(days=random.randint(7, 21)), scenario
    else:
        # Normal long expiry 6–18 months
        return today + timedelta(days=random.randint(180, 540)), scenario


def rand_stock_scenario(min_level: int):
    """Pick stock scenario and return current_stock, stock_number."""
    scenario = random.choice(["out_of_stock", "low_stock", "in_stock", "overstock"])
    if scenario == "out_of_stock":
        current = 0
    elif scenario == "low_stock":
        current = random.randint(0, max(1, min_level))
    elif scenario == "in_stock":
        current = random.randint(min_level + 5, min_level + 40)
    else:  # overstock
        current = random.randint(min_level + 50, min_level + 200)
    return current, current


def gen_batch_number(idx: int) -> str:
    return f"BN-{timezone.now().strftime('%Y%m%d')}-{idx:04d}-{random.randint(1000,9999)}"


class Command(BaseCommand):
    help = "Populate nurse medicine inventory with comprehensive, realistic test data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--nurse-email",
            type=str,
            default=None,
            help="Seed inventory for a specific nurse user email. Defaults to all nurses.",
        )
        parser.add_argument(
            "--count",
            type=int,
            default=40,
            help="Approximate number of distinct medicines to create per nurse (defaults to 40).",
        )
        parser.add_argument(
            "--purge",
            action="store_true",
            help="Delete existing MedicineInventory records for targeted nurse(s) before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        nurse_email = options.get("nurse_email")
        count = options.get("count")
        purge = options.get("purge")

        # Resolve target nurse profiles
        if nurse_email:
            targets = list(NurseProfile.objects.filter(user__email=nurse_email))
            if not targets:
                raise CommandError(f"No NurseProfile found for email: {nurse_email}")
        else:
            targets = list(NurseProfile.objects.all())
            if not targets:
                raise CommandError("No NurseProfile records found. Create at least one nurse user first.")

        created_total = 0
        updated_total = 0
        for nurse in targets:
            if purge:
                deleted, _ = MedicineInventory.objects.filter(inventory=nurse).delete()
                self.stdout.write(self.style.WARNING(f"Purged {deleted} inventory records for nurse {nurse.user.email}"))

            # Build a pool of base medicines and sample up to 'count'
            base_pool = COMMON_MEDICINES.copy()
            random.shuffle(base_pool)
            if count > len(base_pool):
                # Repeat from the start to meet requested count while varying batch/expiry
                base_pool = (base_pool * ((count // len(base_pool)) + 1))[:count]
            else:
                base_pool = base_pool[:count]

            for idx, (name, usage, unit_price) in enumerate(base_pool, start=1):
                # Minimum stock level: vary 10–50
                min_level = random.randint(10, 50)
                # Stock scenario
                current_stock, stock_number = rand_stock_scenario(min_level)
                # Expiry scenario
                expiry_date, expiry_kind = rand_expiry_scenario()
                # Generate batch number (unique constraint)
                batch_number = gen_batch_number(idx)

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

                # Use update_or_create keyed by batch_number to avoid duplicates on rerun
                obj, created = MedicineInventory.objects.update_or_create(
                    batch_number=batch_number,
                    defaults=defaults,
                )
                if created:
                    created_total += 1
                else:
                    updated_total += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Seeded inventory for nurse {nurse.user.email}: {created_total} created, {updated_total} updated."
                )
            )

        self.stdout.write(self.style.SUCCESS("Completed medicine inventory seeding."))