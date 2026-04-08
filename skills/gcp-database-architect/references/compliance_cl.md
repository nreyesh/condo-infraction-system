# Chilean Law No. 19.628: Personal Data Protection

This guide provides architectural patterns for complying with Chilean data laws (specifically the "Right to be Forgotten" and "Purpose Limitation") on GCP.

## 1. The Right to be Forgotten (Derecho al Olvido)

When a resident exercises their right to be forgotten, the following **Active Anonymization** pattern is recommended over pure hard-deletion to maintain historical reporting integrity.

### Active Anonymization Pattern

For the `Resident` and `Staff` models, when `is_active = False`, anonymize the following PII (Personally Identifiable Information):

| Model | PII Field | Anonymization Strategy |
| :--- | :--- | :--- |
| `Resident` | `first_name` | Mask (e.g., `Resident-XXX`) |
| `Resident` | `last_name` | Mask (e.g., `XXX`) |
| `Resident` | `email` | Redact (e.g., `anon-123@deleted.cl`) |
| `Resident` | `phone` | Redact (e.g., `+56-9-XXXX-XXXX`) |
| `Staff` | `full_name` | Mask (e.g., `Staff Member-XXX`) |

### Example SQL for PostgreSQL (Cloud SQL)

```sql
-- Create a function to anonymize a resident
CREATE OR REPLACE FUNCTION anonymize_resident(res_id UUID) RETURNS void AS $$
BEGIN
    UPDATE residents
    SET first_name = 'Resident',
        last_name = SUBSTRING(resident_id::text, 1, 8),
        email = CONCAT('anon-', SUBSTRING(resident_id::text, 1, 8), '@condo.internal'),
        phone = NULL,
        is_active = FALSE,
        updated_at = NOW()
    WHERE resident_id = res_id;
END;
$$ LANGUAGE plpgsql;
```

## 2. Data Residency (Principle of Territory)

Default to the **`southamerica-west1`** (Santiago) region for all database resources to ensure data remains within Chilean borders and minimizes latency for local users.

## 3. Data Retention and Archiving (TTL)

Automate the "Right to be Forgotten" using **Google Cloud Storage (GCS)** for evidence (images/videos):

- **Hot Storage:** Keep images for current infractions in Standard storage (GCS).
- **Archiving Policy:** After 2 years, move images to **Archive Storage** (for audit purposes only).
- **Deletion Policy:** After 5 years (or per legal statute of limitations for civil liabilities), permanently delete images using GCS Object Lifecycle Management.

### Terraform snippet for GCS Lifecycle:
```hcl
resource "google_storage_bucket" "evidence_bucket" {
  name     = "condo-evidence-${var.project_id}"
  location = "SOUTHAMERICA-WEST1"

  lifecycle_rule {
    condition {
      age = 730 # 2 years
    }
    action {
      type          = "SetStorageClass"
      storage_class = "ARCHIVE"
    }
  }

  lifecycle_rule {
    condition {
      age = 1825 # 5 years
    }
    action {
      type = "Delete"
    }
  }
}
```
