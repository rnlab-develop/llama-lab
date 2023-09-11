variable "project_id" {
  description = "The GCP project to deploy to"
  type        = string
  default     = "sandbox-378304"
}

variable "name" {
  description = "The name of the Cloud SQL instance"
  type        = string
  default     = "vdb"
}

variable "zone" {
  description = "The region to deploy to"
  type        = string
  default     = "us-central1-c"
}


variable "database_version" {
  description = "The database version to use"
  type        = string
  default     = "POSTGRES_14"
}