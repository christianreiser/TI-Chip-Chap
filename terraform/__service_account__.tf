# cloud run service account: chatbot-service
resource "google_service_account" "chatbot-service" {
  account_id = "chatbot-service"
}

resource "google_project_iam_member" "chatbot_service_bq_viewer" {
  project = "chatbot-420"
  role    = "roles/bigquery.dataViewer"
  member  = "serviceAccount:${google_service_account.chatbot-service.email}"
}

resource "google_project_iam_member" "chatbot_service_bq_viewer" {
  project = "chatbot-420"
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.chatbot-service.email}"
}
