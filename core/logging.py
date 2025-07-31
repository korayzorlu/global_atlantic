import logging
from .middleware import get_current_user

class UserFilter(logging.Filter):
    def filter(self, record):
        user = get_current_user()
        if user and user.is_authenticated:
            record.username = user.username
        else:
            record.username = 'Anonymous'
        return True