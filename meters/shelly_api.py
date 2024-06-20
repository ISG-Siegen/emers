from requests import post
from time import time
from power_log_manager import PowerLogResult


async def get_data_shelly(**kwargs) -> PowerLogResult:
    headers = {'Content-Type': 'application/x-www-form-urlencoded', }
    request_data = ('{"id":1, '
                    f'"src":"{kwargs["device_id"]}", '
                    '"method":"Switch.GetStatus", '
                    '"params":{"id":0}}')
    response = post(kwargs["device_ip"], headers=headers, data=request_data)

    if response.status_code != 200:
        raise Exception(f"API call failed. Status code: {response.status_code} \n Response: {response}")

    data = response.json()
    electricity_info = data['result']

    current_draw = electricity_info['apower']
    total_draw = electricity_info['aenergy']['total']
    timestamp = time()

    return PowerLogResult(timestamp=timestamp, current_draw=current_draw, total_draw=total_draw, misc=None)
