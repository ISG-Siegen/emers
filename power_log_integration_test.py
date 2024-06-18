from time import sleep
from power_log_manager import PowerLogManager

manager = PowerLogManager("mock_plug", experiment_name="mock_plug", polling=0.5, log_interval=3)
manager.start_experiment_logging()
print("Sleeping")
sleep(4)
print("Done sleeping")
manager.finish_experiment_logging()