# Create the App Service Account
resource "google_service_account" "app_sa" {
  account_id   = "condo-app-sa"
  display_name = "Service Account for the AI Infraction App"
}

# Give the App SA permission to READ the secret we made earlier
resource "google_secret_manager_secret_iam_member" "app_secret_accessor" {
  secret_id = google_secret_manager_secret.db_password_secret.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.app_sa.email}"
}

# Give the App SA permission to connect to Cloud SQL
resource "google_project_iam_member" "app_sql_client" {
  project = "condo-infraction-system"
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.app_sa.email}"
}

# Allow the App SA to use the Cloud SQL Instance
resource "google_project_iam_member" "app_sql_instance_user" {
  project = var.project_id
  role    = "roles/cloudsql.instanceUser" # Specifically for IAM-based login/proxy
  member  = "serviceAccount:${google_service_account.app_sa.email}"
}