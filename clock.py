from apscheduler.schedulers.blocking import BlockingScheduler

from app.user_inventory import user_inventory

sched = BlockingScheduler()


@sched.scheduled_job('cron', day_of_week='mon-sun', hour=17)
def run_user_inventory():
    user_inventory()


sched.start()
