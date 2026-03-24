terraform {
  required_version = ">= 1.0"

  # This is the "Shared Memory" link
  backend "gcs" {
    bucket  = "condo-tf-state"
    prefix  = "terraform/state"
  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}