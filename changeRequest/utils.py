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
import pprint

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


def dayCanBeSwaped(requestee, swapDateID, tradeDateID):
    """
    Check if day can be swaped
    """
    logger.info("Check if day can be swaped")
    result = False
    error_message = []
    try:
        if swapDateID is None or tradeDateID is None:
            message = "Swap Date or Trade Date of Employee is not given"
            logger.error(message)
            error_message.append(message)
            return result, "\n".join(error_message)

        requestorSwapDate = Roster.objects.get(id=swapDateID)
        requestorTradeDate = Roster.objects.get(id=tradeDateID)

        if not requestorSwapDate or not requestorTradeDate:
            raise ValueError("Swap Date or Trade Date of Employee does not exist")

        requesteeSwapDate_exists = Roster.objects.filter(
            employee=requestee,
            start_date=requestorTradeDate.start_date,
            start_time__isnull=False,
        ).exists()

        requesteeTradeDate_exists = Roster.objects.filter(
            employee=requestee,
            start_date=requestorSwapDate.start_date,
            start_time__isnull=True,
        ).exists()

        if requesteeSwapDate_exists:
            result = True
        else:
            message = f"Swap Date of {requestee.user.name} does not exist"
            error_message.append(message)
            logger.error(message)

        if requesteeTradeDate_exists:
            result = True
        else:
            result = False
            message = f"Trade Date of {requestee.user.name} does not exist"
            error_message.append(message)
            logger.error(message)
    except ValueError as e:
        result = False
        logger.error(f"Value Error:{e}")
        error_message.append(f"{e}")
    except Exception as e:
        result = False
        logger.error(f"Exception:{e}")
        error_message.append("Function Error")
    return result, "\n".join(error_message)


def gapInHours(endTime, startTime):
    hours = 0
    if endTime is not None and startTime is not None:
        delta = endTime - startTime
        seconds = delta.total_seconds()
        hours = seconds / (60 * 60)
    return hours


def gapCheck(roster, employee, workRule):
    """
    Checking if the given roster has a gap regarding the work rule of its previous day and next day.

    Args:
        roster (Roster): The current roster instance to check.
        employee (Employee): The employee whose roster is being checked.
        workRule (WorkRule): The work rule instance containing the gap criteria.

    Returns:
        bool: True if the roster gap adheres to the work rule, False otherwise.
    """
    logger.info(f"Gap Check of Roster {roster}")
    result = False
    firstGapCheck = False
    secondGapCheck = False
    error_messages = []

    if roster is None:
        error_messages.append("Roster is None")
    if employee is None:
        error_messages.append("Employee is None")
    if workRule is None:
        error_messages.append("WorkRule is None")

    if error_messages:
        logger.error(", ".join(error_messages))
        return result

    try:
        dateRoster = roster
        previousDate = dateRoster.start_date - timedelta(days=1)
        nextDate = dateRoster.start_date + timedelta(days=1)

        if dateRoster.start_time is None:
            # If the current roster's start time is None, we assume it passes both gap checks
            firstGapCheck = True
            secondGapCheck = True
        else:
            # Check gap with the previous day's roster
            try:
                previousDateRoster = Roster.objects.get(
                    employee=employee, start_date=previousDate
                )
            except Roster.DoesNotExist:
                previousDateRoster = None

            if previousDateRoster and previousDateRoster.start_time:
                previousDateRosterDateTime = datetime.datetime.combine(
                    previousDateRoster.end_date, previousDateRoster.end_time
                )
                dateRosterDatetime = datetime.datetime.combine(
                    dateRoster.start_date, dateRoster.start_time
                )
                gap = gapInHours(dateRosterDatetime, previousDateRosterDateTime)
                firstGapCheck = (
                    gap >= workRule.gap_between_shift_end_to_the_next_shift_start_time
                )
            else:
                firstGapCheck = True

            logger.info(
                f"--First gap check--\n"
                f"|Previous Roster| {previousDateRoster}\n"
                f"|Current Roster| {dateRoster}\n"
                f"|Gap| {gap if previousDateRoster else 'N/A'}\n"
                f"|Result| {firstGapCheck}"
            )

            # Check gap with the next day's roster
            nextDateRoster = Roster.objects.filter(
                employee=employee, start_date=nextDate
            ).first()
            if nextDateRoster and nextDateRoster.start_time:
                dateRosterDatetime = datetime.datetime.combine(
                    dateRoster.end_date, dateRoster.end_time
                )
                nextDateRosterDatetime = datetime.datetime.combine(
                    nextDateRoster.start_date, nextDateRoster.start_time
                )
                gap = gapInHours(nextDateRosterDatetime, dateRosterDatetime)
                secondGapCheck = (
                    gap >= workRule.gap_between_shift_end_to_the_next_shift_start_time
                )
            else:
                secondGapCheck = True

            logger.info(
                f"--Second gap check--\n"
                f"|Current Roster| {dateRoster}\n"
                f"|Next Roster| {nextDateRoster}\n"
                f"|Gap| {gap if nextDateRoster else 'N/A'}\n"
                f"|Result| {secondGapCheck}"
            )

        result = firstGapCheck and secondGapCheck

    except Exception as e:
        logger.error(f"Exception occurred during gap check: {e}")

    if result:
        logger.info("Gap exists between shifts according to the work rule")
    else:
        logger.error("Gap does not exist between shifts according to the work rule")

    return result


