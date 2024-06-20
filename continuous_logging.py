import asyncio

from power_log_manager import PowerLogManager
import argparse


async def main():
    print(f"Running metering for {args.device_name}")
    manager = PowerLogManager(args.device_name, experiment_name="continuous", polling=0.5, log_interval=300)
    await manager.log_data()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run metering with devices.')
    parser.add_argument('--device_name', type=str, help='Device Name to run metering for.', required=False)
    args = parser.parse_args()

    asyncio.run(main())
