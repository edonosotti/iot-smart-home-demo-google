# Set up the Terraform provider
# Docs: https://registry.terraform.io/providers/hashicorp/google/latest/docs/guides/provider_reference
provider "google" {
  project               = var.google_cloud_project_id
  region                = var.google_cloud_region
  zone                  = var.google_cloud_zone
  # Note: https://registry.terraform.io/providers/hashicorp/google/latest/docs/guides/provider_reference#user_project_override
  user_project_override = true
}

#provider "google-beta" {
#  project               = var.gcp_project
#  region                = var.gcp_region
#  zone                  = var.gcp_zone
#
#  # Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/guides/provider_reference#user_project_override
#  user_project_override = true
#}
