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