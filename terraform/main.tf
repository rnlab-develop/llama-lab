module "sql-db" {
  source          = "GoogleCloudPlatform/sql-db/google//modules/postgresql"
  version         = "16.1.0"
  project_id      = var.project_id
  zone            = var.zone
  name            = var.name
  database_version = var.database_version
}