resource "google_storage_bucket" "index-file" {
  name     = "${var.project_id}-index-file"
  location = "EU"

  uniform_bucket_level_access = true
}

resource "google_storage_bucket_iam_member" "bucket_iam_member_legacy" {
  bucket = google_storage_bucket.index-file.name
  role   = "roles/storage.legacyBucketReader"
  member = "serviceAccount:${google_service_account.chatbot-service.email}"
}

resource "google_storage_bucket_iam_member" "bucket_iam_member" {
  bucket = google_storage_bucket.index-file.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.chatbot-service.email}"
}
