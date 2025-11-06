import logging
from typing import Any, Dict, List, Optional

from django.core.management.base import BaseCommand, CommandError

from backend.users.models import User


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Mark users in a hospital as verified/approved, optionally scoped by roles."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--hospital",
            type=str,
            required=True,
            help="Hospital name to scope verification (case-insensitive exact match)",
        )
        parser.add_argument(
            "--roles",
            nargs="*",
            default=["doctor", "nurse", "patient"],
            help="Roles to include (default: doctor nurse patient)",
        )

    def handle(self, *args: Any, **options: Dict[str, Any]) -> None:
        hospital: str = options["hospital"]
        roles: List[str] = options["roles"]

        # Normalize roles to known values
        valid_roles = {User.Role.DOCTOR: "doctor", User.Role.NURSE: "nurse", User.Role.PATIENT: "patient"}
        role_values = set(valid_roles.values())
        roles = [r.lower() for r in roles if r.lower() in role_values]
        if not roles:
            raise CommandError("No valid roles provided. Use any of: doctor nurse patient")

        base_filters = {
            "role__in": roles,
            "hospital_name__iexact": hospital,
        }
        qs = User.objects.filter(**base_filters)
        total = qs.count()
        updated = 0

        for u in qs.iterator():
            try:
                u.verification_status = "approved"
            except Exception:
                pass
            try:
                u.is_verified = True
            except Exception:
                pass
            try:
                u.save(update_fields=["verification_status", "is_verified"])
            except Exception:
                u.save()
            updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"Verified users updated: {updated}/{total} in hospital '{hospital}' for roles {', '.join(roles)}"
        ))