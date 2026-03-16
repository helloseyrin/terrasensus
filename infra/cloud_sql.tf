resource "google_sql_database_instance" "main" {
  name             = "terrasensus-${var.environment}"
  database_version = "POSTGRES_16"
  region           = var.region

  settings {
    tier = "db-f1-micro"   # upgrade for production

    backup_configuration {
      enabled = true
    }

    ip_configuration {
      ipv4_enabled = false
      private_network = google_compute_network.vpc.id
    }
  }

  deletion_protection = true
}

resource "google_sql_database" "terrasensus" {
  name     = "terrasensus"
  instance = google_sql_database_instance.main.name
}
