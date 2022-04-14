# Smart Plug Simulator

This application simulates a IoT Smart Plug compatible with
[Google Cloud IoT Core](https://cloud.google.com/iot-core).

It is based on
[Google's official IoT Core Python sample code](https://github.com/GoogleCloudPlatform/python-docs-samples/blob/main/iot/api-client/mqtt_example/cloudiot_mqtt_example.py)

This virtual device can:

 * Connect to the Cloud
 * Refresh the `JWT` authentication
 * Handle reconnections with [exponential back-off](https://cloud.google.com/iot/docs/how-tos/exponential-backoff)
 * Apply incoming [`configuration`s](https://cloud.google.com/iot/docs/how-tos/config/configuring-devices)
 * Report [`state`](https://cloud.google.com/iot/docs/how-tos/mqtt-bridge#setting_device_state)
 * Receive [`command`s](https://cloud.google.com/iot/docs/how-tos/commands)
 * Publish [`telemetry`](https://cloud.google.com/iot/docs/how-tos/mqtt-bridge#publishing_telemetry_events)

## Requirements

 * [`Python 3.8+`](https://www.python.org/downloads/)
 * A valid **Google Cloud Platform** account
 * (optional) [`conda`](https://docs.conda.io/en/latest/)

## Usage

### Installation

 1. Create a virtual Python environment to run the project,
    with `conda` it can be created and activated with:
    ```bash
    $ conda create --name {ENV_NAME} --file environment.txt
    $ conda activate {ENV_NAME}
    ```
    replace `{ENV_NAME}` with a suitable environment name.
 2. Install the required dependencies:
    ```bash
    $ pip install -r requirements.txt
    ```
 3. Get [Google's CA root certificate](https://pki.google.com/roots.pem)
 4. Follow these chapters of the Google's Quickstart guide for IoT Core:
    * [Create a device registry](https://cloud.google.com/iot/docs/create-device-registry#create_a_device_registry)
    * [Create your credentials](https://cloud.google.com/iot/docs/create-device-registry#create_your_credentials)
    * [Add a device to the registry](https://cloud.google.com/iot/docs/create-device-registry#add_a_device_to_the_registry)

### Running the device simulator

Run:

```bash
python simulator.py \
  --project_id {PROJECT_ID} \
  --cloud_region {CLOUD_REGION} \
  --registry_id {REGISTRY_NAME} \
  --device_id {DEVICE_ID} \
  --private_key_file {PATH_TO_THE_KEY_FILE} \
  --algorithm RS256
```

replace the `{..}` placeholders with the values used in step 4. of the list above.

Run:

```bash
$ python simulator.py -h
```

to get the full list of options.

## Disclaimer

**Using Google Cloud Platform's services costs money.**
It is the users' responsibility to verify the pricing of the services required
by this software and understand how much it will cost them to run it.
