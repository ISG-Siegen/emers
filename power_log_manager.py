import csv
import json
import threading
from pathlib import Path
from time import time, sleep

stop_event = threading.Event()
loop_thread = None


class PowerLogManager:
    def __init__(self, device_name, experiment_name=None, polling=0.5, log_interval=300):
        self.stop_event = threading.Event()
        self.loop_thread = None
        self.device_name = device_name
        self.experiment_name = experiment_name
        self.polling = polling
        self.log_interval = log_interval

        with open("settings.json", "r") as file:
            devices = json.load(file)

        if self.device_name not in devices:
            raise ValueError(f"Device {self.device_name} not found in settings.json")

        self.device = devices[self.device_name]

    def start_experiment_logging(self):
        if self.loop_thread is None or not self.loop_thread.is_alive():
            self.stop_event.clear()
            self.loop_thread = threading.Thread(target=self.log_data)
            self.loop_thread.start()

        print("Logging started")

    def finish_experiment_logging(self):
        if self.loop_thread is not None and self.loop_thread.is_alive():
            self.stop_event.set()
            self.loop_thread.join()
            self.loop_thread = None
        print("Logging stopped")

    def log_data(self):
        device_type = self.device["device_type"]

        module_name = f"meters.{device_type}_api"
        function_name = f"get_data_{device_type}"

        try:
            module = __import__(module_name, fromlist=[function_name], globals={"__name__": __name__})
            api = getattr(module, function_name)
        except ImportError as e:
            raise ImportError(f"Error importing module {module_name}: {e}")

        if self.experiment_name is not None:
            log_base = Path(f"./measurements/{self.device_name}/{self.experiment_name}")
            log_base.mkdir(exist_ok=True, parents=True)
        else:
            log_base = Path(f"./measurements/{self.device_name}")
            log_base.mkdir(exist_ok=True, parents=True)

        start_timestamp = time()

        log_file_name = log_base / f"{start_timestamp}.csv"

        while not self.stop_event.is_set():
            if not Path(log_file_name).exists() or start_timestamp + self.log_interval <= time():
                if start_timestamp + self.log_interval <= time():
                    start_timestamp += self.log_interval
                log_file_name = log_base / f"{start_timestamp}.csv"
                with open(log_file_name, 'w', newline='') as log_file:
                    writer = csv.writer(log_file)
                    writer.writerow(['timestamp', 'draw'])

            result = api(**self.device)

            with open(log_file_name, 'a', newline='') as log_file:
                writer = csv.writer(log_file)
                writer.writerow([result.timestamp, result.draw])

            sleep(self.polling)
