# Cloud Logging Sink to collect CONNECT and DISCONNECT events
# and send them to a Pub/Sub Topic.
# Docs: https://medium.com/rockedscience/tracking-device-connections-in-google-cloud-iot-core-3263ffc38459
# Docs: https://cloud.google.com/logging/docs/export/configure_export_v2
resource "google_logging_project_sink" "smart_plug_connection_sink_pubsub" {
  name                   = "smart-plug-connections-sink-pubsub"
  description            = "Collects CONNECT and DISCONNECT events and sends them to Pub/Sub."
  destination            = "pubsub.googleapis.com/projects/${var.google_cloud_project_id}/topics/${google_pubsub_topic.smart_plug_connections.name}"
  filter                 = "resource.type=\"cloudiot_device\" AND jsonPayload.eventType=(\"CONNECT\" OR \"DISCONNECT\")"
  unique_writer_identity = true

  depends_on = [google_pubsub_topic.smart_plug_connections]
}

# Set the IAM permissions to enable the Log Sink to publish to a Pub/Sub Topic.
resource "google_project_iam_member" "smart_plug_connection_sink_pubsub_writer" {
  project = var.google_cloud_project_id
  role    = "roles/pubsub.publisher"
  member  = google_logging_project_sink.smart_plug_connection_sink_pubsub.writer_identity
}
