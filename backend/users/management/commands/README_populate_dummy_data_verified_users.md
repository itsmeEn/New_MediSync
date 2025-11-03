# populate_dummy_data_verified_users

Retrieve verified doctors and nurses that belong to a specified hospital and output them as a structured JSON array. Intended for generating dummy datasets or validating hospital-scoped user availability.

## Required Permissions
- Application must have access to the main database (read-only sufficient).
- Run in a Django environment where `DJANGO_SETTINGS_MODULE` is configured.
- Command is not restricted to a specific app role, but operational usage should be limited to trusted environments (e.g., developers, administrators).

## Input Parameters
- `--hospital <string>`: Hospital name to filter users (case-insensitive exact match).
- `--user-id <int>`: Derive hospital context from the given User ID if `--hospital` is not provided.
- `--user-email <string>`: Derive hospital context from the given User email if `--hospital` is not provided.
- `--output <path>`: Optional file path to write JSON output. If omitted, outputs to stdout.

At least one of `--hospital`, `--user-id`, or `--user-email` must be provided. If a user is used for derivation and that user has no `hospital_name` set, the command will error with a helpful message.

## Output Format
JSON array of user objects with fields:

```json
[
  {
    "id": 123,
    "full_name": "Dr. Jane Smith",
    "email": "jane.smith@example.com",
    "verification_status": "approved",
    "hospital_name": "General Hospital",
    "hospital_address": "123 Main St, City"
  }
]
```

Notes:
- Only includes users with roles `doctor` or `nurse`.
- Filters: `is_active = True`, `is_verified = True`, `verification_status = 'approved'`, `hospital_name` equals the provided context.
- Sorted by `full_name`.

## Error Handling
- Database connection issues: Reports an error and exits (OperationalError/DatabaseError).
- Missing hospital context: Clear error message if `--hospital` cannot be resolved via `--user-id`/`--user-email`.
- Empty result set: Returns `[]`, logs a warning, and prints a notice to stderr.
- File write failure (when `--output` is provided): Reports the OS error and exits.

## Logging
- Logs start, parameters, counts, and empty-result conditions to the Django logger.
- Emits notices and warnings to the console (stdout/stderr) for visibility.

## Usage Examples

Print verified users for a hospital to stdout:

```
python manage.py populate_dummy_data_verified_users --hospital "General Hospital"
```

Derive hospital from a known user and write output to a file:

```
python manage.py populate_dummy_data_verified_users --user-id 42 --output verified_users.json
```

Derive hospital from an email (case-sensitive match):

```
python manage.py populate_dummy_data_verified_users --user-email nurse.alex@example.com
```

## Notes
- This command mirrors the filtering logic used by secure messaging availability (`role in ['doctor','nurse']`, verified, same `hospital_name`).
- If your deployment relies on both `hospital_name` and `hospital_address` for tighter scoping, consider extending the command to include an optional `--hospital-address` match.