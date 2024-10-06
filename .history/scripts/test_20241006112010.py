from django.core.mail import send_mail
from django.conf import settings


def run():
    try:
        send_mail(
            "Subject here",
            "Here is the message.",
            settings.DEFAULT_FROM_EMAIL,
            ["iamneaz@outlook.com"],
            fail_silently=False,
        )
    except Exception as e:
        print(f"An error occurred while sending email: {e}")
