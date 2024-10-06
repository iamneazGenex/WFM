try:
    send_mail(
        "Subject here",
        "Here is the message.",
        settings.DEFAULT_FROM_EMAIL,
        ["alamin.neaz@genexinfosys.com"],
        fail_silently=False,
    )
except Exception as e:
    print(f"An error occurred while sending email: {e}")
