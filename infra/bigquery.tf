resource "google_bigquery_dataset" "terrasensus" {
  dataset_id    = "terrasensus_${var.environment}"
  friendly_name = "TerraSensus ${var.environment}"
  description   = "Analytics dataset — populated via GCP Datastream from Cloud SQL"
  location      = var.region

  labels = {
    environment = var.environment
    project     = "terrasensus"
  }
}

# Raw tables populated by Datastream (schema mirrors Cloud SQL)
resource "google_bigquery_table" "sensor_readings_raw" {
  dataset_id          = google_bigquery_dataset.terrasensus.dataset_id
  table_id            = "sensor_readings"
  deletion_protection = false

  schema = jsonencode([
    { name = "id",          type = "STRING",    mode = "REQUIRED" },
    { name = "plot_id",     type = "STRING",    mode = "REQUIRED" },
    { name = "created_at",  type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "moisture",    type = "FLOAT64",   mode = "NULLABLE" },
    { name = "temperature", type = "FLOAT64",   mode = "NULLABLE" },
    { name = "ph",          type = "FLOAT64",   mode = "NULLABLE" },
    { name = "nitrogen",    type = "FLOAT64",   mode = "NULLABLE" },
    { name = "phosphorus",  type = "FLOAT64",   mode = "NULLABLE" },
    { name = "potassium",   type = "FLOAT64",   mode = "NULLABLE" },
    { name = "ec",          type = "FLOAT64",   mode = "NULLABLE" }
  ])

  time_partitioning {
    type  = "DAY"
    field = "created_at"
  }
}
