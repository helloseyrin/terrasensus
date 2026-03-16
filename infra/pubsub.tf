resource "google_pubsub_topic" "sensor_readings" {
  name = "terrasensus-sensor-readings"
}

resource "google_pubsub_subscription" "ingestion" {
  name  = "terrasensus-ingestion-sub"
  topic = google_pubsub_topic.sensor_readings.name

  push_config {
    push_endpoint = "${google_cloud_run_v2_service.ingestion.uri}/pubsub/push"
  }

  ack_deadline_seconds = 30
}
