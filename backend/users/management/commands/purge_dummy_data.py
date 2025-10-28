from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from django.apps import apps


class Command(BaseCommand):
    help = "Purge dummy/test data from the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without making changes",
        )
        parser.add_argument(
            "--include-analytics",
            action="store_true",
            help="Also purge mock analytics results created by populate commands",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        include_analytics = options["include_analytics"]

        User = get_user_model()
        PatientRecord = apps.get_model("analytics", "PatientRecord")
        AnalyticsResult = apps.get_model("analytics", "AnalyticsResult")

        # 1) Identify dummy users by email domain (example.com used in tests/seeds)
        dummy_users_qs = User.objects.filter(email__iendswith="@example.com")
        dummy_user_count = dummy_users_qs.count()

        # 2) Identify dummy patient records
        patient_records_count = 0
        dummy_patient_records_qs = None
        has_is_dummy_field = False
        try:
            # Check if 'is_dummy_data' exists on the model
            PatientRecord._meta.get_field("is_dummy_data")
            has_is_dummy_field = True
        except Exception:
            has_is_dummy_field = False

        if has_is_dummy_field:
            dummy_patient_records_qs = PatientRecord.objects.filter(is_dummy_data=True)
        else:
            # Fallback: any patient records whose patient user is a dummy user
            dummy_patient_records_qs = PatientRecord.objects.filter(
                patient__email__iendswith="@example.com"
            )
        patient_records_count = dummy_patient_records_qs.count()

        # 3) Optionally identify mock analytics results created by populate commands
        analytics_count = 0
        analytics_qs = AnalyticsResult.objects.none()
        if include_analytics:
            # Heuristic: results with no processed_by and status completed
            analytics_qs = AnalyticsResult.objects.filter(processed_by__isnull=True)
            analytics_count = analytics_qs.count()

        # Summary
        self.stdout.write("\n=== Dummy Data Purge Summary ===")
        self.stdout.write(f"Dummy users (@example.com): {dummy_user_count}")
        self.stdout.write(f"Dummy patient records: {patient_records_count}")
        if include_analytics:
            self.stdout.write(f"Mock analytics results (unassigned): {analytics_count}")
        else:
            self.stdout.write("Mock analytics results: skipped (use --include-analytics)")

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry-run mode: no changes made."))
            return

        # Execute purge in a single transaction
        with transaction.atomic():
            # Delete patient records first to avoid large cascades if desired
            pr_deleted = dummy_patient_records_qs.delete()
            self.stdout.write(self.style.WARNING(f"Deleted patient records: {pr_deleted[0]}"))

            # Delete dummy users (cascades to profiles and related FKs)
            users_deleted = dummy_users_qs.delete()
            self.stdout.write(self.style.WARNING(f"Deleted users: {users_deleted[0]}"))

            # Optionally delete analytics
            if include_analytics:
                analytics_deleted = analytics_qs.delete()
                self.stdout.write(self.style.WARNING(f"Deleted analytics results: {analytics_deleted[0]}"))

        self.stdout.write(self.style.SUCCESS("Dummy data purge completed successfully."))