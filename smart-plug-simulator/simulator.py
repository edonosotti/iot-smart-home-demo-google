#!/usr/bin/env python

# ==================================================
# GOOGLE CLOUD IOT CORE - CONNECTED DEVICE SIMULATOR
# ==================================================
# Simulates a IoT smart plug device.
#
# Based on Google's official Python sample:
# https://github.com/GoogleCloudPlatform/python-docs-samples/blob/main/iot/api-client/mqtt_example/cloudiot_mqtt_example.py
#
#
# Supported commands:
# * {"time": "echo"}
#
# ATTRIBUTION, CHANGELOG, ORIGINAL COPYRIGHT NOTICE
# AND LICENSE (included in compliance of the
# Apache 2.0 license of the original source code):
#
# Major changes:
# * Added parsing of inbound messages
# * Added processing of basic command messages
# * Added processing of config messages
# * Added management of device state
# * Added re-subscription to topics on reconnect
# * Modified the "device demo" code
# * Removed the "gateway" code
#
# Original copyright notice:
# Copyright 2017 Google Inc.
#
# Original license:
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""A virtual IoT device that connects to Google Cloud IoT Core via MQTT.
This example connects to Google Cloud IoT Core via MQTT, using a JWT for
device authentication. The device simulates a connected plug that can
be remotely switched on and off. The plug sends the current power (W)
reading to the Cloud every 5 seconds. Upon request, the device will also
send its current timestamp back to the Cloud.
"""

import argparse
import datetime
from operator import truediv
import os
import random
import ssl
import time
import json

import jwt
import paho.mqtt.client as mqtt
from termcolor import colored

# --------------------------------------------------
# GLOBALS
# --------------------------------------------------
# The initial backoff time after a disconnection occurs, in seconds.
MIN_BACKOFF_TIME = 1

# The maximum backoff time before giving up, in seconds.
MAX_BACKOFF_TIME = 60 * 60 * 24

# Whether to wait with exponential backoff before publishing.
SHOULD_BACKOFF = False

# MQTT topic for inbound Config messages
MQTT_CONFIG_TOPIC = None

# MQTT topic for inbound Command messages
MQTT_COMMAND_TOPIC = None

# MQTT topic for outbound State messages
MQTT_STATE_TOPIC = None

# MQTT topic for outbound Event messages
MQTT_EVENTS_TOPIC = None

# Config: Switch state
SWITCH_FIELD = "switch"
SWITCH_STATE_ON = "on"
SWITCH_STATE_OFF = "off"
SWITCH_STATE_CURRENT = SWITCH_STATE_OFF

# Command: time
TIME_FIELD = "time"
TIME_CMD_ECHO = "echo"

# Device state
CURRENT_STATE = {
  SWITCH_FIELD: SWITCH_STATE_OFF
}

# --------------------------------------------------
# VALIDATORS
# --------------------------------------------------
def validate_config(parsed_payload):
  """Validate an inbound CONFIG payload content"""
  global SWITCH_FIELD
  global SWITCH_STATE_ON
  global SWITCH_STATE_OFF
  if parsed_payload != None \
    and SWITCH_FIELD in parsed_payload \
    and parsed_payload[SWITCH_FIELD] \
      in [SWITCH_STATE_ON, SWITCH_STATE_OFF]:
        return True
  else:
    print(colored("Invalid inbound CONFIG content", "red"))
    return False

def validate_command(parsed_payload):
  """Validate an inbound COMMAND payload content"""
  global TIME_FIELD
  global TIME_CMD_ECHO
  if parsed_payload != None \
    and TIME_FIELD in parsed_payload \
    and parsed_payload[TIME_FIELD] \
      in [TIME_CMD_ECHO]:
        return True
  else:
    print(colored("Invalid inbound COMMAND content", "red"))
    return False

# --------------------------------------------------
# MESSAGE PARSER
# --------------------------------------------------
def parse_message(payload):
  """Parse an inbound message's payload as JSON"""
  try:
    return json.loads(payload)
  except:
    print(colored("Invalid inbound message format", "red"))
    pass

# --------------------------------------------------
# CONFIGURATION MANAGAMENT
# --------------------------------------------------
def apply_config(client, parsed_payload):
  """Applies a device configuration received from the Cloud"""
  global SWITCH_FIELD
  if SWITCH_FIELD in parsed_payload:
    change_switch_state(parsed_payload[SWITCH_FIELD])
  send_state(client)

