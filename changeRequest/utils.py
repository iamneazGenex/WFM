from .forms import SelectRequestee
from accounts.models import Employee, CustomUser, Supervisor
from roster.models import *
from django.contrib import messages
from django.db.models import Q
from datetime import timedelta
import datetime
import logging
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from rms.global_utilities import *

logger = logging.getLogger(__name__)

APPROVALSTATUS_CHOICES = (
    ("", "----"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
)


def getEmployee(id):
    user = CustomUser.objects.get(id=id)
    employee = Employee.objects.filter(user=user).first()
    return employee


def getSupervisor(id):
    user = CustomUser.objects.get(id=id)
    supervisor = Supervisor.objects.get(user=user)
    return supervisor


def dayCanBeSwaped(requestee, swapDateID, tradeDateID, request):
    """
    Check if day can be swaped
    """
    logger.info("Check if day can be swaped")
    result = False
    if swapDateID is not None and tradeDateID is not None:
        employeeSwapDate = Roster.objects.filter(id=swapDateID).first()
        #print(f"employeeSwapDate - {employeeSwapDate}")
        employeeTradeDate = Roster.objects.filter(id=tradeDateID).first()
        #print(f"employeeTradeDate - {employeeTradeDate}")
        if employeeSwapDate and employeeTradeDate:
            requesteeSwapDate = Roster.objects.filter(
                Q(employee=requestee),
                Q(start_date=employeeTradeDate.start_date),
                ~Q(start_time=None),
            )
            #print(f"requesteeSwapDate - {requesteeSwapDate}")
            requesteeTradeDate = Roster.objects.filter(
                Q(employee=requestee),
                Q(start_date=employeeSwapDate.start_date),
                Q(start_time=None),
            )
            #print(f"requesteeTradeDate - {requesteeTradeDate}")
            if requesteeSwapDate and requesteeTradeDate:
                result = True
            else:
                logger.error("Swap Date or Trade Date of Requestee does not exist")

        else:
            logger.error("Swap Date or Trade Date of Employee does not exist")
    else:
        logger.error("Swap Date or Trade Date of Employee is not given")
    return result


def gapInHours(endTime, startTime):
    hours = 0
    if endTime is not None and startTime is not None:
        delta = endTime - startTime
        seconds = delta.total_seconds()
        hours = seconds / (60 * 60)
    return hours


def gapCheck(roster, employee, workRule):
    """
    Checking if the given roster has gap regarding the work rule of its previous day and next day
    """
    logger.info("Gap Check of Roster {roster}".format(roster=roster))
    result = False
    firstGapCheck = False
    secondGapCheck = False

    try:
        dateRoster = roster
        previousDate = dateRoster.start_date - timedelta(days=1)
        nextDate = dateRoster.start_date + timedelta(days=1)
    except Exception as e:
        logger.error("Exception:{exception}".format(exception=e))

    if dateRoster.start_time is None:
        firstGapCheck = True
        secondGapCheck = True
    else:
        gap = None
        try:
            previousDateRoster = Roster.objects.get(
                employee=employee, start_date=previousDate
            )
        except Roster.DoesNotExist:
            previousDateRoster = None
        if previousDateRoster is not None and previousDateRoster.start_time is not None:
            previousDateRosterDateTime = datetime.datetime.combine(
                previousDateRoster.end_date, previousDateRoster.end_time
            )
            dateRosterDatetime = datetime.datetime.combine(
                dateRoster.start_date, dateRoster.start_time
            )
            # logger.info("dr{dr}".format(dr=dateRosterDatetime))
            # logger.info("pr{pr}".format(pr=previousDateRosterDateTime))
            gap = gapInHours(dateRosterDatetime, previousDateRosterDateTime)
            # logger.info("gap:{gap}".format(gap=gap))

            if gap >= workRule.gap_between_shift_end_to_the_next_shift_start_time:
                firstGapCheck = True
        else:
            firstGapCheck = True
        logger.info(
            "--First gap check--\n|Previous Roster| {previousRoster}\n|Current Roster|{currentRoster}\n|Gap| {gap}\n|Result| {result}".format(
                previousRoster=previousDateRoster,
                currentRoster=dateRoster,
                gap=gap,
                result=firstGapCheck,
            )
        )

        try:
            nextDateRoster = Roster.objects.get(employee=employee, start_date=nextDate)
        except Roster.DoesNotExist:
            nextDateRoster = None

        # logger.info(
        #     "Second gap check\n|Current| {currentRoster}\n|Next|{nextRoster}".format(
        #         nextRoster=nextDateRoster, currentRoster=dateRoster
        #     )
        # )

        if nextDateRoster is not None and nextDateRoster.start_time is not None:
            dateRosterDatetime = datetime.datetime.combine(
                dateRoster.end_date, dateRoster.end_time
            )
            nextDateRosterDatetime = datetime.datetime.combine(
                nextDateRoster.start_date, nextDateRoster.start_time
            )
            # logger.info("dr{dr}".format(dr=dateRosterDatetime))
            # logger.info("nr{nr}".format(nr=nextDateRosterDatetime))
            gap = gapInHours(nextDateRosterDatetime, dateRosterDatetime)
            # logger.info("gap:{gap}".format(gap=gap))
            if gap >= workRule.gap_between_shift_end_to_the_next_shift_start_time:
                secondGapCheck = True
        else:
            secondGapCheck = True
        logger.info(
            "--Second gap check--\n|Current Roster| {currentRoster}\n|Next Roster|{nextRoster}\n|Gap| {gap}\n|Result| {result}".format(
                nextRoster=nextDateRoster,
                currentRoster=dateRoster,
                gap=gap,
                result=secondGapCheck,
            )
        )
    if firstGapCheck is True and secondGapCheck is True:
        result = True
        logger.info("Gap exists")

    return result


def checkGapBetweenShiftEndToTheNextShiftStartTime(
    employee, requestee, swapDateID, tradeDateID, workRule, request
):
    """
    Check the gap between shift end to the next shift start time
    """
    logger.info(
        "Check the gap of Employee: {employeeName} between shift end time to the next shift start time".format(
            employeeName=employee.user.name
        )
    )
    result = False
    employeeGapCheck = False
    requesteeGapCheck = False

    if swapDateID is not None and tradeDateID is not None:
        swapDateRoster = Roster.objects.get(id=swapDateID)
        employeeGapCheck = gapCheck(
            roster=swapDateRoster, employee=employee, workRule=workRule
        )

        requesteeRoster = Roster.objects.get(
            employee=requestee, start_date=Roster.objects.get(id=tradeDateID).start_date
        )
        requesteeGapCheck = gapCheck(
            roster=requesteeRoster, employee=requestee, workRule=workRule
        )
        if employeeGapCheck is not True:
            logger.error(
                " Employee Gap Between Shift End To The Next Shift Start Time does not follow workrule",
            )
        if requesteeGapCheck is not True:
            logger.error(
                " Requestee Gap Between Shift End To The Next Shift Start Time does not follow workrule",
            )
        if employeeGapCheck is True and requesteeGapCheck is True:
            result = True
            logger.info(
                "Gap Between Shift End To The Next Shift Start Time FOLLOWS workrule"
            )
        else:
            logger.error(
                "Requestor Gap Between Shift End To The Next Shift Start Time does not follow workrule",
            )
    return result


def checkFemaleShiftTimeFollowsWorkRule(startTime, endTime, workRule, request):
    """
    Check if the female Shift time follows the work rule of female shift time
    """
    logger.info(
        "Check if the female Shift time follows the work rule of female shift time"
    )
    result = False

    workRuleStartDateTime = datetime.datetime.combine(
        datetime.date.today(), workRule.female_shift_start_time
    )
    workRuleEndDateTime = datetime.datetime.combine(
        datetime.date.today(), workRule.female_shift_end_time
    )
    rosterStartDateTime = datetime.datetime.combine(datetime.date.today(), startTime)
    rosterEndDateTime = datetime.datetime.combine(datetime.date.today(), endTime)
    if (
        rosterStartDateTime >= workRuleStartDateTime
        and rosterEndDateTime <= workRuleEndDateTime
    ):
        logger.info("Roster time follows female workrule")
        result = True
    else:
        logger.warning("Roster time DOES NOT follow female workrule")
    return result


def checkRegularShiftDuration(roster, workRule, request):
    """
    Check if a given roster have the regular shift duration of the workrule
    """
    logger.info(
        "Check if a given roster |{roster}| have the regular shift duration of the workrule".format(
            roster=roster
        )
    )
    result = False
    if roster.start_date and roster.start_time:
        rosterStartDateTime = datetime.datetime.combine(
            roster.start_date, roster.start_time
        )
        # Check if the end time is midnight
        if roster.end_time == datetime.time(0, 0, 0):
            # If so, increment the date by one day
            rosterEndDateTime = datetime.datetime.combine(
                roster.end_date + datetime.timedelta(days=1), roster.end_time
            )
        else:
            rosterEndDateTime = datetime.datetime.combine(
                roster.end_date, roster.end_time
            )

        #print(f"rosterStartDateTime : {rosterStartDateTime} | rosterEndDateTime: {rosterEndDateTime}")
        gap = gapInHours(rosterEndDateTime, rosterStartDateTime)
        #print("Shift Duration of roster : {duration}".format(duration=gap))
        if (
            gap <= workRule.maximum_regular_shift_duration
            and gap >= workRule.minimum_regular_shift_duration
        ):
            result = True
            logger.info("Roster follows regular shift duration")
        else:
            logger.warning("Roster DOES NOT follow regular shift duration")
    else:
        logger.warning(
            f"Roster date is {roster.start_date} Roster time is {roster.start_time}"
        )
    return result


def checkShiftEndInProhibitedTime(roster, workRule):
    """
    Check if the end time of a given roster ends between the prohibited time of the workrule
    """
    logger.info(
        "....Check if the end time of a given roster|{roster}| ends between the prohibited time of the workrule".format(
            roster=roster
        )
    )
    result = False
    #print(f"roster.end_time - {roster.end_time}")
    #print(f"prohibited_time_for_end_of_a_shift_start_time - {workRule.prohibited_time_for_end_of_a_shift_start_time}")
    #print(f"prohibited_time_for_end_of_a_shift_end_time - {workRule.prohibited_time_for_end_of_a_shift_end_time}")
    if (
        roster.end_time >= workRule.prohibited_time_for_end_of_a_shift_start_time
        and roster.end_time <= workRule.prohibited_time_for_end_of_a_shift_end_time
    ):
        result = True
        logger.warning("|Failed|Roster end time falls between the prohibited time")
    else:
        logger.info("|Passed|Roster end time DOES NOT fall between the prohibited time")
    return result


def sendEmail(subject, message, recipientList):
    """
    Send an email
    """
    logger.info(
        "Trying to send and email to {recipientList}".format(
            recipientList=",".join(recipientList)
        )
    )
    result = True
    emailFrom = settings.EMAIL_HOST_USER
    try:
        send_mail(subject, message, emailFrom, recipientList)
        logger.info("|Success| Email sent successfully")
    except Exception as e:
        result = False
        logger.error("|Failed| Exception:{exception}".format(exception=e))
    return result


def swapRosterTimes(roster1, roster2):
    """
    Swap the Time between two Roster
    """
    logger.info(
        "Trying to Swap the time between Roster1:{roster1} and Roster2:{roster2}".format(
            roster1=roster1, roster2=roster2
        )
    )
    result = False
    try:
        roster1StartTime = roster1.start_time
        roster1EndTime = roster1.end_time

        roster2StartTime = roster2.start_time
        roster2EndTime = roster2.end_time

        with transaction.atomic():
            roster2.start_time = roster1StartTime
            roster2.end_time = roster1EndTime
            roster2.save()
            roster1.start_time = roster2StartTime
            roster1.end_time = roster2EndTime
            roster1.save()
            result = True
            logger.info("Swapped successfully")
    except Exception as e:
        logger.error("Exception:{exception}".format(exception=e))

    return result


def checkConsecutiveWorkingDays(tradeRosterID, employee, workRule):
    """Checking if the given swap Roster follows the given work rule

    Args:
        tradeRosterID (Roster): The weekoff roster that the employee wants to trade
        employee (Employee): The current employee
        workRule (WorkRule): The current work rule instance
    Returns:
        boolean: True if the consecutiveWorkingDays is  less than or equal to consecutiveWorkingDays of workRule
        boolean: False if the consecutiveWorkingDays is  greater than consecutiveWorkingDays of workRule
    """
    result = False
    daysBeforeCheck = False
    roster = Roster.objects.get(id=tradeRosterID)
    consecutiveWorkingDays = workRule.consecutive_working_days
    logger.info(
        f"Checking Consecutive Working Days ({consecutiveWorkingDays}) of Roster(id:{roster.id}) |{roster}|"
    )
    try:
        daysBefore = roster.start_date - timedelta(days=consecutiveWorkingDays)

        rostersBeforeStartDate = Roster.objects.filter(
            employee=employee,
            start_date__gte=daysBefore,
            start_date__lt=roster.start_date,
        ).order_by("-start_date")

        # Count consecutive records until a None is found in start_time
        consecutiveCount = 1
        for filteredRoster in rostersBeforeStartDate:
            if filteredRoster.start_time is not None:
                consecutiveCount += 1
            else:
                # Break the loop when None is found in start_time
                break

        if consecutiveCount <= consecutiveWorkingDays:
            logger.info(
                f"--Days Before Check-- consecutiveCount({consecutiveCount}) is  less than or equal to consecutiveWorkingDays "
            )
            daysAfter = roster.start_date + timedelta(
                days=workRule.consecutive_working_days
            )
            rostersAfterStartDate = Roster.objects.filter(
                employee=employee,
                start_date__gt=roster.start_date,
                start_date__lte=daysAfter,
            ).order_by("start_date")
            # Count consecutive records until a None is found in start_time
            for filteredRoster in rostersAfterStartDate:
                if filteredRoster.start_time is not None:
                    consecutiveCount += 1
                else:
                    # Break the loop when None is found in start_time
                    break
            if consecutiveCount <= consecutiveWorkingDays:
                logger.info(
                    f"--Days After Check-- consecutiveCount({consecutiveCount}) is  less than or equal to consecutiveWorkingDays "
                )
                result = True
            else:
                logger.info(
                    f"--Days After Check-- consecutiveCount({consecutiveCount}) is  greater than consecutiveWorkingDays "
                )
        else:
            logger.info(
                f"--Days Before Check-- consecutiveCount({consecutiveCount}) is  greater than consecutiveWorkingDays "
            )
    except Exception as e:
        logger.error("Exception:{exception}".format(exception=e))
    logger.info(f"--Result-- {result} ")
    return result


def checkMaxCountInAParticularInterval(
    requestor, requestorSwapRoster, requestee, requesteeSwapRoster, workRule
):
    result = False

    requestorCalculatedRosterCount = RosterCount.objects.get(
        site=requestor.site,
        process=requestor.process,
        lob=requestor.lob,
        workRole=requestor.work_role,
        start_date=requestorSwapRoster.start_date,
        start_time=requestorSwapRoster.start_time,
        end_date=requestorSwapRoster.end_date,
        end_time=requestorSwapRoster.end_time,
    ).count

    rosterSeatCount = RosterSeatCount.objects.get(
        site=requestor.site, process=requestor.process, lob=requestor.lob
    ).total
    requesteeCalculatedRosterCount = RosterCount.objects.get(
        site=requestee.site,
        process=requestee.process,
        lob=requestee.lob,
        workRole=requestee.work_role,
        start_date=requesteeSwapRoster.start_date,
        start_time=requesteeSwapRoster.start_time,
        end_date=requesteeSwapRoster.end_date,
        end_time=requesteeSwapRoster.end_time,
    ).count

    #print(requestorCalculatedRosterCount, rosterSeatCount, requesteeCalculatedRosterCount)
