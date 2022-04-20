# Data source for the Google Cloud project
# Docs: https://registry.terraform.io/providers/hashicorp/google/latest/docs/data-sources/project
data "google_project" "project" {
  project_id = var.google_cloud_project_id
}
