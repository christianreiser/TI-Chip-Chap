resource "google_secret_manager_secret" "openai_api_key" {
  secret_id = "openai_api_key"
  replication {
    automatic = true
  }
  depends_on = [google_project_service.secretmanager]
}


resource "google_secret_manager_secret_iam_member" "openai_api_key_access" {
  secret_id = google_secret_manager_secret.openai_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.chatbot-service.email}"
}