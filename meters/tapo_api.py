from time import time
from datetime import datetime
from tapo import ApiClient
from tapo.requests import EnergyDataInterval
from power_log_manager import PowerLogResult


async def get_data_tapo(**kwargs) -> PowerLogResult:
    """
    Get data from TP-Link Tapo P115
    :param kwargs: Must include "device_ip", "tapo_user", and "tapo_password"
    :return: PowerLogResult containing energy readings
    """
    client = ApiClient(kwargs["tapo_user"], kwargs["tapo_password"])
    device = await client.p115(kwargs["device_ip"])

    current_draw = await device.get_current_power()
    current_draw = current_draw.current_power
    total_draw = await device.get_energy_data(EnergyDataInterval.Monthly, datetime(datetime.today().year, 1, 1))
    total_draw = sum(total_draw.data) / 1000
    timestamp = time()

    return PowerLogResult(timestamp=timestamp, current_draw=current_draw, total_draw=total_draw, misc=None)
