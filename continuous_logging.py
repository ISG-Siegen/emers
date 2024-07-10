import asyncio

from power_log_manager import PowerLogManager
import argparse


async def main():
    print(f"Running continuous logging for {args.device_name} with "
          f"polling rate {args.polling_rate} and log interval {args.log_interval}...")
    manager = PowerLogManager(device_name=args.device_name, experiment_name="continuous",
                              polling_rate=args.polling_rate, log_interval=args.log_interval)
    await manager.log_data()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run metering with devices.')
    parser.add_argument('--device_name', type=str, required=True)
    parser.add_argument('--polling_rate', type=str, required=False, default=0.5)
    parser.add_argument('--log_interval', type=str, required=False, default=300)
    args = parser.parse_args()

    asyncio.run(main())
