from power_log_manager import PowerLogManager

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Run metering with devices.')
    parser.add_argument('--device_name', type=str, help='Device Name to run metering for.', required=False)
    args = parser.parse_args()

    print(f"Running metering for {args.device_name}")
    manager = PowerLogManager(args.device_name)
    manager.log_data()
