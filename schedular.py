from apscheduler.schedulers.background import BackgroundScheduler

from services.job_scraper import scrape_jobs
from job_alert import send_daily_alerts
from cleanup_job import delete_old_jobs


def start_scheduler(app):

    scheduler = BackgroundScheduler()

    def run_scraper():
        with app.app_context():
            scrape_jobs()

    def run_alerts():
        with app.app_context():
            send_daily_alerts()
            
    def run_cleanup():
        with app.app_context():
            delete_old_jobs(app)

    scheduler.add_job(
        run_scraper,
        "cron",
        hour=6
    )

    scheduler.add_job(
        run_alerts,
        "cron",
        hour=9,
        minute = 30
    )

    scheduler.add_job(
        run_alerts,
        "cron",
        hour=18
    )
    
    scheduler.add_job(
        run_cleanup,
        "cron",
        hour=0,
        minute=0
    )

    scheduler.start()

    print("Scheduler Started")