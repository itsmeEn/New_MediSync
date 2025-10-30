from datetime import date, timedelta
from typing import List

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.db import transaction

from django.db.models import F
from backend.operations.models import MedicineInventory, Notification
from backend.users.models import NurseProfile


def format_alert_lines(items: List[MedicineInventory]) -> List[str]:
    lines = []
    for mi in items:
        status = "OUT OF STOCK" if mi.current_stock == 0 else (
            "LOW STOCK" if mi.current_stock <= mi.minimum_stock_level else "OK"
        )
        expiry_str = mi.expiry_date.strftime("%Y-%m-%d") if mi.expiry_date else "N/A"
        lines.append(
            f"- {mi.medicine_name} | qty={mi.current_stock} (min={mi.minimum_stock_level}) | expiry={expiry_str} | {status}"
        )
    return lines


class Command(BaseCommand):
    help = "Send email notifications to nurses for low-stock and expiring-soon medicines"

    def add_arguments(self, parser):
        parser.add_argument("--nurse-email", type=str, default=None,
                            help="Target a single nurse by email; defaults to all nurses")
        parser.add_argument("--days", type=int, default=21,
                            help="Consider medicines expiring within N days (default: 21)")
        parser.add_argument("--include-expired", action="store_true",
                            help="Also include already expired medicines in alerts")
        parser.add_argument("--only-new", action="store_true",
                            help="Only include items without a linked Notification (avoid re-sending)")
        parser.add_argument("--dry-run", action="store_true",
                            help="Do not send emails, just print the would-be alerts")

    @transaction.atomic
    def handle(self, *args, **options):
        nurse_email = options.get("nurse_email")
        days = options.get("days")
        include_expired = options.get("include_expired")
        only_new = options.get("only_new")
        dry_run = options.get("dry_run")

        # Resolve nurses
        if nurse_email:
            nurses = list(NurseProfile.objects.filter(user__email=nurse_email))
            if not nurses:
                raise CommandError(f"No NurseProfile found for email: {nurse_email}")
        else:
            nurses = list(NurseProfile.objects.all())
            if not nurses:
                raise CommandError("No NurseProfile records found.")

        today = date.today()
        soon_cutoff = today + timedelta(days=days)
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@medisync.local')

        total_sent = 0
        for nurse in nurses:
            # Query medicines for nurse
            qs = MedicineInventory.objects.filter(inventory=nurse)
            # Low stock or out of stock
            low_items = list(qs.filter(current_stock__lte=F('minimum_stock_level')).order_by('medicine_name'))
            out_items = list(qs.filter(current_stock=0).order_by('medicine_name'))

            # Expiring soon and expired
            expiring_items = list(qs.filter(expiry_date__isnull=False, expiry_date__lte=soon_cutoff, expiry_date__gte=today).order_by('expiry_date'))
            expired_items = list(qs.filter(expiry_date__isnull=False, expiry_date__lt=today).order_by('expiry_date'))

            alerts: List[MedicineInventory] = []
            alerts.extend(out_items)
            alerts.extend([mi for mi in low_items if mi not in alerts])
            alerts.extend([mi for mi in expiring_items if mi not in alerts])
            if include_expired:
                alerts.extend([mi for mi in expired_items if mi not in alerts])

            if only_new:
                alerts = [mi for mi in alerts if mi.notification_id is None]

            if not alerts:
                self.stdout.write(self.style.WARNING(f"No alerts for nurse {nurse.user.email}"))
                continue

            # Compose email
            subject = "Medicine Inventory Alerts: Low Stock and Expiring Soon"
            body_lines = [
                f"Hello {nurse.user.full_name or 'Nurse'},",
                "",
                "The following inventory items need attention:",
                "",
            ]
            body_lines.extend(format_alert_lines(alerts))
            body_lines.extend([
                "",
                "Recommended actions:",
                "- Reorder items at or below minimum stock levels",
                "- Prioritize dispensing items expiring soon",
                "- Discard or return expired items per policy",
                "",
                "This is an automated notification from MediSync.",
            ])
            message = "\n".join(body_lines)

            if dry_run:
                self.stdout.write(self.style.NOTICE(f"DRY RUN: Would send email to {nurse.user.email} with {len(alerts)} items"))
            else:
                try:
                    send_mail(subject, message, from_email, [nurse.user.email], fail_silently=False)
                    total_sent += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Failed to send email to {nurse.user.email}: {e}"))

                # Create Notification and link to each item only when actually sending
                notif = Notification.objects.create(
                    user=nurse.user,
                    message=f"{len(alerts)} inventory items require attention (low stock or expiring soon)."
                )
                for mi in alerts:
                    mi.notification = notif
                    mi.save(update_fields=["notification"])

            self.stdout.write(self.style.SUCCESS(f"Prepared alerts for nurse {nurse.user.email}: {len(alerts)} items"))

        self.stdout.write(self.style.SUCCESS(f"Completed sending alerts. Emails sent: {total_sent}"))