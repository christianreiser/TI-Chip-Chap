# cloud run service account: chatbot-service
resource "google_service_account" "chatbot-service" {
  account_id = "chatbot-service"
}