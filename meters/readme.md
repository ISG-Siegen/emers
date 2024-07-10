# Energy Meter Interfaces

Every file in this directory contains an asynchronous method `get_data_<device_type>(**kwargs)` that reads data from a
specific smart plug and returns a `PowerLogResult` object that contains energy measurements.

### Supported Devices

0. [Mock Plug (fake data for debugging)](mock_api.py)
1. [Shelly Plug Plus S](shelly_api.py)
2. [TP-Link Tapo P115](tapo_api.py)

### Setup Instructions for Supported Devices

1. Obtain either the Shelly Plug Plus S or the TP-Link Tapo P115 smart plug.
2. Read the manual of the smart plug to find out how to connect it to your Wi-Fi network and perform the initial setup.
   Make sure that the smart plug is connected to the same network as the computer running this software.
3. Open `settings.json` and add an entry for the smart plug. The key is the desired identifier of the plug. The value
   should be a dictionary with the following keys:
    1. `device_type`: The type of the device. This must be one of the supported device types.
    2. `device_ip`: The IP address of the plug.
    3. For Shelly Plug Plus S:
        1. `device_id`: The device ID of the plug. This is usually `0` if this is the only Shelly Plug Plus S on the
           network.

       Example settings entry for Shelly Plug Plus S:
          ```json
          "shelly_meter": {
              "device_type": "shelly",
              "device_ip": "192.168.2.1",
              "device_id": "0",
          }
          ```
    4. For TP-Link Tapo P115:
        1. `tapo_user`: The username of the Tapo account that the plug is connected to.
        2. `tapo_password`: The password of the Tapo account that the plug is connected to.

       Example settings entry for TP-Link Tapo P115:
          ```json
          "tapo_meter": {
              "device_type": "tapo",
              "device_ip": "192.168.2.2",
              "tapo_user": "yourname@provider.com",
              "tapo_password": "password",
          }
          ```
4. . `name`: The name of the plug.

### Adding Support for New Devices

1. Choose a name for your new device type. We will refer to this name as `<device_type>`.
2. Add a new file `<device_type>_api.py` in this directory.
3. Implement an asynchronous function `get_data_<device_type>(**kwargs) -> PowerLogResult` in the newly created file.
   Document the required keyword arguments that are passed to this function. These must be defined when configuring a
   device of `<device_type>` in `settings.json`.
