# IoT Core Device Registry for the Smart Plugs
# Docs: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloudiot_registry
resource "google_cloudiot_registry" "smart_plug" {
  name     = "smart-plug"

  # Default Pub/Sub Topic for the device telemetry
  event_notification_configs {
    pubsub_topic_name = google_pubsub_topic.smart_plug_default_telemetry.id
    subfolder_matches = ""
  }

  # Default Pub/Sub Topic for the device state
  state_notification_config = {
    pubsub_topic_name = google_pubsub_topic.smart_plug_default_state.id
  }

  mqtt_config = {
    mqtt_enabled_state = "MQTT_ENABLED"
  }

  http_config = {
    http_enabled_state = "HTTP_ENABLED"
  }

  log_level = var.iot_core_log_level

  credentials {
    public_key_certificate = {
      format      = "X509_CERTIFICATE_PEM"
      certificate = tls_self_signed_cert.device_registry_certificate.cert_pem
    }
  }

  depends_on = [
    google_pubsub_topic.smart_plug_default_state,
    google_pubsub_topic.smart_plug_default_telemetry,
    tls_self_signed_cert.device_registry_certificate
  ]
}

# Virtual Smart Plug device
# Docs: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloudiot_device
resource "google_cloudiot_device" "virtual_smart_plug_0001" {
  name     = "VSP-0001"
  registry = google_cloudiot_registry.smart_plug.id

  credentials {
    public_key {
        format = "RSA_X509_PEM"
        key    = tls_locally_signed_cert.virtual_device_certificate.cert_pem
    }
  }

  blocked = false

  log_level = var.iot_core_log_level

  metadata = {
    type = "virtual"
  }

  gateway_config {
    gateway_type = "NON_GATEWAY"
  }

  depends_on = [tls_locally_signed_cert.virtual_device_certificate]
}
