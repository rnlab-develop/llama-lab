module "sql-db_postgresql" {
    source  = "GoogleCloudPlatform/sql-db/google//modules/postgresql"
    version = "16.1.0"
    name = "vdb"
    project_id = "sandbox-378304"
    zone = "us-central1-c"
    database_version = "POSTGRES_14"
}