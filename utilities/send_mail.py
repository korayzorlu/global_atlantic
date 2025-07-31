from concurrent.futures import ThreadPoolExecutor

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives


def custom_send_mail(subject, from_email, recipient_list, template_path, context, document=None,
                     fail_silently=False, auth_user=None, auth_password=None, connection=None):
    html_message = render_to_string(template_path, context)
    
    msg = EmailMultiAlternatives(subject, 'Test Email', from_email, recipient_list, connection=connection)
    msg.attach_alternative(html_message, "text/html")
    if document:
        filepdf = document.file.read()
        msg.attach(document.get_filename(),filepdf, "application/pdf")
    msg.send(fail_silently)
    
    # ThreadPoolExecutor().submit(
    #     send_mail,
    #     subject,
    #     strip_tags(html_message),
    #     from_email,
    #     recipient_list,
    #     html_message=html_message,
    #     fail_silently=fail_silently,
    #     auth_user=auth_user,
    #     auth_password=auth_password,
    #     connection=connection,
    # )
