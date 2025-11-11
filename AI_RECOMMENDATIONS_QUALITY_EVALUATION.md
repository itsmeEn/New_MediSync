# MediSync AI Recommendations Quality Evaluation (ISO/IEC 25010 & ISO 9001:2015)

This document describes how to evaluate the AI-driven recommendations system in MediSync against ISO/IEC 25010 quality characteristics, focusing on functional suitability, performance efficiency, and reliability. It also outlines how the system integrates into a general Quality Management System (QMS) aligned with ISO 9001:2015 and existing LGU health service protocols.

## Scope and Objectives

- Evaluate the AI recommendations pipeline (`backend/analytics/ai_insights_model.py`, `backend/analytics/predictive_analytics.py`) and the endpoint `GET /api/analytics/doctor/recommendations/`.
- Establish measurable criteria and quality gates for:
  - Functional suitability: completeness, correctness, appropriateness
  - Performance efficiency: time behavior, resource utilization, capacity
  - Reliability: availability, fault tolerance, recoverability (and overall maturity)
- Integrate evaluation and continuous improvement into the ISO 9001:2015 QMS in alignment with LGU protocols and clinical governance.

## System Under Test (SUT)

- Components:
  - Recommendations generation: `ai_insights_model.generate_insights()` with TF/RF risk prediction helpers and heuristics
  - Predictive analytics: `predictive_analytics.py` (weekly/monthly forecasts, surge predictions)
  - API: `backend/analytics/views.py` (`get_doctor_analytics_data`, `doctor_analytics`)
  - Reporting: PDF generator `backend/operations/pdf_service.py` (trend charts, insights)
  - Scheduled tasks: `backend/analytics/tasks.py` (optional Celery integration for monthly runs)
- Data:
  - `AnalyticsResult` entries for `illness_prediction`, `patient_health_trends`, `illness_surge_prediction`, `monthly_illness_forecast`, `weekly_illness_forecast`
  - Clinician rule sets and LGU protocols for treatment and triage

## Quality Gates and Acceptance Criteria

- Functional suitability
  - Correctness (recommendation accuracy vs. clinical ground truth): ≥ 85% top-1 correctness or ≥ 70% top-5 hit rate
  - Completeness (all required sections present): ≥ 98% of responses contain risk assessment, protocols, monitoring, and alerts when applicable
  - Appropriateness (alignment with LGU protocols): ≥ 95% protocol alignment as validated by rule checks and clinical review
- Performance efficiency
  - Time behavior: p95 endpoint latency ≤ 800 ms per request; p99 ≤ 1.5 s
  - Resource utilization: average CPU ≤ 60%, memory ≤ 65% under expected load
  - Capacity: sustain ≥ 50 concurrent requests with ≤ 2% error rate
- Reliability
  - Availability: ≥ 99.0% during clinic hours
  - Fault tolerance: graceful degradation with heuristics when ML models/scalers are missing
  - Recoverability: MTTR ≤ 5 minutes for common failure modes (e.g., token expiry, model reload)

## Pseudocode: Functional Suitability Evaluation

```pseudo
function evaluate_functional_suitability(test_cases, lgu_rules):
    metrics = {correct_count: 0, total: 0, complete_count: 0, appropriate_count: 0}
    for case in test_cases:
        // Prepare input reflecting patient cohort & current trends
        input_payload = build_payload(case.demographics, case.trends, case.illness_predictions)

        // Call recommendations API
        response = http_get("/api/analytics/doctor/recommendations/", input_payload)
        parsed = parse_recommendations(response)

        // Correctness: compare predicted risk/protocols to ground truth
        is_correct = compare_to_ground_truth(parsed, case.expected_outcome)

        // Completeness: verify required sections are present
        is_complete = (
            has(parsed, "risk_assessment") and
            has(parsed, "intervention_protocols") and
            has(parsed, "monitoring_guidelines") and
            (not case.requires_alerts or has(parsed, "trend_alerts"))
        )

        // Appropriateness: validate against LGU protocol rules
        // Example: risk level -> appropriate triage path -> matching intervention steps
        is_appropriate = validate_protocol_alignment(parsed, lgu_rules)

        // Aggregate metrics
        metrics.total += 1
        metrics.correct_count += 1 if is_correct else 0
        metrics.complete_count += 1 if is_complete else 0
        metrics.appropriate_count += 1 if is_appropriate else 0

    // Compute rates
    correctness_rate = metrics.correct_count / metrics.total
    completeness_rate = metrics.complete_count / metrics.total
    appropriateness_rate = metrics.appropriate_count / metrics.total

    // Gate decision based on acceptance criteria
    passed = (
        correctness_rate >= 0.85 or top5_hit_rate(test_cases) >= 0.70
    ) and completeness_rate >= 0.98 and appropriateness_rate >= 0.95

    return {correctness_rate, completeness_rate, appropriateness_rate, passed}
```

