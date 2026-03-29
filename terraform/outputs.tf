output "db_connection_name" {
  value       = google_sql_database_instance.infraction_db_instance.connection_name
  description = "The connection string for the database"
}