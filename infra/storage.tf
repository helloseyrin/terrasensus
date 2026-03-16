resource "google_storage_bucket" "lab_reports" {
  name                        = "terrasensus-lab-reports-${var.environment}"
  location                    = var.region
  force_destroy               = false
  uniform_bucket_level_access = true

  lifecycle_rule {
    condition { age = 365 }
    action { type = "SetStorageClass"; storage_class = "NEARLINE" }
  }
}