### Notes

- Ground truth may be derived from retrospective clinician-reviewed cases, protocol-driven gold standards, or simulated cases created via LGU rules.
- `validate_protocol_alignment` checks stepwise protocols (triage, diagnostics, intervention) against LGU definitions and contraindications.

## Pseudocode: Performance Efficiency Evaluation

```pseudo
function evaluate_performance_efficiency(concurrency_levels, duration_sec):
    results = []
    for c in concurrency_levels: // e.g., [1, 5, 10, 25, 50]
        load_generator = start_load_test(c, duration_sec)
        latencies = []
        errors = 0

        while load_generator.running:
            start_time = now()
            response = http_get("/api/analytics/doctor/recommendations/", sample_payload())
            end_time = now()

            if response.status == 200:
                latencies.append(end_time - start_time)
                record_resource_usage() // CPU, memory
            else:
                errors += 1

        p50 = percentile(latencies, 50)
        p95 = percentile(latencies, 95)
        p99 = percentile(latencies, 99)
        throughput = count(latencies) / duration_sec
        avg_cpu = avg_collected_metric("cpu")
        avg_mem = avg_collected_metric("mem")

        results.append({c, p50, p95, p99, throughput, avg_cpu, avg_mem, errors})

    // Evaluate against thresholds
    passed = all(
        r.p95 <= 0.8 and r.p99 <= 1.5 and r.avg_cpu <= 0.60 and r.avg_mem <= 0.65 and (r.errors / total_requests(r)) <= 0.02
        for r in results
    )

    return {results, passed}
```

### Notes

- Use realistic payloads and data distributions reflecting clinic operations.
- Instrumentation hooks can wrap `generate_insights()` to record execution time and resource counters per request.

## Pseudocode: Reliability Evaluation

```pseudo
function evaluate_reliability(test_scenarios):
    // Track availability and error rates during clinic hours
    metrics = {uptime_minutes: 0, downtime_minutes: 0, incidents: []}

    // Maturity: number of known failure modes covered by fallbacks
    // Fault tolerance: behavior under component failures
    for scenario in test_scenarios:
        apply_fault_injection(scenario) // e.g., missing ML model, scaler unfitted, token expired

        start_incident = now()
        response = http_get("/api/analytics/doctor/recommendations/", sample_payload())
        end_incident = now()

        // Assess degradation behavior
        degraded_but_operational = response.status == 200 and has_fallback_markers(response)
        failed = response.status >= 500

        if failed:
            metrics.incidents.append({scenario, start_incident, end_incident, status: "failed"})
            metrics.downtime_minutes += minutes_between(start_incident, end_incident)
        else:
            metrics.incidents.append({scenario, start_incident, end_incident, status: "operational"})
            metrics.uptime_minutes += minutes_between(start_incident, end_incident)

        // Recoverability: measure time-to-recover
        recover_start = now()
        perform_recovery_actions(scenario) // e.g., reload models, refresh token, restart worker
        recover_end = now()
        record_mttr(minutes_between(recover_start, recover_end))

    availability = metrics.uptime_minutes / (metrics.uptime_minutes + metrics.downtime_minutes)
    mttr = average_recorded_mttr()
    mtbf = estimate_mtbf(metrics.incidents)

    // Acceptance thresholds
    passed = availability >= 0.99 and mttr <= 5 and error_rate(metrics) <= 0.005

    return {availability, mttr, mtbf, incidents: metrics.incidents, passed}
```

### Notes

- Leverage built-in fallbacks in `ai_insights_model.py` (heuristic risk, safe scaling) to verify graceful degradation.
- Use synthetic fault scenarios and production-similar logs to estimate MTBF and MTTR.

## Data Collection and Instrumentation

- Add timing and resource probes around `generate_insights()` and API views to log latency and usage.
- Persist evaluation metrics in a `QualityMetric` model or separate store; include timestamp, scenario, and pass/fail.
- Maintain traceability by linking metrics to `AnalyticsResult` ids and monthly report batches.

## ISO 9001:2015 QMS Integration

- Process alignment
  - Plan: define requirements and acceptance criteria (this document) mapped to LGU protocols
  - Do: implement instrumentation and scheduled evaluation runs
  - Check: review metrics; gate releases based on quality thresholds
  - Act: corrective and preventive actions (CAPA) and continuous improvement
- Roles and responsibilities
  - Clinical Lead: validates appropriateness vs. LGU protocols; approves clinical content
  - Quality Manager: owns quality gates, audits, CAPA records
  - Data/ML Engineer: maintains models, instrumentation, and evaluation tooling
- Document control
  - Store evaluation reports, metrics dashboards, and versioned protocol mappings
  - Attach evaluation annex to monthly LGU trend reports (PDF)
- Risk-based thinking
  - Maintain risk register (e.g., model drift, data gaps); prioritize mitigations
  - Use severity × likelihood scoring to set CAPA priority

