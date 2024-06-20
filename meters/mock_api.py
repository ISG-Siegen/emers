from numpy import random
from time import time

from power_log_manager import PowerLogResult


async def get_data_mock(**kwargs) -> PowerLogResult:
    current_draw = random.randint(20, 250)
    total_draw = random.randint(1, 5)
    timestamp = time()

    return PowerLogResult(timestamp=timestamp, current_draw=current_draw, total_draw=total_draw, misc=None)
