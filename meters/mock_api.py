import numpy as np
from meters.power_log_result import PowerLogResult
from time import time


def get_data_mock(**kwargs) -> PowerLogResult:
    timestamp = time()
    draw = np.random.randint(0, 100)

    result = PowerLogResult(timestamp=timestamp, draw=draw, misc=None)

    return result
