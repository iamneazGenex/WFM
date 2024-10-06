from django.core.mail import send_mail
from django.conf import settings
from accounts.models import *


def run():
    employee = CustomUser.objects.get(employee_id=26328)
    print(employee.email)
    # try:
    #     send_mail(
    #         "Subject here",
    #         "Here is the message.",
    #         settings.DEFAULT_FROM_EMAIL,
    #         ["mehedimaruf@genexsvc.com"],
    #         fail_silently=False,
    #     )
    # except Exception as e:
    #     print(f"An error occurred while sending email: {e}")
