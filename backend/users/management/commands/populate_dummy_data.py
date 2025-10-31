import json
import logging
from typing import Optional

from django.core.management.base import BaseCommand, CommandError

from backend.utils.dummy_data import populate_dummy_data


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Populate realistic dummy data scoped to a hospital instance."

    def add_arguments(self, parser):
        parser.add_argument('--hospital-name', default='Catanduanes Medical Hospital', help='Hospital name to scope data')
        parser.add_argument('--hospital-address', default='San Isidro Village, Virac, Catanduanes', help='Hospital address to scope data')
        parser.add_argument('--hospital-phone', default='+63 (52) 811-1234', help='Hospital contact phone number')
        parser.add_argument('--hospital-email', default='info@catanduanesmedical.ph', help='Hospital contact email address')
        parser.add_argument('--patients', type=int, default=50, help='Number of patients to create')
        parser.add_argument('--nurses', type=int, default=20, help='Number of nurses to create')
        parser.add_argument('--appointments-per-patient', type=int, default=2)
        parser.add_argument('--dry-run', action='store_true', help='Create and rollback without persisting')
        parser.add_argument('--cleanup', action='store_true', help='Delete created records after verification')
        parser.add_argument('--no-verify', action='store_true', help='Skip verification steps')

    def handle(self, *args, **options):
        hospital_name: str = options['hospital_name']
        hospital_address: str = options['hospital_address']
        patients: int = options['patients']
        nurses: int = options['nurses']
        appt_per_patient: int = options['appointments_per_patient']
        dry_run: bool = options['dry_run']
        cleanup: bool = options['cleanup']
        verify: bool = not options['no_verify']
        hospital_phone: str = options['hospital_phone']
        hospital_email: str = options['hospital_email']

        try:
            self.stdout.write(self.style.NOTICE('Starting dummy data population...'))
            result = populate_dummy_data(
                hospital_name=hospital_name,
                hospital_address=hospital_address,
                num_patients=patients,
                appointments_per_patient=appt_per_patient,
                nurses_count=nurses,
                hospital_phone=hospital_phone,
                hospital_email=hospital_email,
                dry_run=dry_run,
                cleanup=cleanup,
                verify=verify,
            )
            self.stdout.write(json.dumps(result, indent=2))
            if result.get('errors'):
                self.stdout.write(self.style.WARNING('Completed with errors.'))
            else:
                self.stdout.write(self.style.SUCCESS('Completed successfully.'))
        except Exception as e:
            logger.exception("Command failed: %s", e)
            raise CommandError(str(e))