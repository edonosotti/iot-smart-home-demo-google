variable google_cloud_project_id {
  type        = string
  description = "The Google Cloud Project ID."
}

variable google_cloud_region {
  type        = string
  description = "The Google Cloud region to provision resources into."
}

variable google_cloud_zone {
  type        = string
  description = "The Google Cloud zone to provision resources into."
}

# Docs: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloudiot_device#log_level
variable iot_core_log_level {
  type        = string
  default     = "INFO"
  description = "The default log level for the Device Registry and IoT Devices."
}

variable google_iot_ca_roots_url {
  type        = string
  default     = "https://pki.google.com/roots.pem"
  description = "URL to the Google's CA roots file for Cloud IoT Core."
}
