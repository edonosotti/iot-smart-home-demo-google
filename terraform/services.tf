# Enable the required services
# Docs: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/google_project_service
resource "google_project_service" "services" {
  for_each = toset([
#    "artifactregistry.googleapis.com",
#    "bigquery.googleapis.com",
#    "bigquerydatatransfer.googleapis.com",
#    "bigquerymigration.googleapis.com",
#    "bigquerystorage.googleapis.com",
    "cloudapis.googleapis.com",
    "cloudbuild.googleapis.com",
    "clouddebugger.googleapis.com",
    "cloudfunctions.googleapis.com",
    "cloudiot.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "cloudtrace.googleapis.com",
#    "containerregistry.googleapis.com",
#    "datastore.googleapis.com",
    "eventarc.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
    "pubsub.googleapis.com",
#    "run.googleapis.com",
    "servicemanagement.googleapis.com",
    "serviceusage.googleapis.com",
#    "source.googleapis.com",
#    "sql-component.googleapis.com",
#    "storage-api.googleapis.com",
#    "storage-component.googleapis.com",
#    "storage.googleapis.com",
  ])

  project                    = var.google_cloud_project_id
  service                    = each.key
  disable_dependent_services = false
  disable_on_destroy         = false

  depends_on = [data.google_project.project]
}