def checkGapBetweenShiftEndToTheNextShiftStartTime(
    requestor, requestee, swapDateID, tradeDateID, workRule
):
    """
    Check the gap between shift end to the next shift start time
    """
    logger.info(
        "Check the gap of Employee: {requestorName} between shift end time to the next shift start time".format(
            requestorName=requestor.user.name
        )
    )
    result = False
    requestorGapCheck = False
    requesteeGapCheck = False
    error_messages = []

    try:
        if swapDateID is None:
            raise ValueError("Swap Date is not provided")
        if tradeDateID is None:
            raise ValueError("Trade Date ID is not provided")

        # Get the rosters
        swapDateRoster = Roster.objects.get(id=swapDateID)
        tradeDateRoster = Roster.objects.get(id=tradeDateID)

        # Check gap for requestor
        requestorGapCheck = gapCheck(
            roster=swapDateRoster, employee=requestor, workRule=workRule
        )
        if not requestorGapCheck:
            error_message = "Employee gap between shift end to the next shift start time does not follow work rule"
            logger.error(error_message)
            error_messages.append(error_message)

        # Check gap for requestee
        requesteeRoster = Roster.objects.get(
            employee=requestee, start_date=tradeDateRoster.start_date
        )
        requesteeGapCheck = gapCheck(
            roster=requesteeRoster, employee=requestee, workRule=workRule
        )
        if not requesteeGapCheck:
            error_message = "Requestee gap between shift end to the next shift start time does not follow work rule"
            logger.error(error_message)
            error_messages.append(error_message)

        # Final result check
        if requestorGapCheck and requesteeGapCheck:
            result = True
            logger.info(
                "Gap between shift end to the next shift start time follows work rule for both requestor and requestee"
            )
        else:
            error_message = "Gap between shift end to the next shift start time does not follow work rule for either requestor or requestee"
            logger.error(error_message)
            error_messages.append(error_message)

    except Roster.DoesNotExist as e:
        error_message = f"Roster not found: {e}"
        logger.error(error_message)
        error_messages.append(error_message)
    except ValueError as ve:
        error_message = str(ve)
        logger.error(error_message)
        error_messages.append(error_message)
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        logger.error(error_message)
        error_messages.append(error_message)

    return result, "\n".join(error_messages)


