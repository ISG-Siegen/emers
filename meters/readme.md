# Power Meter Readers

Every file in this directory contains an asynchronous method `get_data_<device_type>(**kwargs)` that reads data from a
specific power meter device and returns a `PowerLogResult` object that contains energy readings.

### Supported Devices

0. [Mock Plug (for debug)](mock_api.py)
1. [Shelly Plug Plus S](shelly_api.py)
2. [TP-Link Tapo P115](tapo_api.py)

### Adding Support for New Devices

1. Choose a name for your new device type. We will refer to this name as `<device_type>`.
2. Add a new entry in `settings.json` with the desired `name` of the new plug. One of the keys in this new entry must
   be `device_type` and its value must be your chosen `<device_type>`. The remaining key-value pairs should be other
   parameters of your choice that are required to read data from the new device type. They will be available in the data
   reading function as keyword arguments.
3. Add a new file `<device_type>_api.py` in this directory.
4. Implement an asynchronous function `get_data_<device_type>(**kwargs)` in the newly created file. The keyword
   arguments that are passed to this function are taken from `settings.json`. This function must return
   a `PowerLogResult` object.
