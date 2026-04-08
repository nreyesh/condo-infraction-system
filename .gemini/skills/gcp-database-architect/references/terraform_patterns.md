# Terraform Patterns for GCP Databases

Use the official **`terraform-google-modules`** whenever possible for production environments.

## 1. Cloud SQL (PostgreSQL)

This pattern uses the `terraform-google-modules/sql-db/google` module.

```hcl
module "pg_db" {
  source  = "terraform-google-modules/sql-db/google//modules/postgresql"
  version = "~> 22.0"

  project_id       = var.project_id
  name             = "condo-infractions"
  region           = "southamerica-west1"
  database_version = "POSTGRES_15"
  tier             = "db-f1-micro"

  deletion_protection = true

  ip_configuration = {
    ipv4_enabled    = false # Private IP only
    private_network = var.vpc_id
    require_ssl     = true
  }

  backup_configuration = {
    enabled                        = true
    start_time                     = "04:00"
    location                       = "southamerica-west1"
    point_in_time_recovery_enabled = true
    transaction_log_retention_days = 7
    retention_unit                 = "COUNT"
    retained_backups               = 30
  }
}
```

## 2. Cloud Storage (Evidence Bucket)

Pattern for storing images/videos with IAM-based access.

```hcl
module "evidence_bucket" {
  source  = "terraform-google-modules/cloud-storage/google//modules/simple_bucket"
  version = "~> 6.0"

  name       = "condo-evidence-${var.project_id}"
  project_id = var.project_id
  location   = "SOUTHAMERICA-WEST1"

  lifecycle_rules = [
    {
      action = {
        type          = "SetStorageClass"
        storage_class = "ARCHIVE"
      }
      condition = {
        age = 730 # 2 years
      }
    },
    {
      action = {
        type = "Delete"
      }
      condition = {
        age = 1825 # 5 years
      }
    }
  ]

  iam_members = [
    {
      role   = "roles/storage.objectViewer"
      member = "serviceAccount:${var.app_service_account}"
    }
  ]
}
```

## 3. Best Practices Checklist
- [ ] Use **Private IP** only for database instances.
- [ ] Enable **Deletion Protection** in production.
- [ ] Configure **CMEK** (Customer-Managed Encryption Keys) if required by strict compliance.
- [ ] Always set a **region** explicitly (default: `southamerica-west1`).
