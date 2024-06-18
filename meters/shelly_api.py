import requests
from meters.power_log_result import PowerLogResult
from time import time


def get_data_shelly(**kwargs) -> PowerLogResult:
    headers = {'Content-Type': 'application/x-www-form-urlencoded', }
    request_data = ('{"id":1, '
                    f'"src":"{kwargs["device_id"]}", '
                    '"method":"Switch.GetStatus", '
                    '"params":{"id":0}}')
    response = requests.post(kwargs["device_ip"], headers=headers, data=request_data)

    if response.status_code != 200:
        raise Exception(f"API call failed. Status code: {response.status_code} \n Response: {response}")

    data = response.json()

    electricity_info = data['result']
    current_enery_draw = electricity_info['apower']

    '''
    total_watt_hours = electricity_info['aenergy']['total']
    total_watt_hours_minute_ts = electricity_info['aenergy']['minute_ts']    
    current_voltage = electricity_info['voltage']
    current_current = electricity_info['current']
    current_temperature_C = electricity_info['temperature']['tC']
    '''

    timestamp = time()

    result = PowerLogResult(timestamp=timestamp, draw=current_enery_draw, misc=None)

    return result
