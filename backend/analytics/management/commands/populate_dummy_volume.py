import random
from datetime import timedelta
from typing import Dict, List, Tuple

from django.core.management.base import BaseCommand
from django.utils import timezone

from backend.analytics.models import AnalyticsResult, PatientRecord


class Command(BaseCommand):
    help = "Create a dummy AnalyticsResult for patient volume prediction"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="Number of past days to build baseline counts (default: 30)",
        )
        parser.add_argument(
            "--forecast",
            type=int,
            default=8,
            help="Forecast horizon in days for future predictions (default: 8)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing patient volume AnalyticsResult entries before seeding",
        )
        parser.add_argument(
            "--baseline",
            type=int,
            default=20,
            help="Baseline synthetic daily volume when records are sparse (default: 20)",
        )
        parser.add_argument(
            "--jitter",
            type=float,
            default=0.35,
            help="Relative jitter applied to forecasts (default: 0.35)",
        )

    def handle(self, *args, **options):
        days: int = options.get("days")
        horizon: int = options.get("forecast")
        clear: bool = options.get("clear")
        baseline: int = options.get("baseline")
        jitter: float = options.get("jitter")

        if clear:
            deleted, _ = AnalyticsResult.objects.filter(
                analysis_type="patient_volume_prediction"
            ).delete()
            self.stdout.write(self.style.WARNING(f"Cleared {deleted} patient volume analytics entries"))

        end_dt = timezone.now()
        start_dt = end_dt - timedelta(days=days)

        # Build daily counts from PatientRecord if available; otherwise synthesize
        daily_counts: Dict[str, int] = {}
        qs = PatientRecord.objects.filter(date_of_admission__range=(start_dt, end_dt))
        if qs.exists():
            for dt in qs.values_list("date_of_admission", flat=True):
                key = dt.date().strftime("%Y-%m-%d")
                daily_counts[key] = daily_counts.get(key, 0) + 1
        else:
            # Simple synthetic baseline with light weekly seasonality
            for i in range(days):
                d = (start_dt + timedelta(days=i)).date().strftime("%Y-%m-%d")
                weekday_factor = 1.1 if (start_dt + timedelta(days=i)).weekday() in (0, 1) else 0.9
                val = max(0, int(round(baseline * weekday_factor * (1 + random.uniform(-0.25, 0.25)))))
                daily_counts[d] = val

        days_sorted: List[Tuple[str, int]] = sorted(daily_counts.items())

        # Forecast next horizon days using recent average + jitter
        forecasted: List[Dict[str, int | None]] = []
        avg_recent = (
            sum(c for _, c in days_sorted[-min(30, len(days_sorted)):])
            / max(1, min(30, len(days_sorted)))
            if days_sorted
            else baseline
        )
        today = end_dt.date()
        for i in range(1, horizon + 1):
            j = random.uniform(-jitter, jitter)
            value = max(0, int(round(avg_recent * (1 + j))))
            forecasted.append({
                "date": (today + timedelta(days=i)).strftime("%Y-%m-%d"),
                "predicted": value,
                "actual": None,
            })

        # Comparison data for the most recent period
        comparison_span = min(horizon, len(days_sorted))
        comparison_data = [
            {
                "date": d,
                "predicted": max(0, int(round(c * (1 + random.uniform(-0.15, 0.15))))),
                "actual": c,
            }
            for d, c in days_sorted[-comparison_span:]
        ]

        # Basic metrics (synthetic if historical is thin)
        if comparison_data:
            diffs = [abs(item["actual"] - item["predicted"]) for item in comparison_data]
            mae = round(sum(diffs) / len(diffs), 2)
            rmse = round((sum(d * d for d in diffs) / len(diffs)) ** 0.5, 2)
        else:
            mae = round(random.uniform(0.5, 2.5), 2)
            rmse = round(random.uniform(0.8, 3.2), 2)

        payload = {
            "forecasted_data": forecasted,
            "evaluation_metrics": {"mae": mae, "rmse": rmse},
            "comparison_data": comparison_data,
        }

        AnalyticsResult.objects.create(
            analysis_type="patient_volume_prediction",
            status="completed",
            results=payload,
        )

        self.stdout.write(self.style.SUCCESS(
            f"Seeded patient volume analytics: horizon={horizon}, baseline_days={days}, records={len(days_sorted)}"
        ))