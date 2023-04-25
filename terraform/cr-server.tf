resource "google_cloud_run_service" "chatbot" {
  name     = "chatbot"
  location = "europe-west1"

  template {

    spec {
      service_account_name = google_service_account.chatbot-service.email
      containers {
#        image = "gcr.io/${var.project_id}/chatbot"
#        europe-west1-docker.pkg.dev/${PROJECT_ID}/artifact-repository/chatbot-service
        image = "europe-west1-docker.pkg.dev/${var.project_id}/artifact-repository/chatbot-service:latest"
        env {
          name  = "openai_api_key"
          value_from {
            secret_key_ref {
              key  = "latest"
              name = "openai_api_key"
            }
          }
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

}

resource "google_cloud_run_service_iam_member" "chatbot_public" {
  service = google_cloud_run_service.chatbot.name
  location = "europe-west1"
  role     = "roles/run.invoker"
  member   = "allUsers"
}