## Pseudocode: QMS Quality Gate Workflow

```pseudo
function monthly_quality_gate_run():
    fs = evaluate_functional_suitability(load_test_cases(), load_lgu_rules())
    pe = evaluate_performance_efficiency([1, 5, 10, 25, 50], duration_sec=300)
    re = evaluate_reliability(load_fault_scenarios())

    // Gate decision
    all_passed = fs.passed and pe.passed and re.passed

    if all_passed:
        publish_monthly_report_annex({fs, pe, re})
        record_qms_log("release_approved", {fs, pe, re})
    else:
        create_capa_record("quality_gate_failed", root_cause_analysis({fs, pe, re}))
        assign_actions_and_due_dates()
        schedule_re_evaluation()

    return all_passed
```

## Alignment with LGU Health Service Protocols

- Encode LGU protocols as machine-verifiable rule sets for triage, diagnostics, interventions, and follow-up.
- Validate recommendations against these rules during functional suitability checks.
- Include clinician review loops for edge cases and exceptions; document deviations.

## Reporting

- Produce a monthly evaluation annex with:
  - Functional suitability metrics (correctness, completeness, appropriateness)
  - Performance efficiency metrics (latency percentiles, resource usage, capacity)
  - Reliability metrics (availability, MTBF/MTTR, incident log)
  - Gate decision and CAPA summary
- Integrate annex into standardized LGU PDF reports via `pdf_service.py`.

## Implementation Notes and Next Steps

- Instrumentation wrappers: add timing/resource decorators in `views.py` and `ai_insights_model.py`.
- Storage: create `QualityMetric` table or lightweight log store to persist evaluation runs.
- Scheduling: add Celery Beat job for `monthly_quality_gate_run()`; archive artifacts.
- Dashboard: expose evaluation results to admin site for auditability.

## Security Scope and Next Steps

This evaluation intentionally focused on ISO/IEC 25010 characteristics requested for the AI recommendations system: functional suitability, performance efficiency, and reliability. Full security coverage (also an ISO/IEC 25010 characteristic) is handled at the platform level and across other controls. Some security measures are not listed here because:

- Scope limitation: the objective was to assess recommendation quality and operational behavior, not to exhaustively audit security.
- Existing platform controls: authentication/authorization, TLS, secret management, and audit logging are addressed elsewhere in the stack.
- Separation of concerns: security and privacy controls are documented in security architecture and compliance artifacts.

To strengthen security explicitly within this evaluation and in alignment with LGU protocols, we recommend adding a companion annex that covers ISO/IEC 25010 Security sub-characteristics (confidentiality, integrity, non-repudiation, accountability, authenticity) and references ISO 27001/27701 practices.

### Recommended Security Measures for AI Recommendations

- Access control and authorization
  - Enforce role-based access for `doctor` on `/api/analytics/doctor/recommendations/`
  - Validate JWT scopes; implement token freshness checks and rotation
- Data protection and privacy
  - Ensure encryption in transit (TLS) and at rest for analytics caches/artifacts
  - Redact PII in logs; minimize payload fields; apply purpose limitation
- Integrity and provenance
  - Verify model/scaler artifacts via checksums/signatures; log versions in responses
  - Record recommendation trace IDs linking inputs, model versions, and rules used
- Robustness and input validation
  - Validate payloads (schema, ranges); detect adversarial or anomalous inputs
  - Rate limit endpoint; apply WAF rules for known attack vectors
- Auditability and accountability
  - Structured audit logs of access, changes to clinical protocols, and model deployments
  - Periodic access reviews and anomaly detection on usage patterns

### Pseudocode: Security Checks (Companion Annex)

```pseudo
function evaluate_security_controls():
    // Access control
    assert_requires_role("doctor", "/api/analytics/doctor/recommendations/")
    assert_jwt_validity_and_scope()

    // Data protection
    assert_tls_enforced()
    assert_pii_redaction_in_logs(["name", "address", "contact"])

    // Integrity and provenance
    assert_artifact_checksum(model_path)
    assert_response_contains({"model_version", "rules_version", "trace_id"})

    // Robustness and input validation
    for payload in adversarial_payloads():
        response = http_get(endpoint, payload)
        assert response.status in [400, 422] or flagged_as_anomaly(response)

    // Rate limiting and WAF
    simulate_burst_traffic()
    assert rate_limit_applies() and waf_blocks_malicious_patterns()

    // Auditability
    assert_audit_log_entries_for_access_and_changes()

    return summary_of_checks()
```

### QMS Integration for Security

- Include security checks in the monthly quality gate alongside suitability/performance/reliability.
- Record findings in QMS logs; create CAPA for failures (e.g., missing redaction, outdated artifacts).
- Align clinician access rules and protocol updates with LGU governance and audit requirements.