variable "project_id" {
  type    = string
  default = "condo-infraction-system-492221" 
}

variable "region" {
  type    = string
  default = "southamerica-west1"
}

variable "state_bucket_name" {
  type    = string
  default = "condo-infraction-system-tf-state"
}

variable "authorized_emails" {
  type    = list(string)
  default = ["user:nereyes@miuandes.cl", 
        "user:nico.uk.cl@gmail.com", 
        "user:infraction.system@gmail.com"]
  description = "List of users allowed to access the Cloud Run service"
}