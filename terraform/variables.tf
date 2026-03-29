variable "project_id" {
  type    = string
  default = "condo-infraction-system" # Ensure this matches your GCP Project ID
}

variable "region" {
  type    = string
  default = "us-central1"
}

variable "state_bucket_name" {
  type    = string
  default = "condo-tf-state" # The one that actually exists
}

variable "authorized_emails" {
  type    = list(string)
  default = ["user:nereyes@miuandes.cl", "user:nico.uk.cl@gmail.com"]
  description = "List of users allowed to access the Cloud Run service"
}