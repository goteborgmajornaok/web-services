from apscheduler.schedulers.blocking import BlockingScheduler

from app.user_inventory import user_inventory

sched = BlockingScheduler()


@sched.scheduled_job('cron', hour=15, minute=8)
def run_user_inventory():
    user_inventory()


sched.start()
