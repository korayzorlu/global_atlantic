import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')

app = Celery('core')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

#zamanlanmış görevler crontab(minute=0, hour='*/1')
app.conf.beat_schedule = {
    'exchange-rates-update': {
        'task': 'user.tasks.exchangeUpdate',
        'schedule': crontab(minute=0, hour=0),
        'args': '',
        'options': {
            'expires': 15.0,
        },
    },
    'dail_financial_report_send': {
        'task': 'report.tasks.sendMailDailyFinancialReport',
        'schedule': crontab(minute=35, hour=17),
        'args': '',
        'options': {
            'expires': 30.0,
        },
    },
    'dail_financial_report_send_test': {
        'task': 'report.tasks.sendMailDailyFinancialReportTest',
        'schedule': crontab(minute=11, hour=12),
        'args': '',
        'options': {
            'expires': 30.0,
        },
    },
}