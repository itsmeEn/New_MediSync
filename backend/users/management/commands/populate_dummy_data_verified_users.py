import json
import logging
from typing import Any, Dict, List, Optional

from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError, OperationalError

from backend.users.models import User


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Retrieve all verified users belonging to a specified hospital context "
        "and output them as a structured JSON array."
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--hospital",
            type=str,
            help="Hospital name to filter users (case-insensitive exact match)",
        )
        parser.add_argument(
            "--user-id",
            type=int,
            help="Optional: derive hospital context from a given User ID",
        )
        parser.add_argument(
            "--user-email",
            type=str,
            help="Optional: derive hospital context from a given User email",
        )
        parser.add_argument(
            "--output",
            type=str,
            help="Optional: path to write JSON output to a file (prints to stdout otherwise)",
        )
        parser.add_argument(
            "--strict",
            action="store_true",
            help=(
                "If set, require both verification_status='approved' AND is_verified=True. "
                "By default, only verification_status='approved' is required to match admin approval behavior."
            ),
        )

    def _resolve_hospital(self, hospital: Optional[str], user_id: Optional[int], user_email: Optional[str]) -> str:
        """
        Resolve hospital context from provided args. Prefer explicit --hospital,
        otherwise derive from user_id or user_email. Raise CommandError if missing.
        """
        if hospital:
            return hospital.strip()

        # Derive from user-id
        if user_id:
            try:
                user = User.objects.only("hospital_name").get(id=user_id)
                if not user.hospital_name:
                    raise CommandError(
                        "Hospital context missing: The specified user has no hospital_name set."
                    )
                return user.hospital_name.strip()
            except User.DoesNotExist:
                raise CommandError(f"User with id={user_id} not found")

        # Derive from user-email
        if user_email:
            try:
                user = User.objects.only("hospital_name").get(email=user_email)
                if not user.hospital_name:
                    raise CommandError(
                        "Hospital context missing: The specified user has no hospital_name set."
                    )
                return user.hospital_name.strip()
            except User.DoesNotExist:
                raise CommandError(f"User with email={user_email} not found")

        raise CommandError(
            "Hospital context is required. Provide --hospital or --user-id/--user-email to derive it."
        )

    def handle(self, *args: Any, **options: Dict[str, Any]) -> None:
        hospital_arg: Optional[str] = options.get("hospital")
        user_id: Optional[int] = options.get("user_id")
        user_email: Optional[str] = options.get("user_email")
        output_path: Optional[str] = options.get("output")
        strict: bool = bool(options.get("strict"))

        try:
            hospital = self._resolve_hospital(hospital_arg, user_id, user_email)
            self.stdout.write(self.style.NOTICE(f"Using hospital context: '{hospital}'"))
            logger.info("populate_dummy_data_verified_users:start", extra={"hospital": hospital})

            # Filter verified doctors and nurses in the SAME hospital
            base_filters = {
                "role__in": ["doctor", "nurse"],
                "is_active": True,
                "verification_status": "approved",
                "hospital_name__iexact": hospital,
            }
            if strict:
                base_filters["is_verified"] = True
            queryset = User.objects.filter(**base_filters).order_by("full_name")

            # Select relevant fields
            users: List[Dict[str, Any]] = list(
                queryset.values(
                    "id",
                    "full_name",
                    "email",
                    "verification_status",
                    "hospital_name",
                    "hospital_address",
                )
            )

            count = len(users)
            logger.info(
                "populate_dummy_data_verified_users:results",
                extra={"hospital": hospital, "count": count, "strict": strict},
            )

            if count == 0:
                msg = f"No verified users found for hospital '{hospital}'."
                self.stderr.write(self.style.WARNING(msg))
                logger.warning("populate_dummy_data_verified_users:empty", extra={"hospital": hospital})

            # Output as JSON
            payload = json.dumps(users, indent=2)
            if output_path:
                try:
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(payload)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Wrote {count} user(s) to '{output_path}'"
                        )
                    )
                except OSError as fs_err:
                    logger.error(
                        "populate_dummy_data_verified_users:write_failed",
                        extra={"error": str(fs_err), "output_path": output_path},
                    )
                    raise CommandError(f"Failed to write output file: {fs_err}")
            else:
                # Print to stdout
                self.stdout.write(payload)

        except OperationalError as db_op_err:
            logger.error(
                "populate_dummy_data_verified_users:db_operational_error",
                extra={"error": str(db_op_err)},
            )
            raise CommandError(
                f"Database connection issue: {db_op_err}. Ensure the database is reachable."
            )
        except DatabaseError as db_err:
            logger.error(
                "populate_dummy_data_verified_users:db_error",
                extra={"error": str(db_err)},
            )
            raise CommandError(f"Database error: {db_err}")
        except CommandError:
            # Already logged; re-raise to stop execution with error code
            raise
        except Exception as e:
            logger.error(
                "populate_dummy_data_verified_users:unexpected",
                extra={"error": str(e)},
            )
            raise CommandError(f"Unexpected error: {e}")