resource "google_storage_bucket" "evidence_bucket" {
  name          = "${var.project_id}-evidence"
  location      = var.region
  force_destroy = true 
  public_access_prevention = "enforced"
}

# Create the Service Account
resource "google_service_account" "terraform_cicd" {
  account_id   = "terraform-cicd"
  display_name = "Terraform CI/CD Service Account"
}

# Give it "Editor" permissions so it can build things
resource "google_project_iam_member" "terraform_editor" {
  project = var.project_id
  role    = "roles/editor"
  member  = "serviceAccount:${google_service_account.terraform_cicd.email}"
}

# Give it access to the State Bucket specifically
resource "google_storage_bucket_iam_member" "state_admin" {
  bucket = var.state_bucket_name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.terraform_cicd.email}"
}

## --------- GitHub Actions --------- ##
# Create a Workload Identity Pool (The "Meeting Room")
resource "google_iam_workload_identity_pool" "github_pool" {
  workload_identity_pool_id = "github-pool"
  display_name              = "GitHub Pool"
}

# Create a Provider (The "Receptionist" who checks GitHub's ID)
resource "google_iam_workload_identity_pool_provider" "github_provider" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github_pool.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-provider"
  
  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.repository" = "assertion.repository"
  }

  attribute_condition = "assertion.repository == 'nreyesh/condo-infraction-system'"

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

# Allow your GitHub Repo to "Impersonate" the Service Account
resource "google_service_account_iam_member" "github_sa_user" {
  service_account_id = google_service_account.terraform_cicd.name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github_pool.name}/attribute.repository/nreyesh/condo-infraction-system"
}


## --------- Cloud SQL --------- ##
# Generate a random password (so you don't have to invent one)
resource "random_password" "db_password" {
  length  = 16
  special = false
}

# The Cloud SQL Instance (The "Server")
resource "google_sql_database_instance" "infraction_db_instance" {
  name             = "condo-db-instance"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = "db-f1-micro" # Smallest tier to keep costs low
    
    ip_configuration {
      ipv4_enabled = true # Allows connection for local testing
    }
  }

  deletion_protection = false # Set to true for production!
}

# The actual Database (The "Folder" inside the server)
resource "google_sql_database" "infraction_db" {
  name     = "infractions"
  instance = google_sql_database_instance.infraction_db_instance.name
}

# The Database User
resource "google_sql_user" "db_user" {
  name     = "ai_backend_user"
  instance = google_sql_database_instance.infraction_db_instance.name
  password = random_password.db_password.result
}