def change_switch_state(new_state):
  """Change the switch state"""
  global CURRENT_STATE
  global SWITCH_FIELD
  global SWITCH_STATE_ON
  CURRENT_STATE[SWITCH_FIELD] = new_state
  print(
      colored(
        "Changed the switch status to:",
        "white"
      ),
      colored(
        new_state,
        ("green" if new_state == SWITCH_STATE_ON else "red")
      )
    )

# --------------------------------------------------
# COMMAND PROCESSORS
# --------------------------------------------------
def dispatch_command(client, parsed_payload):
  """Dispatch a valid message to its processor function"""
  global TIME_FIELD
  global TIME_CMD_ECHO
  if TIME_FIELD in parsed_payload \
    and parsed_payload[TIME_FIELD] == TIME_CMD_ECHO:
    send_time(client)

def send_time(client):
  """Sends an EVENT message"""
  global MQTT_EVENTS_TOPIC
  # Adding a subfolder to the topic for easier
  # dispatchment of the message on the Cloud.
  # If a dedicated topic for the subfolder is
  # not configured in IoT Core, the message
  # will be delivered to the default topic
  # and the subfolder will be kept as a
  # parameter of the message.
  topic = "{}/time".format(MQTT_EVENTS_TOPIC)
  print(colored("Publishing the current time...", "green"))
  client.publish(topic, json.dumps({
    "current_time": datetime.datetime.now().isoformat()
  }))

# --------------------------------------------------
# TELEMETRY
# --------------------------------------------------
def send_telemetry(client):
  """Sends a telemetry information message"""
  global MQTT_EVENTS_TOPIC
  # No subfoldere here, just publish the telemetry
  # to its default topic.
  print(colored("Publishing telemetry...", "green"))
  client.publish(MQTT_EVENTS_TOPIC, json.dumps({
    "time": datetime.datetime.now().isoformat(),
    "power": (random.randint(1,15) / 10) # Simulated
  }))

# --------------------------------------------------
# STATE MANAGEMENT
# --------------------------------------------------
def send_state(client):
  """Sends the current device STATE to the Cloud"""
  global CURRENT_STATE
  global MQTT_STATE_TOPIC
  print(colored("Publishing the current state...", "green"))
  client.publish(
    MQTT_STATE_TOPIC,
    json.dumps(CURRENT_STATE),
    qos=1 # Retry on failure
  )

# --------------------------------------------------
# CLOUD AUTHENTICATION
# --------------------------------------------------
def create_jwt(project_id, private_key_file, algorithm):
    """Creates a JWT (https://jwt.io) to establish an MQTT connection.
    Args:
      project_id: The cloud project ID this device belongs to
      private_key_file: Path to a RSA256 or ES256 private key file.
      algorithm: The encryption algorithm to use, 'RS256' or 'ES256'.
    Returns:
      A JWT generated from the given project_id and private key, which
      expires in 20 minutes. After 20 minutes, your client will be
      disconnected, and a new JWT will have to be generated.
    Raises:
      ValueError: If the private_key_file does not contain a known key.
    """

    token = {
        # The time that the token was issued at
        "iat": datetime.datetime.now(tz=datetime.timezone.utc),
        # The time the token expires.
        "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(minutes=20),
        # The audience field should always be set to the GCP project id.
        "aud": project_id,
    }

    # Read the private key file.
    with open(private_key_file, "r") as f:
        private_key = f.read()

    print(
      colored(
        "Creating JWT using {} from private key file {}".format(
            algorithm, private_key_file
        ),
        "magenta"
      )
    )

    return jwt.encode(token, private_key, algorithm=algorithm)

# --------------------------------------------------
# MQTT EVENT HANDLERS
# --------------------------------------------------
def error_str(rc):
    """Convert a Paho error to a human readable string."""
    return "{}: {}".format(rc, mqtt.error_string(rc))

def on_connect(unused_client, unused_userdata, unused_flags, rc):
    """Callback for when a device connects."""
    global SHOULD_BACKOFF
    global MIN_BACKOFF_TIME
    print(colored("on_connect", "blue"), mqtt.connack_string(rc))
    # After a successful connect, reset backoff time and stop backing off.
    SHOULD_BACKOFF = False
    MIN_BACKOFF_TIME = 1

