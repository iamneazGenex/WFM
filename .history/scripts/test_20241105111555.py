from django.core.mail import send_mail
from django.conf import settings
from accounts.models import *
from roster.models import *
from changeRequest.utils import *


def run():
    workRule = WorkRule.objects.get(id=1)
    requestorRoster = Roster.objects.get(id=4179)
    requestee = Employee.objects.get(id=214096)
    requesteeRoster = Roster.objects.filter(
        Q(employee=requestee),
        Q(start_date=requestorRoster.start_date),
        Q(end_date=requestorRoster.end_date),
    ).first()
    requestorRegularShiftDurationResult, requestorRegularShiftDurationError = (
        checkRegularShiftDuration(
            roster=requestorRoster,
            workRule=workRule,
        )
    )
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