def checkFemaleShiftTimeFollowsWorkRule(startTime, endTime, workRule):
    """
    Check if the female shift time follows the work rule of female shift time.

    Args:
        startTime (datetime.time): The start time of the shift.
        endTime (datetime.time): The end time of the shift.
        workRule (WorkRule): The work rule instance containing the shift time criteria.
        request (Request): The request instance (if any).

    Returns:
        tuple: (bool, str) A tuple containing a boolean indicating if the shift time adheres to the work rule and a string of error messages (if any).
    """
    logger.info(
        "Check if the female Shift time follows the work rule of female shift time"
    )
    result = False
    error_messages = []

    # Validate inputs
    if startTime is None:
        error_messages.append("Start time is None")
    if endTime is None:
        error_messages.append("End time is None")
    if workRule is None:
        error_messages.append("WorkRule is None")

    if error_messages:
        error_message_str = ", ".join(error_messages)
        logger.error(error_message_str)
        return result, error_message_str

    try:
        workRuleStartDateTime = datetime.datetime.combine(
            datetime.date.today(), workRule.female_shift_start_time
        )
        workRuleEndDateTime = datetime.datetime.combine(
            datetime.date.today(), workRule.female_shift_end_time
        )
        rosterStartDateTime = datetime.datetime.combine(
            datetime.date.today(), startTime
        )
        rosterEndDateTime = datetime.datetime.combine(datetime.date.today(), endTime)

        if (
            rosterStartDateTime >= workRuleStartDateTime
            and rosterEndDateTime <= workRuleEndDateTime
        ):
            logger.info("Roster time follows female work rule")
            result = True
        else:
            error_message = "Roster time DOES NOT follow female work rule"
            logger.warning(error_message)
            error_messages.append(error_message)

    except Exception as e:
        error_message = f"Exception occurred during shift time check: {e}"
        logger.error(error_message)
        error_messages.append(error_message)

    error_message_string = ", ".join(error_messages)
    return result, error_message_string


def checkFemaleShiftTimeFollowsWorkRuleOLD(startTime, endTime, workRule, request):
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


def checkRegularShiftDuration(roster, workRule):
    """
    Check if a given roster has the regular shift duration of the work rule.

    Args:
        roster (Roster): The roster instance to check.
        workRule (WorkRule): The work rule instance containing the shift duration criteria.

    Returns:
        tuple: (bool, str) A tuple containing a boolean indicating if the shift duration adheres to the work rule and a string of error messages (if any).
    """
    logger.info(
        "Check if a given roster |{roster}| has the regular shift duration of the work rule".format(
            roster=roster
        )
    )
    result = False
    error_messages = []

    # Validate inputs
    if roster is None:
        error_messages.append("Roster is None")
    if workRule is None:
        error_messages.append("WorkRule is None")

    if error_messages:
        error_message_str = ", ".join(error_messages)
        logger.error(error_message_str)
        return result, error_message_str

    try:
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

            gap = gapInHours(rosterEndDateTime, rosterStartDateTime)

            if (
                gap <= workRule.maximum_regular_shift_duration
                and gap >= workRule.minimum_regular_shift_duration
            ):
                result = True
                logger.info("Roster follows regular shift duration")
            else:
                error_message = "Roster DOES NOT follow regular shift duration"
                logger.warning(error_message)
                error_messages.append(error_message)
        else:
            error_message = f"Roster date is {roster.start_date}, Roster time is {roster.start_time}"
            logger.warning(error_message)
            error_messages.append(error_message)

    except Exception as e:
        error_message = f"Exception occurred during shift duration check: {e}"
        logger.error(error_message)
        error_messages.append(error_message)

    error_message_str = ", ".join(error_messages)
    return result, error_message_str


