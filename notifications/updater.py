from apscheduler.schedulers.background import BackgroundScheduler
from notifications.models import Notification
from notifications.utilities import create_notification
from django.utils.timezone import get_default_timezone
import datetime

from sales.models import Quotation

def start():
    scheduler = BackgroundScheduler()

    TimeBasedNotification(hours=12, minutes=0, seconds=0, scheduler=scheduler, cron=False)

    scheduler.start()

    # for job in scheduler.get_jobs():
    #     print(job.next_run_time)
    
    
class TimeBasedNotification:
    """"""
    def __init__(self, scheduler, **kwargs):
        """
        This functions ensure the first run of scheduler
        by checking last update time from database
        need same keyword arguments with add_job
        @param kwargs:
        """
        cron = kwargs.pop('cron', None)
        timezone = get_default_timezone()
        now = datetime.datetime.now(timezone)    
        last_update_time = Notification.get_last_notification_update_time().astimezone(timezone)      
        time_passed = now - last_update_time
        hours, minutes, seconds = kwargs.pop('hours', 1), kwargs.pop('minutes', 0), kwargs.pop('seconds', 0)

        if not cron:
            period = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
            next_run_time = last_update_time + period           
            if time_passed >= period:
                print(f"Currency Notification Scheduler: {time_passed} geçtiği için çalıştı.")
                scheduler.add_job(self.CheckAndCreateNotification, 'interval', hours=hours, minutes=minutes, seconds=seconds,
                                  next_run_time=now)
            else:
                print(f"Currency Notification Scheduler: Henüz {time_passed} geçti, {next_run_time}'da çalışacak.")
                scheduler.add_job(self.CheckAndCreateNotification, 'interval', hours=hours, minutes=minutes, seconds=seconds,
                                  next_run_time=next_run_time)
        else:
            period = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
            print((now -last_update_time))
            if time_passed > period:
                print(f"Currency Notification Scheduler: En son 1 günden daha önce çalıştığı için çalıştı.")
                scheduler.add_job(self.CheckAndCreateNotification, 'cron', hour=hours, minute=minutes, second=seconds, next_run_time=now)
            else:
                print(f"Currency Notification Scheduler: En yakın {hours, minutes, seconds}'ta çalışacak.")
                scheduler.add_job(self.CheckAndCreateNotification, 'cron', hour=hours, minute=minutes, second=seconds)
    
    @classmethod
    def CheckAndCreateNotification(self):
        """"""
        print('Checking Quotations')
        quotations = Quotation.objects.filter(is_notified=False, project__is_closed=False, project__stage='quotation', confirmation__isnull=True, notconfirmation__isnull=True).exclude(parts__isnull=True)
        timezone = get_default_timezone()
        now = datetime.datetime.now(timezone)
        for quotation in quotations:
            first_part = quotation.parts.first()

            if (now - first_part.created_at).days >= 14:
                print("creating notifications")
                create_notification(to_user=quotation.project.responsible, notification_type=Notification.CONFIRMATION, url_key="sales:project_quotation_notification", relationed_object_id=quotation.project.id, optional_id=quotation.id)
                quotation.is_notified=True
                quotation.save()
          
        

