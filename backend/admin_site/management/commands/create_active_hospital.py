from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.core.files.base import ContentFile

from backend.admin_site.models import Hospital


class Command(BaseCommand):
    help = "Create or activate a Hospital record to ACTIVE for local testing."

    def add_arguments(self, parser):
        parser.add_argument("--name", required=False, default="Catanduanes Medical Hospital",
                            help="Official hospital name")
        parser.add_argument("--address", required=False, default="San Isidro Village, Virac, Catanduanes",
                            help="Hospital address")
        parser.add_argument("--license-id", required=False, default="LIC-DEMO-001",
                            help="Unique license ID")
        parser.add_argument("--doc-name", required=False, default="license_demo.pdf",
                            help="License document filename to store")
        parser.add_argument("--doc-bytes", required=False, default=b"Demo license document for local testing.",
                            help="Raw bytes for the license document (for simple seed)")

    def handle(self, *args, **options):
        name = options["name"]
        address = options["address"]
        license_id = options["license_id"]
        doc_name = options["doc_name"]
        # doc_bytes may come in as str via argparse; normalize to bytes
        doc_bytes = options["doc_bytes"]
        if isinstance(doc_bytes, str):
            doc_bytes = doc_bytes.encode("utf-8")

        try:
            hosp, created = Hospital.objects.get_or_create(
                license_id=license_id,
                defaults={
                    "official_name": name,
                    "address": address,
                    "status": Hospital.Status.PENDING,
                },
            )

            # Update name/address if changed
            updated = False
            if hosp.official_name != name:
                hosp.official_name = name
                updated = True
            if hosp.address != address:
                hosp.address = address
                updated = True

            # Ensure we have a license document stored
            if not hosp.license_document:
                hosp.license_document.save(doc_name, ContentFile(doc_bytes), save=False)
                updated = True

            # Activate hospital
            hosp.status = Hospital.Status.ACTIVE
            hosp.activated_at = timezone.now()
            updated = True

            if updated:
                hosp.save()

            self.stdout.write(self.style.SUCCESS(
                f"Hospital ready: id={hosp.id} name='{hosp.official_name}' status={hosp.status}"
            ))

        except Exception as e:
            raise CommandError(f"Failed to create/activate hospital: {e}")