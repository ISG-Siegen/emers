# EMERS: Energy Meter for Recommender Systems

EMERS is the first software library that measures, monitors, records, and shares the energy consumption of recommender
systems experiments.

EMERS reads and logs energy readings from smart plugs, organizes them based on the associated research experiment,
provides a user interface to monitor and analyze measurements, and creates a standardized, automated report to share
with the community.

## Features

1. User interface to visualize measured energy consumption: [Monitoring Interface](monitoring_interface.py)
2. Report of energy consumption for selected experiments through the user interface.
3. Integrate energy consumption measurements in your project: [Integration Example](integration_example.py)
4. Continuously measure energy consumption: [Continuous Logging](continuous_logging.py)

## Requirements

1. A smart plug that can read and transmit energy consumption data. Supported devices, setup instructions, and
   instructions to add new devices are found in the `meters` directory.
2. Python 3.10 and the required packages. Install them with `pip install -r requirements.txt`.

## Usage

1. Refer to the `examples` directory for usage examples.

2. For continuous measurement, run the script `continuous_logging.py`, providing the device name.
3. For integrating energy logging into your project, see the example script `integration_example.py`.
4. The monitoring user interface runs on a Flask server and can be started with the script `monitoring_interface.py`.
   You can then access the interface at `http://localhost:5000`.