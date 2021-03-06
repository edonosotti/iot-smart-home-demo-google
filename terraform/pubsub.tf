# Default Pub/Sub Topic for the IoT devices' state
# Docs: https://cloud.google.com/iot/docs/how-tos/config/getting-state#reporting_device_state
resource "google_pubsub_topic" "smart_plug_default_state" {
  name = "smart-plug-default-state"
}

# Default Pub/Sub Topic for the IoT devices' telemetry
# Docs: https://cloud.google.com/iot/docs/how-tos/mqtt-bridge#publishing_telemetry_events
resource "google_pubsub_topic" "smart_plug_default_telemetry" {
  name = "smart-plug-default-telemetry"
}

# Pub/Sub Topic to receive CONNECT and DISCONNECT events from a Log Sink
# Docs: https://medium.com/rockedscience/tracking-device-connections-in-google-cloud-iot-core-3263ffc38459
# Docs: https://cloud.google.com/logging/docs/export/configure_export_v2
resource "google_pubsub_topic" "smart_plug_connections" {
  name = "smart-plug-connections"
}
