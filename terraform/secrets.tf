# Secret Container
resource "google_secret_manager_secret" "db_password_secret" {
  secret_id = "db-password" # The name you'll see in the console

  replication {
    auto {} # Let Google handle backing this up across regions
  }

  depends_on = [google_project_service.secretmanager]
}

# password previosly created
resource "google_secret_manager_secret_version" "db_password_version" {
  secret      = google_secret_manager_secret.db_password_secret.id
  secret_data = random_password.db_password.result # Points to our generator in database.tf
}