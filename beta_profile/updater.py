import datetime
import os
from ssl import SSLError

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils.timezone import get_default_timezone

from beta_profile.models import Currency


def start():
    scheduler = BackgroundScheduler()

    UpdateCurrencies(hour=16, minute=00, scheduler=scheduler, cron=True)

    scheduler.start()

    # for job in scheduler.get_jobs():
    #     print(job.next_run_time)


class UpdateCurrencies:

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
        last_update_time = Currency.get_last_currency_update_time().astimezone(timezone)
        time_passed = now - last_update_time

        if not cron:
            hours, minutes, seconds = kwargs.pop('hours', 1), kwargs.pop('minutes', 0), kwargs.pop('seconds', 0)
            period = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
            next_run_time = last_update_time + period

            if time_passed >= period:
                print(f"Currency Scheduler: {time_passed} geçtiği için çalıştı.")
                scheduler.add_job(self.update, 'interval', hours=hours, minutes=minutes, seconds=seconds,
                                  next_run_time=now)
            else:
                print(f"Currency Scheduler: Henüz {time_passed} geçti, {next_run_time}'da çalışacak.")
                scheduler.add_job(self.update, 'interval', hours=hours, minutes=minutes, seconds=seconds,
                                  next_run_time=next_run_time)
        else:
            hour, minute, second = kwargs.pop('hour', 0), kwargs.pop('minute', 0), kwargs.pop('second', 0)
            if now.strftime("%Y%m%d") != last_update_time.strftime("%Y%m%d"):
                print(f"Currency Scheduler: En son 1 günden daha önce çalıştığı için çalıştı.")
                scheduler.add_job(self.update, 'cron', hour=hour, minute=minute, second=second, next_run_time=now)
            else:
                print(f"Currency Scheduler: En yakın {hour, minute, second}'ta çalışacak.")
                scheduler.add_job(self.update, 'cron', hour=hour, minute=minute, second=second)

    @staticmethod
    def get_page(url, counter=10, dynamic_verification=True):
        """
        Returns response
        @param url:
        @param counter:
        @param dynamic_verification:
        @return:
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        }
        verify = True
        for count in range(1, counter + 1):
            try:
                response = requests.get(url, timeout=10, headers=headers, verify=verify)
                return response
            except ConnectionError as cae:
                print("A weird connection error!", count, url, cae)
                continue
            except Exception as e:
                print('Error occurred while getting page content!', count, url, e)
                if dynamic_verification and type(e) == SSLError:
                    verify = False
                continue
        raise TimeoutError

    @classmethod
    def update(cls):
        print('Updating currencies...')
        api_url = "http://data.fixer.io/api/latest?access_key={}&format=1".format(os.getenv('DATA_FIXER_IO_ACCESS_KEY'))
        try:
            response = cls.get_page(api_url, counter=3)
        except (TimeoutError, TypeError, ValueError) as e:
            print(e)
            return
        data = response.json()
        # if data['success']:
        #     base = data['base']
        #     for currency, rate in data['rates'].items():
        #         obj, created = Currency.objects.get_or_create(base=base, name=currency)
        #         obj.rate = rate
        #         obj.save()
