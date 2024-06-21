from time import sleep
from power_log_manager import PowerLogManager

manager = PowerLogManager("mock_plug", experiment_name="test_experiment", polling=0.5, log_interval=3)
manager.start_experiment_logging()
print("Started experiment logging")
sleep(10)
manager.finish_experiment_logging()
print("Finished experiment logging")
