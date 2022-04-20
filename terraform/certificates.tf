locals {
  device_registry_private_key_path = "${path.module}/../certificates/registry-private.key"
  device_registry_certificate_path = "${path.module}/../certificates/registry-public.pem"
  virtual_device_private_key_path  = "${path.module}/../certificates/device-private.key"
  virtual_device_certificate_path  = "${path.module}/../certificates/device-public.pem"
  google_ca_roots_path             = "${path.module}/../certificates/roots.pem"
}

# ==================================================
# DEVICE REGISTRY
# ==================================================

# Create a RSA key of size 2048 bits for the Device Registry
# Docs: https://registry.terraform.io/providers/hashicorp/tls/latest/docs/resources/private_key
resource "tls_private_key" "device_registry_private_key" {
  algorithm = "RSA"
  rsa_bits  = 2048
}

# Write the Device Registry's private key to a local file
# Docs: https://registry.terraform.io/providers/hashicorp/local/latest/docs/resources/file
resource "local_file" "device_registry_private_key" {
  content  = tls_private_key.device_registry_private_key.private_key_pem
  filename = local.device_registry_private_key_path
}

# Create a self-signed certificate for the Device Registry
# from the private key
# Docs: https://registry.terraform.io/providers/hashicorp/tls/latest/docs/resources/self_signed_cert
resource "tls_self_signed_cert" "device_registry_certificate" {
  private_key_pem   = tls_private_key.device_registry_private_key.private_key_pem
  is_ca_certificate = true

  subject {
    common_name     = "Virtual Smart Plug Registry"
    organization    = "Google Smart Home IoT Tutorial"
  }

  validity_period_hours = (24 * 365) # 1 yr

  # Docs: https://datatracker.ietf.org/doc/html/rfc5280#section-4.2.1.3
  # and:  https://datatracker.ietf.org/doc/html/rfc5280#section-4.2.1.12
  allowed_uses      = [
    "cert_signing",
    "key_encipherment",
    "digital_signature",
    "server_auth",
  ]
}

# Write the Device Registry's certificate to a local file
# Docs: https://registry.terraform.io/providers/hashicorp/local/latest/docs/resources/file
resource "local_file" "device_registry_certificate" {
  content  = tls_self_signed_cert.device_registry_certificate.cert_pem
  filename = local.device_registry_certificate_path
}

# ==================================================
# VIRTUAL DEVICE
# ==================================================

# Create a RSA key of size 2048 bits for the virtual device
# Docs: https://registry.terraform.io/providers/hashicorp/tls/latest/docs/resources/private_key
resource "tls_private_key" "virtual_device_private_key" {
  algorithm = "RSA"
  rsa_bits  = 2048
}

# Write the virtual device's private key to a local file
# Docs: https://registry.terraform.io/providers/hashicorp/local/latest/docs/resources/file
resource "local_file" "virtual_device_private_key" {
  content  = tls_private_key.virtual_device_private_key.private_key_pem
  filename = local.virtual_device_private_key_path
}

# Create a Certificate Signing Request for the virtual device
# Docs: https://registry.terraform.io/providers/hashicorp/tls/latest/docs/resources/cert_request
resource "tls_cert_request" "virtual_device_certificate" {
  private_key_pem   = tls_private_key.virtual_device_private_key.private_key_pem

  subject {
    common_name     = "Virtual Smart Plug - VSP-0001"
    organization    = "Google Smart Home IoT Tutorial"
  }
}

# Create a self-signed certificate for the virtual device
# Docs: https://registry.terraform.io/providers/hashicorp/tls/latest/docs/resources/locally_signed_cert
resource "tls_locally_signed_cert" "virtual_device_certificate" {
  cert_request_pem   = tls_cert_request.virtual_device_certificate.cert_request_pem
  ca_private_key_pem = tls_private_key.device_registry_private_key.private_key_pem
  ca_cert_pem        = tls_self_signed_cert.device_registry_certificate.cert_pem

  validity_period_hours = (24 * 365) # 1 yr

  # Docs: https://datatracker.ietf.org/doc/html/rfc5280#section-4.2.1.3
  # and:  https://datatracker.ietf.org/doc/html/rfc5280#section-4.2.1.12
  allowed_uses      = [
    "key_encipherment",
    "digital_signature",
    "server_auth",
  ]
}

# Write the virtual device certificate to a local file
# Docs: https://registry.terraform.io/providers/hashicorp/local/latest/docs/resources/file
resource "local_file" "virtual_device_certificate" {
  content  = tls_locally_signed_cert.virtual_device_certificate.cert_pem
  filename = local.virtual_device_certificate_path
}

# URL to the Google's CA roots file for Cloud IoT Core
data "http" "google_iot_ca_roots" {
  url = var.google_iot_ca_roots_url
}

# Write the Google's CA roots file for Cloud IoT Core to a local file
# Docs: https://registry.terraform.io/providers/hashicorp/local/latest/docs/resources/file
resource "local_file" "google_ca_roots_certificates" {
  content  = data.http.google_iot_ca_roots.body
  filename = local.google_ca_roots_path
}
