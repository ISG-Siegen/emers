# Power Consumption Monitor

## Features

1. Continuously read and log energy data from a smart power plug: [Continuous Logging](continuous_logging.py)
2. Integrate energy data logging in your project and monitor your
   experiments: [Integration Example](integration_example.py)
3. Run the monitoring user interface to visualize logged energy data: [Monitoring Interface](monitoring_interface.py)

## Usage

1. Energy logging requires setup of your device in `settings.json`. For required settings, see the documentation of the
   API class for your device type in the `meters` directory.
2. For continuous logging of a plug, run the script `continuous_logging.py`, providing the device name.
3. For integrating energy logging into your project, see the example script `integration_example.py`.
4. The monitoring user interface runs on a Flask server and can be started with the script `monitoring_interface.py`.
   You can then access the interface at `http://localhost:5000`.