def checkRegularShiftDurationOLD(roster, workRule):
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

        # print(f"rosterStartDateTime : {rosterStartDateTime} | rosterEndDateTime: {rosterEndDateTime}")
        gap = gapInHours(rosterEndDateTime, rosterStartDateTime)
        # print("Shift Duration of roster : {duration}".format(duration=gap))
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
    Check if the end time of a given roster ends between the prohibited time of the work rule.

    Args:
        roster (Roster): The roster instance to check.
        workRule (WorkRule): The work rule instance containing the prohibited time criteria.

    Returns:
        tuple: (bool, str) A tuple containing a boolean indicating if the roster end time falls within the prohibited time and a string of error messages (if any).
    """
    logger.info(
        "Check if the end time of a given roster |{roster}| ends between the prohibited time of the work rule".format(
            roster=roster
        )
    )
    result = False
    error_messages = []

    # Validate inputs
    if roster is None:
        error_messages.append("Roster is None")
    if workRule is None:
        error_messages.append("WorkRule is None")

    if error_messages:
        error_message_str = ", ".join(error_messages)
        logger.error(error_message_str)
        return result, error_message_str

    try:
        if (
            roster.end_time >= workRule.prohibited_time_for_end_of_a_shift_start_time
            and roster.end_time <= workRule.prohibited_time_for_end_of_a_shift_end_time
        ):
            result = True
            warning_message = "Roster end time falls between the prohibited time"
            logger.warning(f"|Failed| {warning_message}")
            error_messages.append(warning_message)
        else:
            logger.info(
                "|Passed| Roster end time DOES NOT fall between the prohibited time"
            )

    except Exception as e:
        error_message = f"Exception occurred during shift end time check: {e}"
        logger.error(error_message)
        error_messages.append(error_message)

    error_message_str = ", ".join(error_messages)
    return result, error_message_str


def checkShiftEndInProhibitedTimeOLD(roster, workRule):
    """
    Check if the end time of a given roster ends between the prohibited time of the workrule
    """
    logger.info(
        "....Check if the end time of a given roster|{roster}| ends between the prohibited time of the workrule".format(
            roster=roster
        )
    )
    result = False

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


def checkConsecutiveWorkingDays(swapRosterID, tradeRosterID, employee, workRule):
    """Checking if the given swap Roster follows the given work rule

    Args:
        tradeRosterID (int): The ID of the trade roster
        swapRosterID (int): The ID of the swap roster
        employee (Employee): The current employee
        workRule (WorkRule): The current work rule instance
    Returns:
        tuple: (boolean, str) True if the consecutive working days is less than or equal to workRule's limit, False otherwise.
        str contains error message if any.
    """
    result = False
    error_messages = []
    try:
        # Retrieve the rosters
        trade_roster = Roster.objects.get(id=tradeRosterID)
        swap_roster = Roster.objects.get(id=swapRosterID)
        consecutiveWorkingDays = workRule.consecutive_working_days
        logging.info(
            f"Checking Consecutive Working Days ({consecutiveWorkingDays}) for Employee(id:{employee.id})"
        )

        # Create a combined list of dates to check
        daysBefore = min(trade_roster.start_date, swap_roster.start_date) - timedelta(
            days=consecutiveWorkingDays
        )
        daysAfter = max(trade_roster.end_date, swap_roster.end_date) + timedelta(
            days=consecutiveWorkingDays
        )

        # Fetch rosters in the specified range
        rosters = Roster.objects.filter(
            employee=employee,
            start_date__range=(daysBefore, daysAfter),
        ).order_by("start_date")

        # Initialize a data structure to store the rosters with dates and times
        roster_dates = []
        for r in rosters:
            if (
                r.start_date != trade_roster.start_date
                and r.start_date != swap_roster.start_date
            ):
                roster_dates.append(
                    {
                        "start_date": r.start_date,
                        "end_date": r.end_date,
                        "start_time": r.start_time,
                        "end_time": r.end_time,
                    }
                )

        # Include the trade and swap rosters in the data structure
        roster_dates.append(
            {
                "start_date": trade_roster.start_date,
                "end_date": trade_roster.end_date,
                "start_time": swap_roster.start_time,
                "end_time": swap_roster.end_time,
            }
        )
        roster_dates.append(
            {
                "start_date": swap_roster.start_date,
                "end_date": swap_roster.end_date,
                "start_time": trade_roster.start_time,
                "end_time": trade_roster.end_time,
            }
        )

        # Sort rosters by start date
        roster_dates.sort(key=lambda x: x["start_date"])
        # Track consecutive working days
        consecutiveCount = 0
        previous_end_date = None

        for roster in roster_dates:
            if (
                previous_end_date
                and (roster["start_date"] - previous_end_date).days > 1
            ):
                # Gap found, reset count
                consecutiveCount = 0

            if roster["start_time"] is not None and roster["end_time"] is not None:
                consecutiveCount += 1
                previous_end_date = roster["end_date"]
            else:
                # Break on any roster without a start or end time
                consecutiveCount = 0
                break

            if consecutiveCount > consecutiveWorkingDays:
                message = f"Consecutive working days ({consecutiveCount}) exceed the limit ({consecutiveWorkingDays})"
                logging.info(message)
                error_messages.append(message)
                return False, "\n".join(error_messages)

        result = True if consecutiveCount < consecutiveWorkingDays else False

    except Roster.DoesNotExist:
        error_message = f"One of the rosters with IDs {tradeRosterID} or {swapRosterID} does not exist: {e}"
        logging.error(error_message)
        error_messages.append(error_message)
    except Exception as e:
        error_message = f"Exception: {e}"
        logging.error(error_message)
        error_messages.append("Exception occurred")

    logging.info(f"Consecutive working days check result: {result}")
    return result, "\n".join(error_messages)


def checkConsecutiveWorkingDaysGPT(swapRosterID, tradeRosterID, employee, workRule):
    """Checking if the given swap Roster follows the given work rule

    Args:
        tradeRosterID (int): The ID of the roster that the employee wants to trade
        employee (Employee): The current employee
        workRule (WorkRule): The current work rule instance
    Returns:
        bool: True if the consecutive working days is less than or equal to workRule's limit, False otherwise
    """
    result = False
    tradeRoster = Roster.objects.get(id=tradeRosterID)
    consecutiveWorkingDays = workRule.consecutive_working_days
    logging.info(
        f"Checking Consecutive Working Days ({consecutiveWorkingDays}) of Roster(id:{tradeRoster.id}) |{tradeRoster}|"
    )

    try:
        # Date range before and after the current roster start date
        daysBefore = tradeRoster.start_date - timedelta(days=consecutiveWorkingDays)
        daysAfter = tradeRoster.start_date + timedelta(days=consecutiveWorkingDays)

        # Fetch tradeRosters in the specified range, including current tradeRoster
        tradeRosters = Roster.objects.filter(
            employee=employee,
            start_date__range=(daysBefore, daysAfter),
        ).order_by("start_date")

        # Track consecutive working days
        consecutiveCount = 0
        previous_end_date = None

        for tradeRoster in tradeRosters:
            logger.info(f"Processing tradeRoster: {tradeRoster}")

            if previous_end_date:
                gap_days = (tradeRoster.start_date - previous_end_date).days
                logger.info(
                    f"Previous end date: {previous_end_date}, Current start date: {tradeRoster.start_date}, Gap days: {gap_days}"
                )
                if gap_days > 1:
                    logger.info("Gap found, resetting consecutive count")
                    consecutiveCount = 0

            if tradeRoster.start_time is not None and tradeRoster.end_time is not None:
                consecutiveCount += 1
                previous_end_date = tradeRoster.end_date
                logger.info(
                    f"Roster has valid start and end times. Consecutive count: {consecutiveCount}"
                )
            else:
                logger.info(
                    "Roster missing start or end time, resetting consecutive count and breaking loop"
                )
                consecutiveCount = 0
                break

            if consecutiveCount > consecutiveWorkingDays:
                logger.info(
                    f"Consecutive working days ({consecutiveCount}) exceed the limit ({consecutiveWorkingDays})"
                )
                return False

        result = True if consecutiveCount <= consecutiveWorkingDays else False

    except Roster.DoesNotExist:
        logging.error("Roster with ID {tradeRosterID} does not exist.")
    except Exception as e:
        logging.error(f"Exception: {e}")

    logging.info(f"Consecutive working days check result: {result}")
    return result


def checkConsecutiveWorkingDaysOLD(tradeRosterID, employee, workRule):
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

    # print(requestorCalculatedRosterCount, rosterSeatCount, requesteeCalculatedRosterCount)
