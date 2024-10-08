import asyncio
import csv
import json
import threading
from dataclasses import dataclass
from pathlib import Path
from time import time, sleep
from typing import Optional

stop_event = threading.Event()
loop_thread = None


@dataclass
class MeasurementLogResult:
    """
    Dataclass to store the result of a smart plug reading.
    """
    timestamp: float
    current_draw: float
    total_draw: float
    misc: Optional[dict] = None


class MeasurementManager:
    """
    Class to manage the measuring and logging of power data from a smart plug.
    """

    def __init__(self, device_name, experiment_name=None, polling_rate=0.5, log_interval=300):
        """
        Initialize the MeasurementManager.
        :param device_name: The name of the device that will be used to retrieve connection parameters.
        :param experiment_name: The name of the experiment that this data will be logged under.
        :param polling_rate: The rate at which the device will be polled for data in seconds.
        :param log_interval: The interval at which the log file will be rotated in seconds.
        """
        self.stop_event = threading.Event()
        self.loop_thread = None
        self.device_name = device_name
        self.experiment_name = experiment_name
        self.polling_rate = polling_rate
        self.log_interval = log_interval

        with open("settings.json", "r") as file:
            devices = json.load(file)

        if self.device_name not in devices:
            raise ValueError(f"Device {self.device_name} not found in settings.json")

        self.device = devices[self.device_name]

    def _start_experiment_logging(self):
        """
        Start the experiment logging. Private method.
        """
        if self.loop_thread is None or not self.loop_thread.is_alive():
            self.stop_event.clear()

            def async_intermediate():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.log_data())
                loop.close()

            self.loop_thread = threading.Thread(target=async_intermediate)
            self.loop_thread.start()

        print(f"EMERS logging started for device {self.device_name}, "
              f"experiment {self.experiment_name} with "
              f"polling rate {self.polling_rate} and "
              f"log interval {self.log_interval}.")

    def _finish_experiment_logging(self):
        """
        Finish the experiment logging. Private method.
        """
        if self.loop_thread is not None and self.loop_thread.is_alive():
            self.stop_event.set()
            self.loop_thread.join()
            self.loop_thread = None

        print(f"EMERS logging stopped for device {self.device_name}, "
              f"experiment {self.experiment_name} with "
              f"polling rate {self.polling_rate} and "
              f"log interval {self.log_interval}.")

    def __enter__(self):
        """
        Enter the context manager.
        """
        self._start_experiment_logging()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager.
        """
        self._finish_experiment_logging()

    async def log_data(self):
        """
        Log data from the smart plug.
        """
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
                    writer.writerow(['timestamp', 'current_draw', 'total_draw'])

            result: MeasurementLogResult = await api(**self.device)

            with open(log_file_name, 'a', newline='') as log_file:
                writer = csv.writer(log_file)
                writer.writerow([result.timestamp, result.current_draw, result.total_draw])

            sleep(self.polling_rate)
