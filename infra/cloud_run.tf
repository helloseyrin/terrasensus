locals {
  services = ["ingestion", "alert-engine", "ai-recommendations", "lab-parser"]
}

resource "google_cloud_run_v2_service" "ingestion" {
  name     = "terrasensus-ingestion-${var.environment}"
  location = var.region

  template {
    containers {
      image = "gcr.io/${var.project_id}/terrasensus-ingestion:latest"

      env {
        name  = "ENV"
        value = var.environment
      }
      env {
        name = "DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = "terrasensus-db-url"
            version = "latest"
          }
        }
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }
  }
}

resource "google_cloud_run_v2_service" "alert_engine" {
  name     = "terrasensus-alert-engine-${var.environment}"
  location = var.region

  template {
    containers {
      image = "gcr.io/${var.project_id}/terrasensus-alert-engine:latest"
      env {
        name  = "ENV"
        value = var.environment
      }
    }
    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }
  }
}

resource "google_cloud_run_v2_service" "ai_recommendations" {
  name     = "terrasensus-ai-recommendations-${var.environment}"
  location = var.region

  template {
    containers {
      image = "gcr.io/${var.project_id}/terrasensus-ai-recommendations:latest"
      env {
        name  = "ENV"
        value = var.environment
      }
      env {
        name  = "VERTEX_AI_LOCATION"
        value = var.region
      }
    }
    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }
  }
}

resource "google_cloud_run_v2_service" "lab_parser" {
  name     = "terrasensus-lab-parser-${var.environment}"
  location = var.region

  template {
    containers {
      image = "gcr.io/${var.project_id}/terrasensus-lab-parser:latest"
      env {
        name  = "ENV"
        value = var.environment
      }
      env {
        name  = "GCS_BUCKET"
        value = google_storage_bucket.lab_reports.name
      }
    }
    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }
  }
}
