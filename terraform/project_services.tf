
# Cloud Resource Manager API
resource "google_project_service" "cloudresourcemanager" {
  project            = var.project_id
  service            = "cloudresourcemanager.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "cloudbuild" {
  project            = var.project_id
  service            = "cloudbuild.googleapis.com"
  disable_on_destroy = false
  depends_on = [
    google_project_service.cloudresourcemanager,
  ]
}

resource "google_project_service" "iam" {
  project            = var.project_id
  service            = "iam.googleapis.com"
  disable_on_destroy = false
  depends_on = [
    google_project_service.cloudresourcemanager,
  ]
}

resource "google_project_service" "cloudrun" {
  project            = var.project_id
  service            = "run.googleapis.com"
  disable_on_destroy = false
  depends_on = [
    google_project_service.cloudresourcemanager,
  ]
}

resource "google_project_service" "secretmanager" {
  project            = var.project_id
  service            = "secretmanager.googleapis.com"
  disable_on_destroy = false
  depends_on = [
    google_project_service.cloudresourcemanager,
  ]
}

resource "google_project_service" "artifactregistry" {
  project            = var.project_id
  service            = "artifactregistry.googleapis.com"
  disable_on_destroy = false
  depends_on = [
    google_project_service.cloudresourcemanager,
  ]
}

