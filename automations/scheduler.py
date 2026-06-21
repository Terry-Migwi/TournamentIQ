from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import subprocess
import time

def run_ingestion():
    print("Running ingestion scripts...")
    subprocess.run(["python", "ingest_teams.py"])
    subprocess.run(["python", "ingest_standings.py"])
    subprocess.run(["python", "ingest_matches.py"])
    print("Ingestion complete.")

scheduler = BackgroundScheduler()
scheduler.add_job(
    run_ingestion,
    CronTrigger(hour=0, minute=0)  # runs daily at midnight UTC
)

if __name__ == "__main__":
    scheduler.start()
    print("Scheduler running. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        scheduler.shutdown()
        print("Scheduler stopped.")