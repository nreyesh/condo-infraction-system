resource "google_cloud_run_v2_service" "ai_backend" {
  name     = "condo-ai-backend"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    # 1. Attach our specialized Identity
    service_account = google_service_account.app_sa.email

    containers {
      image = "us-docker.pkg.dev/cloudrun/container/hello" # Placeholder image for now

      # 2. Inject the Database Connection String (Your Variable!)
      env {
        name  = "DB_CONNECTION_NAME"
        value = google_sql_database_instance.infraction_db_instance.connection_name
      }

      # 3. Pull the Password directly from Secret Manager
      env {
        name = "DB_PASSWORD"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.db_password_secret.secret_id
            version = "latest"
          }
        }
      }

      # 4. Open the "Tunnel" (Cloud SQL Auth Proxy)
      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }
    }

    volumes {
      name = "cloudsql"
      cloud_sql_instance {
        instances = [google_sql_database_instance.infraction_db_instance.connection_name]
      }
    }
  }

  depends_on = [
    google_project_service.project_services["sqladmin.googleapis.com"],
    google_project_service.project_services["run.googleapis.com"],
    google_secret_manager_secret_iam_member.app_secret_accessor,
    google_project_iam_member.app_sql_client,
    google_project_iam_member.app_sql_instance_user
  ]
}

# Allow access to the AI Backend
resource "google_cloud_run_v2_service_iam_member" "authorized_access" {
  for_each = toset(var.authorized_emails)

  location = google_cloud_run_v2_service.ai_backend.location
  name     = google_cloud_run_v2_service.ai_backend.name
  role     = "roles/run.invoker"
  member   = each.value

  depends_on = [
    time_sleep.wait_for_iam,
  ]
}