def on_disconnect(unused_client, unused_userdata, rc):
    """Paho callback for when a device disconnects."""
    global SHOULD_BACKOFF
    print(colored("on_disconnect", "blue"), error_str(rc))
    # Since a disconnect occurred, the next loop iteration will wait with
    # exponential backoff.
    SHOULD_BACKOFF = True

def on_publish(unused_client, unused_userdata, mid):
    """Paho callback when a message is sent to the broker."""
    print(
      colored("on_publish", "blue"),
      "Publishing message with ID: {}".format(mid)
    )

def on_message(client, unused_userdata, message):
    """Callback when the device receives a message on a subscription."""
    global MQTT_CONFIG_TOPIC
    payload = str(message.payload.decode("utf-8"))
    print(
      colored("on_message", "blue"),
      "Received message '{}' on topic '{}' with QoS {}".format(
          payload, message.topic, str(message.qos)
      )
    )
    if payload == "":
      print(colored("Ignoring the empty message.", "red"))
    elif (message.topic == MQTT_CONFIG_TOPIC):
      process_config_message(client, payload)
    else:
      process_command_message(client, payload)

# --------------------------------------------------
# INBOUND MESSAGES VALIDATION AND DISPATCHING
# --------------------------------------------------
def process_config_message(client, payload):
    """Process a config message"""
    print(colored("Processing a CONFIG message...", "white"))
    parsed_payload = parse_message(payload)
    if validate_config(parsed_payload):
      apply_config(client, parsed_payload)

def process_command_message(client, payload):
    """Process a command message"""
    print(colored("Processing a COMMAND message...", "cyan"))
    parsed_payload = parse_message(payload)
    if validate_command(parsed_payload):
      dispatch_command(client, parsed_payload)

# --------------------------------------------------
# MQTT CLIENT
# --------------------------------------------------
def connect_client(client, device_id, mqtt_bridge_hostname, mqtt_bridge_port):
  """Connect a client to the server and subscribe to the topics"""
  # Connect to the Google MQTT bridge.
  client.connect(mqtt_bridge_hostname, mqtt_bridge_port)

  # This is the topic that the device will receive configuration updates on.
  global MQTT_CONFIG_TOPIC
  MQTT_CONFIG_TOPIC = "/devices/{}/config".format(device_id)
  # Subscribe to the commands topic
  print(colored("Subscribing to Config: {}".format(MQTT_CONFIG_TOPIC), "cyan"))
  # Subscribe to the config topic.
  client.subscribe(MQTT_CONFIG_TOPIC, qos=1)

  # The topic that the device will receive commands on.
  global MQTT_COMMAND_TOPIC
  MQTT_COMMAND_TOPIC = "/devices/{}/commands/#".format(device_id)
  # Subscribe to the commands topic, QoS 1 enables message acknowledgement.
  print(colored("Subscribing to Commands: {}".format(MQTT_COMMAND_TOPIC), "cyan"))
  client.subscribe(MQTT_COMMAND_TOPIC, qos=0)

  return client

def get_client(
    project_id,
    cloud_region,
    registry_id,
    device_id,
    private_key_file,
    algorithm,
    ca_certs,
):
    """Create our MQTT client. The client_id is a unique string that identifies
    this device. For Google Cloud IoT Core, it must be in the format below."""
    client_id = "projects/{}/locations/{}/registries/{}/devices/{}".format(
        project_id, cloud_region, registry_id, device_id
    )
    print(colored("Device client_id is '{}'".format(client_id), "green"))

    client = mqtt.Client(client_id=client_id)

    # With Google Cloud IoT Core, the username field is ignored, and the
    # password field is used to transmit a JWT to authorize the device.
    client.username_pw_set(
        username="unused", password=create_jwt(project_id, private_key_file, algorithm)
    )

    # Enable SSL/TLS support.
    client.tls_set(ca_certs=ca_certs, tls_version=ssl.PROTOCOL_TLSv1_2)

    # Register message callbacks: https://eclipse.org/paho/clients/python/docs/
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    return client

