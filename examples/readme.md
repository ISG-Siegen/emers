# Usage Examples

## Measuring energy consumption

Measuring energy consumption comes in two logging modes: continuous and integrated.

### Continuous logging

1. Continuous logging is designed to be run as a separate Python script and logs energy consumption data until stopped.
2. Continuous logging is implemented in `continuous_logging.py`.
3. To run continuous logging, execute the following command in your terminal:

    ```bash
     python continuous_logging.py --device_name <device_name> --polling_rate <polling_rate> --log_interval <log_interval>
    ```

    1. Replace `<device_name>` with the name of the device as specified in `settings.json`.
    2. The default `<polling_rate>` is 0.5 (seconds), e.g., the smart plug is polled twice a second.
    3. The default `<log_interval>` is 300 (seconds), e.g., a new log file is created every 300 seconds.

4. The logs are saved in the `measurements` directory. A new directory is created for each device, and
   continuous logs are saved in a directory named `continuous`.
5. End the process at any time to stop continuous logging.
6. Run the script again to restart continuous logging.

### Integrated logging

1. Integrated logging is designed to be used within code that executes experiments.
2. Integrated logging is implemented in `power_log_manager.py`.
3. The following Python code is a simplified example of what a recommender systems experiment may generally look like:

    ```python
    from my_functions import load_data, split_data, train_model, evaluate_model

    data = load_data()
    train, test = split_data(data)
    model = train_model(train)
    predictions = model.predict(test)
    evaluate_model(predictions)
    ```

    1. The code snippet assumes that the functions `load_data`, `split_data`, `train_model`, and `evaluate_model` are
       defined elsewhere in the project.

4. Integrated logging can be added to the code snippet above to log energy consumption data at specific points
   in during execution. For example, to log only the training phase, the code snippet would be modified to look like
   this:

    ```python
    from my_functions import load_data, split_data, train_model, evaluate_model
    from power_logger import PowerLogManager
    
    data = load_data()
    with PowerLogManager(device_name=device_name, experiment_name=experiment_name, polling_rate=polling_rate, log_interval=log_interval) as manager:
        train, test = split_data(data)
    model = train_model(train)
    predictions = model.predict(test)
    evaluate_model(predictions)
    ```   

    1. Replace `device_name` with the name of the device as specified in `settings.json`.
    2. Replace `experiment_name` with the name of the experiment, e.g., `my_algorithm_training`.
    3. The default `polling_rate` is 0.5 (seconds), e.g., the smart plug is polled twice a second.
    4. The default `log_interval` is 300 (seconds), e.g., a new log file is created every 300 seconds.
    5. The `PowerLogManager` class is a context manager that logs energy consumption data during the execution of the
       code block within the `with` statement. It automatically starts logging when entering the block and stops logging
       when exiting the block, organizing the logs by device and experiment.

5. The logs are saved in the `measurements` directory. A new directory is created for each device, and
   integrated logs are saved in a directory named `experiment_name`.

## Monitoring energy consumption

The monitoring interface is a web application that visualizes energy consumption data.

### Running the monitoring interface

1. It is implemented in `monitoring_interface.py`.
2. To start the monitoring interface, execute the following command in your terminal:

    ```bash
    python monitoring_interface.py --ip <ip> --port <port>
    ```
    1. Replace `<ip>` with the IP address of the computer running the monitoring interface. The default is `localhost`.
    2. Replace `<port>` with the port number to run the monitoring interface on. The default is `5000`.

3. The monitoring interface can be accessed in a web browser at `http://<ip>:<port>`.

### Using the monitoring interface

The monitoring interface consists of five major regions.

1. **Device/Experiment Selection**: A dropdown menu to select the device/experiment to monitor.
    1. There are three dropdown menus: One for the device, one for the experiment, and one for specific log files. The
       selected items will be used to display the energy consumption graph and information.
2. **Cost/Footprint Settings and Report Generation**: A form to set the cost and carbon footprint of energy and buttons
   to generate a sharable report.
    1. The cost of energy per kWh, its currency, and the carbon footprint of energy per kWh in gCO2e can be adjusted
       here. The values will be used to calculate the cost and carbon footprint of the energy consumption. To
       persistently modify these settings, modify the `monitor_settings.json` file.
    2. Two types of reports can be generated: A summary report of the selected device/experiment and a detailed report
       of the whole project.
3. **Energy Consumption Graph Settings**: A form to toggle live updating and smoothness of the energy consumption graph.
    1. Live updating is disabled by default and can be toggled at any time. The update interval can also be configured
       here.
    2. A smoothed version of each graph can be displayed. This is toggled here and the rolling window size for
       smoothness can be adjusted here as well.
4. **Device/Experiment Information**: Tabular information about the energy consumption the selected device/experiment.
    1. This is a table containing information about the energy consumption, cost, and carbon footprint of the selected
       device/experiment.
5. **Energy Consumption Graph**: A live updating graph of energy consumption.
    1. Two graphs are displayed: One for the energy consumption at specific time stamps and one for the total energy
       consumption.