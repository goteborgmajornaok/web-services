from apscheduler.schedulers.blocking import BlockingScheduler

from application.user_inventory import user_inventory

sched = BlockingScheduler()


@sched.scheduled_job('cron', hour=0)
def run_user_inventory():
    user_inventory()


sched.start()