# --------------------------------------------------
# DEVICE LOGIC
# --------------------------------------------------
def mqtt_device_demo(args):
    """Simulates a IoT device."""
    global SHOULD_BACKOFF
    global MIN_BACKOFF_TIME
    global MAX_BACKOFF_TIME
    global MQTT_STATE_TOPIC
    global MQTT_EVENTS_TOPIC
    global MQTT_CONFIG_TOPIC
    global MQTT_COMMAND_TOPIC

    MQTT_STATE_TOPIC = "/devices/{}/{}".format(args.device_id, "state")
    MQTT_EVENTS_TOPIC = "/devices/{}/{}".format(args.device_id, "events")

    jwt_iat = datetime.datetime.now(tz=datetime.timezone.utc)
    jwt_exp_mins = args.jwt_expires_minutes
    client = get_client(
        args.project_id,
        args.cloud_region,
        args.registry_id,
        args.device_id,
        args.private_key_file,
        args.algorithm,
        args.ca_certs,
    )
    client = connect_client(
      client,
      args.device_id,
      args.mqtt_bridge_hostname,
      args.mqtt_bridge_port,
    )

    try:
      print(colored("Device running (press CTRL-C to stop)...", "yellow"))
      while True:
        # Process network events.
        client.loop()

        # Wait if backoff is required.
        if SHOULD_BACKOFF:
            # If backoff time is too large, give up.
            if MIN_BACKOFF_TIME > MAX_BACKOFF_TIME:
                print("Exceeded maximum backoff time. Giving up.")
                break
            # Otherwise, wait and connect again.
            delay = MIN_BACKOFF_TIME + random.randint(0, 1000) / 1000.0
            print("Waiting for {} before reconnecting.".format(delay))
            time.sleep(delay)
            MIN_BACKOFF_TIME *= 2
            client = connect_client(
              client,
              args.device_id,
              args.mqtt_bridge_hostname,
              args.mqtt_bridge_port,
            )

        # Refresh the JWT
        seconds_since_issue = (datetime.datetime.now(tz=datetime.timezone.utc) - jwt_iat).seconds
        if seconds_since_issue > 60 * jwt_exp_mins:
            print("Refreshing token after {}s".format(seconds_since_issue))
            jwt_iat = datetime.datetime.now(tz=datetime.timezone.utc)
            client.loop()
            client.disconnect()
            client = get_client(
                args.project_id,
                args.cloud_region,
                args.registry_id,
                args.device_id,
                args.private_key_file,
                args.algorithm,
                args.ca_certs,
                args.mqtt_bridge_hostname,
                args.mqtt_bridge_port,
            )

        # Send telemetry every 5 seconds
        for i in range(0, 5):
            time.sleep(1)
            client.loop()
        send_telemetry(client)
    except KeyboardInterrupt:
        pass

# --------------------------------------------------
# COMMAND LINE ARGUMENTS PARSER
# --------------------------------------------------
def parse_command_line_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=("Example Google Cloud IoT Core MQTT device connection code.")
    )
    parser.add_argument(
        "--algorithm",
        choices=("RS256", "ES256"),
        required=True,
        help="Encryption algorithm choice to generate the JWT.",
    )
    parser.add_argument(
        "--ca_certs",
        default="roots.pem",
        help="Path to the CA root certificate from https://pki.google.com/roots.pem",
    )
    parser.add_argument(
        "--cloud_region",
        default="us-central1",
        help="GCP Region"
    )
    parser.add_argument(
        "--device_id",
        required=True,
        help="Cloud IoT Core device ID (serial number)."
    )
    parser.add_argument(
        "--jwt_expires_minutes",
        default=20,
        type=int,
        help="Expiration time for the JWT tokens (in minutes).",
    )
    parser.add_argument(
        "--private_key_file",
        required=True,
        help="Path to private certificate key file."
    )
    parser.add_argument(
        "--project_id",
        default=os.environ.get("GOOGLE_CLOUD_PROJECT"),
        help="GCP Project ID.",
    )
    parser.add_argument(
        "--registry_id",
        required=True,
        help="Cloud IoT Core registry ID."
    )
    parser.add_argument(
        "--service_account_json",
        default=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
        help="Path to the Service Account JSON file.",
    )
    parser.add_argument(
        "--mqtt_bridge_hostname",
        default="mqtt.googleapis.com",
        help="MQTT bridge hostname.",
    )
    parser.add_argument(
        "--mqtt_bridge_port",
        choices=(8883, 443),
        default=8883,
        type=int,
        help="MQTT bridge port.",
    )
    return parser.parse_args()

# --------------------------------------------------
# MAIN
# --------------------------------------------------
def main():
    args = parse_command_line_args()
    mqtt_device_demo(args)
    print("Shutting down.")

if __name__ == "__main__":
    main()
