from django.test import TestCase
from accounts.models import *
from roster.models import *
from reporting.utils import *
import datetime
import pprint
import smtplib
import base64
from rms.global_utilities import *
import time

# Create your tests here.


def runtest():
    skill = Skill.objects.get(id=20)
    intervalType = "month"
    monthString = "2024-03"
    year, month = map(int, monthString.split("-"))
    tableData = []
    if intervalType == "date":
        tableData = generate_hour_table_data()
    else:
        tableData = generate_date_table_data(month, year)
    forecast_mapping = {}
    if skill.name == "premium" or skill.name == "medium":
        process = Process.objects.get(name="gp")
        lob = LOB.objects.get(name="premium" if skill.name == "premium" else "mass")
        # Create a mapping of intervals to corresponding forecasts and required_hc
        forecasts = (
            Forecast.objects.filter(date__month=month, process=process, lob=lob)
            .values("date")
            .annotate(
                forecast=Sum("forecast"),
                required_hc=Sum("required_hc"),
            )
        )
        for f in forecasts:
            pass
            # print(f)
        # print("\n================================")
        forecast_mapping = {}
        for f in forecasts:
            formatted_date = f["date"].strftime("%Y-%m-%d")
            forecast_mapping[formatted_date] = (f["forecast"], f["required_hc"])

    avayaCDRMapping = getAvayaCDRMappingByMonth(month=month, year=year, skill=skill)

    # --------- Agent Hourly Performance Mapping

    agentHourlyPerformanceMapping = (
        getAgentHourlyPerformanceMappingWithRosterByMonthTest(
            month=month, year=year, skill=skill
        )
    )
    pprint.pprint(agentHourlyPerformanceMapping)


def getAgentHourlyPerformanceMappingWithRosterByMonthTest(month, year, skill):
    """Get Agent Hourly Performance Mapping

    Args:
        month (int): month
        year (int): year
        skill (Skill): selected skill

    Returns:
        dict: Agent Hourly Performance Mapping
    """
    agentHourlyPerformanceMapping = {}
    # if hour == 1:
    #     #print(f"Hour - {hour}")

    # Filter agentHourlyPerformances for the current hour
    # Fetch related ShiftLegend objects
    tableData = generate_date_table_data(month, year)
    for item in tableData:
        date = item["date"]
        shiftCount = 0
        absent = 0
        try:
            agentHourlyPerformances = AgentHourlyPerformance.objects.filter(
                date=date, skill=skill
            ).select_related("roster__shiftLegend")
            unique_roster_ids = agentHourlyPerformances.values_list(
                "roster_id", flat=True
            ).distinct()

            for item in unique_roster_ids:
                if item:
                    roster = Roster.objects.get(id=item)
                    shiftCount += roster.shiftLegend.shift_count
                    absent += roster.is_absent

            agentHourlyPerformanceMapping[date] = {
                "shiftCount": shiftCount,
                "absent": absent,
            }
        except Exception as e:
            agentHourlyPerformanceMapping[date] = {
                "shiftCount": 0,
                "absent": 0,
            }

    return agentHourlyPerformanceMapping


from exchangelib import DELEGATE, Account, Credentials, Configuration
import requests


def runSMTPTest():
    email_address = "wfm.notification@genexsvc.com"
    email_password = "Genex@4312#$"
    smtp_server = "172.23.28.31"  # Use the FQDN from the debug output

    try:
        credentials = Credentials(email_address, email_password)
        config = Configuration(server=smtp_server, credentials=credentials)
        account = Account(
            primary_smtp_address=email_address,
            config=config,
            autodiscover=False,
            access_type=DELEGATE,
        )

        print("Authentication successful")

        # Optional: Try to access the inbox to confirm the connection
        inbox = account.inbox
        print(f"Inbox folder name: {inbox.name}")

    except Exception as e:
        print(f"An error occurred: {e}")
    # email_address = "your_email@example.com"
    # email_password = "your_password"

    # encoded_email = base64.b64encode(email_address.encode()).decode()
    # encoded_password = base64.b64encode(email_password.encode()).decode()

    # print(f"Encoded email: {encoded_email}")
    # print(f"Encoded password: {encoded_password}")


from django.core.mail import send_mail
from django.conf import settings


def send_email(subject, message, recipient_list):
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"An error occurred while sending email: {e}")
        return False


# send_email("TEST Subject", "Test Message", ["m.nizam@genexsvc.com"])


# send_email_ntlm(
#     f"TEST Subject - {time.time()}",
#     "Test Message",
#     ["alamin.neaz@genexinfosys.com"],
# )

from django.core.mail import send_mail

# send_mail(
#     "Subject here",
#     "Here is the message.",
#     "wfm.notification@genexsvc.com",
#     ["alamin.neaz@genexinfosys.com"],
#     fail_silently=False,
# )
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
