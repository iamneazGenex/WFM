from django.test import TestCase
from accounts.models import *
from roster.models import *
from reporting.utils import *
import datetime

# Create your tests here.


def runtest():
    skill = Skill.objects.get(name="premium")
    process = Process.objects.get(name="gp")
    lob = LOB.objects.get(name="premium")
    month = 1
    year = 2024
    date = datetime.datetime(2024, 1, 8)
    agentHourlyPerformanceMapping = getAvayaCDRMappingByMonth(
        month=1, year=2024, skill=skill
    )
    print(agentHourlyPerformanceMapping["2024-29-01"]["offeredCalls"])
    print(agentHourlyPerformanceMapping)
