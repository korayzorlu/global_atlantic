from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from information.models import Contact, ContactCompanyHistory


@receiver(m2m_changed, sender=Contact.company.through)
def create_user_profile(sender, instance, action, **kwargs):
    """
    Creates company histories
    if contact updated, get or create company history
    if get set working status working
    if created default working
    """
    #  https://docs.djangoproject.com/en/dev/ref/signals/#m2m-changed
    if action not in ['post_remove', 'post_add']:
        return

    working_objs = []
    # contact actively working at there companies
    for company in instance.company.all():
        obj, created = ContactCompanyHistory.objects.get_or_create(company=company, contact=instance)
        working_objs.append(obj)
        if not created:
            obj.working_status = 'working'
            obj.save()
        else:
            continue

    # these are all of them (working and not working)
    # if not exist current working list, make them not working
    for history in instance.company_history.all():
        # print(history, working_objs)
        if history not in working_objs and history.working_status == 'working':
            history.working_status = 'not_working'
            history.save()
        else:
            continue
