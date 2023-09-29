import schedule
import time
import datetime
import subprocess
from src import config

# Function to execute the Python file you want to run
def run_python_file():
    # Replace 'your_python_file.py' with the actual Python file you want to run
    subprocess.run(['python', 'carter.py'])

# Function to schedule the job at NYSE market open time (9:30 AM on the first trading day of the month)
def schedule_monthly_job():
    today = datetime.date.today()
    first_trading_day_of_month = today.replace(day=1)
    if today == first_trading_day_of_month:
        # Schedule the job for 9:30 AM (NYSE market open time) on the first trading day of the month
        schedule.every().minute.at('09:30').do(run_python_file)

# Schedule the job
schedule_monthly_job()

while True:
    schedule.run_pending()
    time.sleep(1)
