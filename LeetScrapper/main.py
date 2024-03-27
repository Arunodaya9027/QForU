from launch import launch_scraper
import time
import schedule

def main():
    ms = launch_scraper()
    ms.start()
    # Simulating program execution time
    time.sleep(2 * 60)  # 2 minutes


# Define the job to run at 10 am
schedule.every().day.at("21:56").do(main)

while True:
    # Check if there are any pending jobs
    if schedule.next_run():
        # Calculate the time until the next run
        next_run_time = schedule.next_run().timestamp()
        current_time = time.time()
        delay = next_run_time - current_time

        if delay > 0:
            print(f"Next run in {delay} seconds.")
            time.sleep(delay)
    else:
        print("No scheduled runs found.")
        break

    # Run the scheduled job
    schedule.run_pending()

    # Check if the current time is past the scheduled run time
    current_time = time.time()
    if current_time >= next_run_time:
        continue

