from time import sleep
from power_log_manager import PowerLogManager

with PowerLogManager("mock_plug", experiment_name="test_experiment", polling=0.5, log_interval=3) as manager:
    sleep(10)
