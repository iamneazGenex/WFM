from django.shortcuts import render, redirect
from .forms import *
from accounts.models import Employee, CustomUser
from roster.models import *
from django.contrib import messages
from .utils import *
from .models import DayOffTrading, ShiftTimeTrading
from django.db.models import Q
from .tables import *
import django_tables2 as tables
import logging
import datetime
from datetime import datetime, timezone
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.http import JsonResponse
from rms.global_utilities import *
from rms.page_info_collection import PageInfoCollection
from django.contrib.auth.decorators import login_required
from rms.constants import GroupEnum
from rms.decorators import check_user_able_to_see_page
from django.conf import settings

logger = logging.getLogger(__name__)

# Create your views here.
################################################################
#   Day Off Trading
################################################################


@login_required(login_url="/login/")
@check_user_able_to_see_page(
    GroupEnum.wfm, GroupEnum.supervisor, GroupEnum.employee, GroupEnum.mis_group_1
)
def viewDayOffTradingRequests(request):
    template = "changeRequest/dayOffTrading/view.html"
    breadCrumbList = [
        PageInfoCollection.DAYOFFTRADING_VIEW,
    ]
    context = {
        "breadCrumbList": breadCrumbList,
        "currentBreadCrumb": PageInfoCollection.DAYOFFTRADING_VIEW.pageName,
        "details": {
            "name": "delete",
            "type": "process",
        },
        "ajaxUrl": PageInfoCollection.DAYOFFTRADING_JSON.urlName,
        "createUrl": PageInfoCollection.DAYOFFTRADING_CREATE.urlName,
        "dayOffTradingActive": "active",
    }
    return render(request, template, context)


@login_required(login_url="/login/")
@check_user_able_to_see_page(GroupEnum.wfm, GroupEnum.supervisor, GroupEnum.employee)
def createDayOffTrading(request):
    template = "changeRequest/dayOffTrading/create.html"
    breadCrumbList = [
        PageInfoCollection.DAYOFFTRADING_VIEW,
        PageInfoCollection.DAYOFFTRADING_CREATE,
    ]
    requestor = getEmployee(request.user.id)
    context = {
        "breadCrumbList": breadCrumbList,
        "currentBreadCrumb": PageInfoCollection.DAYOFFTRADING_CREATE.pageName,
        "details": {
            "name": "delete",
            "type": "process",
        },
        "ajaxUrl": PageInfoCollection.PROCESS_JSON.urlName,
        "createUrl": PageInfoCollection.DAYOFFTRADING_CREATE.urlName,
        "dayOffTradingActive": "active",
    }
    if request.method == "POST" and "btnform1" in request.POST:
        logging.info(logString("Day Off Trading", 1))
        swapDateID = int(request.POST.get("swapDate"))
        tradeDateID = int(request.POST.get("tradeDate"))
        requesteeID = int(request.POST.get("requestee"))

        form1 = DayOffTradingForm(
            employee=requestor,
            swapDateID=swapDateID,
            tradeDateID=tradeDateID,
            requesteeID=requesteeID,
        )
        context["form1"] = form1
        #   WORKRULE
        try:
            workRule = WorkRule.objects.get(id=1)
            logging.info(logString("WorkRule exists", 3))
        except WorkRule.DoesNotExist:
            workRule = None
            logging.error(logString("WorkRule does not exist", 5))
            messages.error(request, "WorkRule does not exist")
            return render(request, template, context)
        #   REQUESTEE
        try:
            requestee = Employee.objects.get(id=requesteeID)
        except Employee.DoesNotExist:
            logging.error(
                logString(f"Employee with ID {requesteeID} does not exist", 5)
            )
            messages.error(request, "Requestee does not exist")
            return render(request, template, context)
        #   REQUESTOR SWAP DAY
        try:
            requestorSwapDayRoster = Roster.objects.get(id=swapDateID)
        except Roster.DoesNotExist:
            logging.error(
                logString(
                    f"RequestorSwapDayRoster with ID {swapDateID} does not exist", 5
                )
            )
            messages.error(request, "Requestor Swap Roster does not exist")
            return render(request, template, context)
        #   REQUESTOR TRADE DAY
        try:
            requestorTradeDayRoster = Roster.objects.get(id=tradeDateID)
        except Roster.DoesNotExist:
            logging.error(
                logString(
                    f"RequestorTradeDayRoster with ID {tradeDateID} does not exist", 5
                )
            )
            messages.error(request, "Requestor Trade Roster does not exist")
            return render(request, template, context)
        #   REQUESTEE SWAP DAY
        try:
            requesteeSwapDayRoster = Roster.objects.get(
                employee=requestee, start_date=requestorTradeDayRoster.start_date
            )
        except Roster.DoesNotExist:
            logging.error(
                logString(
                    f"RequesteeSwapDayRoster with ID {swapDateID} does not exist", 5
                )
            )
            messages.error(request, "Requestee Swap Roster does not exist")
            return render(request, template, context)
        #   REQUESTEE TRADE DAY
        try:
            requesteeTradeDayRoster = Roster.objects.get(
                employee=requestee, start_date=requestorSwapDayRoster.start_date
            )
        except Roster.DoesNotExist:
            logging.error(
                logString(
                    f"RequesteeTradeDayRoster with ID {swapDateID} does not exist", 5
                )
            )
            messages.error(request, "Requestee Trade Roster does not exist")
            return render(request, template, context)

        logging.info(f"--Requestor:{requestor} |id:{requestor.id}|")
        logging.info(
            f"--Requestor Swap Day Roster:{requestorSwapDayRoster} |id:{requestorSwapDayRoster.id}|"
        )
        logging.info(
            f"--Requestor Trade Day Roster:{requestorTradeDayRoster} |id:{requestorTradeDayRoster.id}|"
        )
        logging.info(f"--Requestee:{requestee} |id:{requestee.id}|")
        logging.info(
            f"--Requestee Swap Day Roster:{requesteeSwapDayRoster} |id:{requesteeSwapDayRoster.id}|"
        )
        logging.info(
            f"--Requestee Trade Day Roster:{requesteeTradeDayRoster} |id:{requesteeTradeDayRoster.id}|"
        )

        ###########################
        ##  Checking Business rules
        ###########################
        # checkMaxCountInAParticularInterval(
        #     requestor=employee,
        #     requestorSwapRoster=requestorSwapDayRoster,
        #     requestee=requestee,
        #     requesteeSwapRoster=requesteeSwapDayRoster,
        #     workRule=workRule,
        # )
        ##########################
        # Consecutive Working Days for REQUESTOR
        logging.info(logString("Consecutive Working Days", 2))

        (
            requestorConsecutiveWorkingDaysResult,
            requestorConsecutiveWorkingDayError,
        ) = checkConsecutiveWorkingDays(
            swapRosterID=swapDateID,
            tradeRosterID=tradeDateID,
            employee=requestor,
            workRule=workRule,
        )

        if not requestorConsecutiveWorkingDaysResult:
            error_message = f"Requestor consecutive working days check failed: {requestorConsecutiveWorkingDayError}"
            logging.error(error_message)
            messages.error(request, requestorConsecutiveWorkingDayError)
            return render(request, template, context)
        ################################
        # Consecutive Working Days for REQUESTEE
        (
            requesteeConsecutiveWorkingDaysResult,
            requesteeConsecutiveWorkingDayError,
        ) = checkConsecutiveWorkingDays(
            swapRosterID=requesteeSwapDayRoster.id,
            tradeRosterID=requesteeTradeDayRoster.id,
            employee=requestee,
            workRule=workRule,
        )
        if not requesteeConsecutiveWorkingDaysResult:
            error_message = f"Requestee consecutive working days check failed: {requesteeConsecutiveWorkingDayError}"
            logging.error(error_message)
            messages.error(request, requesteeConsecutiveWorkingDayError)
            return render(request, template, context)
        ################################
        # Day Swap
        dayCanBeSwapedResult, dayCanBeSwapedError = dayCanBeSwaped(
            requestee=requestee,
            swapDateID=swapDateID,
            tradeDateID=tradeDateID,
        )
        if not dayCanBeSwapedResult:
            logging.error(logString("Days can be swapped", 4))
            messages.error(request, dayCanBeSwapedError)
            return render(request, template, context)

        ####################################################
        # Gap between shift end to the next shift start time
        logging.info(logString("Gap Check", 2))
        gapCheckingResult, gapCheckingError = (
            checkGapBetweenShiftEndToTheNextShiftStartTime(
                requestor=requestor,
                requestee=requestee,
                swapDateID=swapDateID,
                tradeDateID=tradeDateID,
                workRule=workRule,
            )
        )
        if not gapCheckingResult:
            logging.error(f"Gap Checking failed: {gapCheckingError}")
            messages.error(request, gapCheckingError)
            return render(request, template, context)

        #########################################################
        # Female Shift time
        # ---- Requestor
        if requestor.gender == "F":
            logging.info(logString("Female Shift Time - <Employee>", 2))
            requestorFemaleShifttimeResult, requestorFemaleShifttimeError = (
                checkFemaleShiftTimeFollowsWorkRule(
                    startTime=requestorSwapDayRoster.start_time,
                    endTime=requestorSwapDayRoster.end_time,
                    workRule=workRule,
                )
            )
            if not requestorFemaleShifttimeResult:
                logging.error(
                    f"Requestor Female Shift Time check failed : {requestorFemaleShifttimeError}"
                )
                messages.error(request, requestorFemaleShifttimeError)
                return render(request, template, context)
        else:
            logging.info(f"Female Shift Time check skipped as requestor is male")
        # ---- Requestee
        if requestee.gender == "F":
            logging.info(logString("Female Shift Time - <Requestee>", 2))
            requesteeFemaleShifttimeResult, requesteeFemaleShifttimeError = (
                checkFemaleShiftTimeFollowsWorkRule(
                    startTime=requesteeSwapDayRoster.start_time,
                    endTime=requesteeSwapDayRoster.end_time,
                    workRule=workRule,
                )
            )
            if not requesteeFemaleShifttimeResult:
                logging.error(
                    f"Requestee Female Shift Time check failed : {requesteeFemaleShifttimeError}"
                )
                messages.error(request, requesteeFemaleShifttimeError)
                return render(request, template, context)
        else:
            logging.info(f"Female Shift Time check skipped as requestee is male")

        ########################
        # Regular Shift Duration
        logging.info(logString("Regular Shift Duration", 2))
        # Check Regular shift duration of the roster of the requestee which the employee want to swap with
        requestorRegularShiftDurationResult, requestorRegularShiftDurationError = (
            checkRegularShiftDuration(
                roster=requestorSwapDayRoster,
                workRule=workRule,
            )
        )
        if not requestorRegularShiftDurationResult:
            logging.error(
                f"Requestor Regular Shift Duration check failed : {requestorRegularShiftDurationError}"
            )
            messages.error(request, requestorRegularShiftDurationError)
            return render(request, template, context)

        #   Check Regular shift duration of the roster of the employee which the requestee want to swap with
        requesteeRegularShiftDurationResult, requesteeRegularShiftDurationError = (
            checkRegularShiftDuration(roster=requesteeSwapDayRoster, workRule=workRule)
        )
        if not requesteeRegularShiftDurationResult:
            logging.error(
                f"Requestee Regular Shift Duration check failed : {requesteeRegularShiftDurationError}"
            )
            messages.error(request, requesteeRegularShiftDurationError)
            return render(request, template, context)

        ###################################################################
        # Check Roster end time of a shift is between the prohibitted time
        logging.info(
            logString(
                "Roster end time of a shift is between the prohibitted time",
                2,
            )
        )
        requestorProhibitedTimeResult, requestorProhibitedTimeError = (
            checkShiftEndInProhibitedTime(
                roster=requestorSwapDayRoster,
                workRule=workRule,
            )
        )

        if not requestorProhibitedTimeResult:
            logging.error(
                f"Requestor Prohibitted Time check failed : {requestorProhibitedTimeError}"
            )
            messages.error(request, requestorProhibitedTimeError)
            return render(request, template, context)

        requesteeProhibitedTimeResult, requesteeProhibitedTimeError = (
            checkShiftEndInProhibitedTime(
                roster=requesteeSwapDayRoster,
                workRule=workRule,
            )
        )

        if not requesteeProhibitedTimeResult:
            logging.error(
                f"Requestee Prohibitted Time check failed : {requesteeProhibitedTimeError}"
            )
            messages.error(request, requesteeProhibitedTimeError)
            return render(request, template, context)

        # Check if the Day Off Trading already exists
        try:
            dayOffTradingExists = DayOffTrading.objects.filter(
                Q(requestor=requestor),
                Q(requestee=requestee),
                Q(requestor_swap_roster=requestorSwapDayRoster),
                Q(requestor_trade_roster=requestorTradeDayRoster),
                Q(requestee_swap_roster=requesteeSwapDayRoster),
                Q(requestee_trade_roster=requesteeTradeDayRoster),
                Q(trading_status__in=["in process", "accepted"]),
            ).exists()

            if dayOffTradingExists:
                logging.error("Trading already exists")
                messages.error(request, "Trading already exists")
                return render(request, template, context)

            # Create a new Day Off Trading instance
            dayOffTradingInstance = DayOffTrading(
                requestor=requestor,
                requestee=requestee,
                requestor_swap_roster=requestorSwapDayRoster,
                requestor_trade_roster=requestorTradeDayRoster,
                requestee_swap_roster=requesteeSwapDayRoster,
                requestee_trade_roster=requesteeTradeDayRoster,
                trading_status="in process",
            )
            dayOffTradingInstance.save()
            return redirect(PageInfoCollection.DAYOFFTRADING_VIEW.urlName)

        except DayOffTrading.DoesNotExist:
            messages.error(request, "Trading does not exist")
            return render(request, template, context)

        except Exception as e:
            logging.error(
                logString(f"Could not create Day off Trading. Exception: {e}", 4)
            )
            messages.error(request, "Could not create Day off Trading")
            return render(request, template, context)

    else:
        form1 = DayOffTradingForm(
            employee=requestor, swapDateID=None, tradeDateID=None, requesteeID=None
        )
        context["form1"] = form1

    return render(request, template, context)


@login_required(login_url="/login/")
@check_user_able_to_see_page(GroupEnum.wfm, GroupEnum.supervisor, GroupEnum.employee)
def createDayOffTradingOLD(request):
    template = "changeRequest/dayOffTrading/create.html"
    breadCrumbList = [
        PageInfoCollection.DAYOFFTRADING_VIEW,
        PageInfoCollection.DAYOFFTRADING_CREATE,
    ]
    employee = getEmployee(request.user.id)

    if request.method == "POST" and "btnform1" in request.POST:
        logging.info(logString("Day Off Trading", 1))
        swapDateID = int(request.POST.get("swapDate"))
        tradeDateID = int(request.POST.get("tradeDate"))
        requesteeID = int(request.POST.get("requestee"))

        form1 = DayOffTradingForm(
            employee=employee,
            swapDateID=swapDateID,
            tradeDateID=tradeDateID,
            requesteeID=requesteeID,
        )

        try:
            workRule = WorkRule.objects.get(id=1)
            logging.info(logString("WorkRule exists", 3))
        except WorkRule.DoesNotExist:
            workRule = None
            logging.error(logString("WorkRule does not exist", 5))
            messages.error(request, "WorkRule does not exist")

        if workRule is not None:
            result = False
            requestee = Employee.objects.get(id=requesteeID)
            # The roster selected by requestor to be swapped
            requestorSwapDayRoster = Roster.objects.get(id=swapDateID)
            # The roster selected by requestor to be traded
            requestorTradeDayRoster = Roster.objects.get(id=tradeDateID)
            # The roster of requestee to be swapped
            requesteeSwapDayRoster = None
            # The roster of requestee to be traded
            requesteeTradeDayRoster = None
            try:
                requestor_swap_roster = Roster.objects.get(id=swapDateID)
                requestor_trade_roster = Roster.objects.get(id=tradeDateID)
                requestee_swap_roster = Roster.objects.get(id=requesteeID)

                # Validate work rules
                error_messages = []

                # Consecutive working days
                if (
                    requestor_trade_roster.start_date - requestor_swap_roster.start_date
                ).days > workRule.consecutive_working_days:
                    error_messages.append(
                        "Exceeds the maximum allowed consecutive working days."
                    )

                # Regular shift duration
                requestor_shift_duration = (
                    datetime.combine(
                        requestor_swap_roster.end_date,
                        requestor_swap_roster.end_time,
                    )
                    - datetime.combine(
                        requestor_swap_roster.start_date,
                        requestor_swap_roster.start_time,
                    )
                ).seconds / 3600
                if (
                    requestor_shift_duration < workRule.minimum_regular_shift_duration
                    or requestor_shift_duration
                    > workRule.maximum_regular_shift_duration
                ):
                    error_messages.append(
                        "Requestor shift duration does not comply with regular shift duration limits."
                    )

                requestee_shift_duration = (
                    datetime.combine(
                        requestee_swap_roster.end_date, requestee_swap_roster.end_time
                    )
                    - datetime.combine(
                        requestee_swap_roster.start_date,
                        requestee_swap_roster.start_time,
                    )
                ).seconds / 3600
                if (
                    requestee_shift_duration < workRule.minimum_regular_shift_duration
                    or requestee_shift_duration
                    > workRule.maximum_regular_shift_duration
                ):
                    error_messages.append(
                        "Requestee shift duration does not comply with regular shift duration limits."
                    )

                # Gap between shifts
                if (
                    datetime.combine(
                        requestor_swap_roster.end_date, requestor_swap_roster.end_time
                    )
                    + timedelta(
                        hours=workRule.gap_between_shift_end_to_the_next_shift_start_time
                    )
                ) > datetime.combine(
                    requestor_trade_roster.start_date, requestor_trade_roster.start_time
                ):
                    error_messages.append(
                        "Insufficient gap between requestor's shifts."
                    )

                if (
                    datetime.combine(
                        requestee_swap_roster.end_date, requestee_swap_roster.end_time
                    )
                    + timedelta(
                        hours=workRule.gap_between_shift_end_to_the_next_shift_start_time
                    )
                ) > datetime.combine(
                    requestee_swap_roster.start_date, requestee_swap_roster.start_time
                ):
                    error_messages.append(
                        "Insufficient gap between requestee's shifts."
                    )

                # Female shift time
                if requestor_swap_roster.gender == "F":
                    if not (
                        workRule.female_shift_start_time
                        <= requestor_swap_roster.start_time
                        <= workRule.female_shift_end_time
                    ):
                        error_messages.append(
                            "Requestor's shift does not comply with female shift time limits."
                        )
                if requestee_swap_roster.gender == "F":
                    if not (
                        workRule.female_shift_start_time
                        <= requestee_swap_roster.start_time
                        <= workRule.female_shift_end_time
                    ):
                        error_messages.append(
                            "Requestee's shift does not comply with female shift time limits."
                        )

                # Prohibited time for end of a shift
                if (
                    workRule.prohibited_time_for_end_of_a_shift_start_time
                    <= requestor_swap_roster.end_time
                    <= workRule.prohibited_time_for_end_of_a_shift_end_time
                ):
                    error_messages.append(
                        "Requestor's shift ends in the prohibited time interval."
                    )
                if (
                    workRule.prohibited_time_for_end_of_a_shift_start_time
                    <= requestee_swap_roster.end_time
                    <= workRule.prohibited_time_for_end_of_a_shift_end_time
                ):
                    error_messages.append(
                        "Requestee's shift ends in the prohibited time interval."
                    )

                if error_messages:
                    for error in error_messages:
                        messages.error(request, error)
                else:
                    # Save the day off trading request
                    DayOffTrading.objects.create(
                        requestor=employee,
                        requestee_id=requesteeID,
                        requestor_swap_roster=requestor_swap_roster,
                        requestor_trade_roster=requestor_trade_roster,
                        requestee_swap_roster=requestee_swap_roster,
                        requestee_trade_roster=requestor_trade_roster,  # should be appropriate
                        trading_status="in process",
                    )
                    messages.success(
                        request, "Day Off Trading request created successfully."
                    )
                    return redirect("day_off_trading_list")

            except Roster.DoesNotExist:
                messages.error(request, "Roster does not exist.")
    else:
        form1 = DayOffTradingForm(
            employee=employee, swapDateID=None, tradeDateID=None, requesteeID=None
        )

    context = {
        "form1": form1,
        "breadCrumbList": breadCrumbList,
        "currentBreadCrumb": PageInfoCollection.DAYOFFTRADING_CREATE.pageName,
        "details": {
            "name": "delete",
            "type": "process",
        },
        "ajaxUrl": PageInfoCollection.PROCESS_JSON.urlName,
        "createUrl": PageInfoCollection.DAYOFFTRADING_CREATE.urlName,
        "dayOffTradingActive": "active",
    }
    return render(request, template, context)


@login_required(login_url="/login/")
@check_user_able_to_see_page(
    GroupEnum.wfm, GroupEnum.supervisor, GroupEnum.employee, GroupEnum.mis_group_1
)
def createshiftTimeTrading(request):
    template = "changeRequest/shiftTimeTrading/create.html"
    breadCrumbList = [
        PageInfoCollection.SHIFTTIMETRADING_VIEW,
        PageInfoCollection.SHIFTTIMETRADING_CREATE,
    ]
    context = {
        "breadCrumbList": breadCrumbList,
        "currentBreadCrumb": PageInfoCollection.SHIFTTIMETRADING_CREATE.pageName,
        "details": {
            "name": "delete",
            "type": "process",
        },
        "ajaxUrl": PageInfoCollection.PROCESS_JSON.urlName,
        "createUrl": PageInfoCollection.SHIFTTIMETRADING_CREATE.urlName,
        "shiftTimeTradingActive": "active",
    }
    requestor = getEmployee(request.user.id)

    if request.method == "POST" and "btnform1" in request.POST:
        result = False
        swapDateID = int(request.POST.get("swapDate"))
        requesteeID = int(request.POST.get("requestee"))

        form1 = ShiftTimeTradingForm(
            employee=requestor,
            swapDateID=swapDateID,
            requesteeID=requesteeID,
        )
        context["form1"] = form1
        requestorRoster = Roster.objects.get(id=swapDateID)
        try:
            workRule = WorkRule.objects.get(id=1)
            logger.info("|Passed|WorkRule exists")
        except WorkRule.DoesNotExist:
            workRule = None
            messages.error(request, "WorkRule does not exist")
            logger.error("|Failed|WorkRule does not exist")
            return render(request, template, context)
        #   REQUESTEE
        try:
            requestee = Employee.objects.get(id=requesteeID)
        except Employee.DoesNotExist:
            logging.error(
                logString(f"Employee with ID {requesteeID} does not exist", 5)
            )
            messages.error(request, "Requestee does not exist")
            return render(request, template, context)
        logging.info(
            f"Requestor:{requestor} |id:{requestor.id}|\nRequestee:{requestee} |id:{requestee.id}|\n"
        )
        #   REQUESTEE Roster
        try:
            requesteeRoster = Roster.objects.filter(
                Q(employee=requestee),
                Q(start_date=requestorRoster.start_date),
                Q(end_date=requestorRoster.end_date),
            ).first()
        except Exception as e:
            messages.error(request, "Requestee Roster Not Found")
            logger.error(f"|Failed|Requestee Roster Not Found:{e}")
            return render(request, template, context)
        ###
        ##  Checking Business rules
        ###
        ##  Gap check
        employeeSwappedTimeRoster = Roster(
            employee=requestor,
            start_date=requestorRoster.start_date,
            start_time=requesteeRoster.start_time,
            end_date=requestorRoster.end_date,
            end_time=requesteeRoster.end_time,
        )
        employeeRosterGapCheck = gapCheck(
            roster=employeeSwappedTimeRoster,
            employee=requestor,
            workRule=workRule,
        )
        if employeeRosterGapCheck is False:
            pass
        if workRule is not None:

            if 1 > 0:

                ##  Gap check

                if employeeRosterGapCheck is True:
                    requesteeSwappedTimeRoster = Roster(
                        employee=requestee,
                        start_date=requesteeRoster.start_date,
                        start_time=requestorRoster.start_time,
                        end_date=requesteeRoster.end_date,
                        end_time=requestorRoster.end_time,
                    )

                    requesteeRosterGapCheck = gapCheck(
                        roster=requesteeSwappedTimeRoster,
                        employee=requestee,
                        workRule=workRule,
                    )
                    logger.info(
                        "Gap of {employee} and {requestee} EXISTS".format(
                            employee=requestor.user.name, requestee=requestee.user.name
                        )
                    )
                    if requesteeRosterGapCheck is True:
                        ## Female Shift time
                        employeeGenderResult = True
                        if requestor.gender == "F":
                            employeeGenderResult = checkFemaleShiftTimeFollowsWorkRule(
                                startTime=employeeSwappedTimeRoster.start_time,
                                endTime=employeeSwappedTimeRoster.end_time,
                                workRule=workRule,
                                request=request,
                            )
                        requesteeGenderResult = True
                        if requestee.gender == "F":
                            requesteeGenderResult = checkFemaleShiftTimeFollowsWorkRule(
                                startTime=requesteeSwappedTimeRoster.start_time,
                                endTime=requesteeSwappedTimeRoster.end_time,
                                workRule=workRule,
                                request=request,
                            )
                        if (
                            employeeGenderResult is True
                            and requesteeGenderResult is True
                        ):
                            logger.info("|Passed|Female Shift Time Check")
                            #   Regular Shift Duration
                            #   Check Regular shift duration of the roster of the requestee which the employee want to swap with
                            employeeRegularShiftDurationResult = (
                                checkRegularShiftDuration(
                                    roster=employeeSwappedTimeRoster,
                                    workRule=workRule,
                                    request=request,
                                )
                            )
                            #   Check Regular shift duration of the roster of the employee which the requestee want to swap with
                            requesteeRegularShiftDurationResult = (
                                checkRegularShiftDuration(
                                    roster=requesteeSwappedTimeRoster,
                                    workRule=workRule,
                                    request=request,
                                )
                            )
                            if (
                                employeeRegularShiftDurationResult is True
                                and requesteeRegularShiftDurationResult is True
                            ):
                                logger.info("|Passed|Regular Shift Duration Check")
                                ##   Check Roster end time of a shift is between the prohibitted time
                                employeeProhibitedTimeResult = (
                                    checkShiftEndInProhibitedTime(
                                        roster=employeeSwappedTimeRoster,
                                        workRule=workRule,
                                    )
                                )
                                requesteeProhibitedTimeResult = (
                                    checkShiftEndInProhibitedTime(
                                        roster=requesteeSwappedTimeRoster,
                                        workRule=workRule,
                                    )
                                )
                                if (
                                    employeeProhibitedTimeResult is False
                                    and requesteeProhibitedTimeResult is False
                                ):
                                    logger.info("|Passed|Prohibited Time Check")
                                    shiftTimeTradingExist = (
                                        ShiftTimeTrading.objects.filter(
                                            Q(requestor=requestor),
                                            Q(requestee=requestee),
                                            Q(requestor_swap_roster=requestorRoster),
                                            Q(requestee_swap_roster=requesteeRoster),
                                            Q(requestee_approval_status="accepted"),
                                            Q(trading_status="in process")
                                            | Q(trading_status="accepted"),
                                        ).exists()
                                    )
                                    if shiftTimeTradingExist is True:
                                        errorMessage = "Trading already exists"
                                        logger.info(errorMessage)
                                        messages.error(
                                            request,
                                            errorMessage,
                                        )
                                    else:
                                        try:
                                            shiftTimeTradingInstance = ShiftTimeTrading(
                                                requestor=requestor,
                                                requestee=requestee,
                                                requestor_swap_roster=requestorRoster,
                                                requestor_start_time=requestorRoster.start_time,
                                                requestor_end_time=requestorRoster.end_time,
                                                requestee_swap_roster=requesteeRoster,
                                                requestee_start_time=requesteeRoster.start_time,
                                                requestee_end_time=requesteeRoster.end_time,
                                                trading_status="in process",
                                            )
                                            shiftTimeTradingInstance.save()
                                            result = True

                                        except Exception as e:
                                            logger.error(
                                                "|Failed| Creating new shift time trading instance.\nException:{exception}".format(
                                                    exception=e
                                                )
                                            )
                                            messages.error(
                                                request,
                                                "Exception:{exception}".format(
                                                    exception=e
                                                ),
                                            )

            else:
                errorText = "|Failed|Roster of {requestee} Not found".format(
                    requestee=requestee.user.name
                )
                logger.error(errorText)
                messages.error(request, errorText.replace("|Failed|", ""))

            if result is True:
                messages.success(
                    request,
                    "Request Submitted Successfully",
                )
                return redirect(PageInfoCollection.SHIFTTIMETRADING_VIEW.urlName)
            else:
                messages.error(
                    request,
                    "Failed to Submit Request",
                )

    else:
        form1 = ShiftTimeTradingForm(
            employee=requestor, swapDateID=None, requesteeID=None
        )
        context["form1"] = form1

    return render(request, template, context)


def get_roster_details(request):
    requestee_id = request.GET.get("requestee_id")
    swap_date_id = request.GET.get("swap_date_id")
    print(requestee_id)
    print(swap_date_id)
    data = {
        "start_time": None,
        "end_time": None,
    }
    requestee = CustomUser.objects.get(id=requestee_id)
    # try:
    #     roster_entry = Roster.objects.get(
    #         employee__id=requestee_id, start_date=swap_date_id
    #     )
    #     data = {
    #         "start_time": roster_entry.start_time,
    #         "end_time": roster_entry.end_time,
    #     }
    # except Roster.DoesNotExist:
    #     data = {
    #         "start_time": None,
    #         "end_time": None,
    #     }
    return JsonResponse(data)


@login_required(login_url="/login/")
@check_user_able_to_see_page(
    GroupEnum.wfm, GroupEnum.supervisor, GroupEnum.employee, GroupEnum.mis_group_1
)
def viewShiftTimeTradingRequests(request):
    template = "changeRequest/shiftTimeTrading/view.html"
    breadCrumbList = [
        PageInfoCollection.SHIFTTIMETRADING_VIEW,
    ]

    employee = getEmployee(request.user.id)
    if employee.is_supervisor():
        userType = "Supervisor"
    else:
        userType = "Employee"
    context = {
        "breadCrumbList": breadCrumbList,
        "currentBreadCrumb": PageInfoCollection.SHIFTTIMETRADING_VIEW.pageName,
        "details": {
            "name": "delete",
            "type": "process",
        },
        "ajaxUrl": PageInfoCollection.SHIFTTIMETRADING_JSON.urlName,
        "createUrl": PageInfoCollection.SHIFTTIMETRADING_CREATE.urlName,
        "shiftTimeTradingActive": "active",
        "userType": userType,
    }
    return render(request, template, context)


@login_required(login_url="/login/")
@check_user_able_to_see_page(GroupEnum.wfm, GroupEnum.supervisor, GroupEnum.employee)
def acceptDayOffTrading(request, id):
    record = DayOffTrading.objects.get(id=id)
    success = False
    errorMessage = "Failed to Accept"
    successMessage = ""
    if request.user.is_Employee():
        if record.requestee_approval_status == None:
            try:
                record.requestee_approval_status = "approved"
                record.requestee_approval_status_datetime = datetime.now()
                record.save()
                success = True
                logging.info(
                    f"|Success| DayOffTrading |id:{id}| Accepted Successfully by Employee {request.user}"
                )
                successMessage = "Accepted Successfully. Sent to Approver for Approval"
            except Exception as e:
                logging.error(f"|Failed| DayOffTrading |id:{id}| Exception:{e}")
        else:
            errorMessage = "Decision already taken"
            logging.error(f"|Failed| DayOffTrading |id:{id}| {errorMessage} ")

    elif request.user.is_Supervisor():
        employee = getEmployee(request.user.id)
        if record.supervisor_approval_status == None:
            firstSwapResult = swapRosterTimes(
                record.requestor_swap_roster.id, record.requestee_trade_roster.id
            )
            if firstSwapResult is True:
                secondSwapResult = swapRosterTimes(
                    record.requestor_trade_roster.id, record.requestee_swap_roster.id
                )
                if secondSwapResult is True:
                    try:
                        record.supervisor = employee
                        record.supervisor_approval_status = "approved"
                        record.supervisor_approval_status_datetime = datetime.now()
                        record.trading_status = "approved"
                        record.save()
                        success = True
                        logging.info(
                            f"|Success| DayOffTrading |id:{id}| Accepted Successfully by Supervisor {request.user}"
                        )
                        successMessage = "Accepted Successfully"
                    except Exception as e:
                        logging.error(f"|Failed| DayOffTrading |id:{id}| Exception:{e}")
                else:
                    errorMessage = "Internal error occurred"
                    logging.warning(
                        f"|Failed| {errorMessage} - Second swap failed |id:{id}|"
                    )
            else:
                errorMessage = "Internal error occurred"
                logging.warning(
                    f"|Failed| {errorMessage} - First swap failed |id:{id}|"
                )
        else:
            errorMessage = "Decision already taken"
            logging.warning(f"|Failed| {errorMessage} |id:{id}|")

    response = JsonResponse(
        {
            "success": success,
            "message": successMessage if success is True else errorMessage,
        }
    )
    return response


@login_required(login_url="/login/")
@check_user_able_to_see_page(GroupEnum.wfm, GroupEnum.supervisor, GroupEnum.employee)
def rejectDayOffTrading(request, id):
    record = DayOffTrading.objects.get(id=id)
    success = False
    errorMessage = "Failed to Reject"
    successMessage = ""
    if request.user.is_Employee():
        employee = getEmployee(request.user.id)
        if record.requestee_approval_status == None:
            try:
                record.requestee_approval_status = "rejected"
                record.requestee_approval_status_datetime = datetime.now()
                record.trading_status = "rejected"
                record.save()
                success = True
                logging.info(
                    f"|Success| DayOffTrading |id:{id}| Rejected Successfully by Employee {request.user}"
                )
                successMessage = "Rejected Successfully"
            except Exception as e:
                logging.error(f"|Failed| DayOffTrading |id:{id}| Exception:{e}")
        else:
            errorMessage = "Decision already taken"
            logging.error(f"|Failed| DayOffTrading |id:{id}| {errorMessage} ")
    elif request.user.is_Supervisor():
        employee = getEmployee(request.user.id)
        if record.supervisor_approval_status == None:
            try:
                record.supervisor = employee
                record.supervisor_approval_status = "rejected"
                record.supervisor_approval_status_datetime = datetime.now()
                record.trading_status = "rejected"
                record.save()
                success = True
                logging.info(
                    f"|Success| DayOffTrading |id:{id}| Rejected Successfully by Supervisor {request.user}"
                )
                successMessage = "Rejected Successfully"
            except Exception as e:
                logging.error(f"|Failed| DayOffTrading |id:{id}| Exception:{e}")
        else:
            errorMessage = "Decision already taken"
            logging.warning(f"|Failed| {errorMessage} |id:{id}|")
    response = JsonResponse(
        {
            "success": success,
            "message": successMessage if success is True else errorMessage,
        }
    )
    return response


@login_required(login_url="/login/")
@check_user_able_to_see_page(GroupEnum.wfm, GroupEnum.supervisor, GroupEnum.employee)
def acceptShiftTimeTrading(request, id):
    record = ShiftTimeTrading.objects.get(id=id)
    success = False
    errorMessage = "Failed to Accept"
    successMessage = ""
    if request.user.is_Employee():
        employee = getEmployee(request.user.id)
        if employee.is_supervisor():
            if record.supervisor_approval_status == None:
                swapResult = swapRosterTimes(
                    record.requestor_swap_roster, record.requestee_swap_roster
                )
                if swapResult is True:
                    try:
                        record.supervisor = employee
                        record.supervisor_approval_status = "approved"
                        record.supervisor_approval_status_datetime = datetime.now()
                        record.trading_status = "approved"
                        record.save()
                        success = True
                        logging.info(
                            f"|Success| ShiftTimeTrading |id:{id}| Accepted Successfully by Supervisor {request.user}"
                        )
                        successMessage = "Accepted Successfully"
                    except Exception as e:
                        logging.error(
                            f"|Failed| ShiftTimeTrading |id:{id}| Exception:{e}"
                        )
                else:
                    logging.warning(f"|Failed| First Swap Failed |id:{id}|")
            else:
                errorMessage = "Decision already taken"
                logging.warning(f"|Failed| {errorMessage} |id:{id}|")
        else:
            if record.requestee_approval_status == None:
                try:
                    record.requestee_approval_status = "approved"
                    record.requestee_approval_status_datetime = datetime.now()
                    record.save()
                    success = True
                    logging.info(
                        f"|Success| ShiftTimeTrading |id:{id}| Accepted Successfully by Employee {request.user}"
                    )
                    successMessage = (
                        "Accepted Successfully. Sent to Approver for Approval"
                    )
                except Exception as e:
                    logging.error(f"|Failed| ShiftTimeTrading |id:{id}| Exception:{e}")
            else:
                errorMessage = "Decision already taken"
                logging.error(f"|Failed| ShiftTimeTrading |id:{id}| {errorMessage} ")

    response = JsonResponse(
        {
            "success": success,
            "message": successMessage if success is True else errorMessage,
        }
    )
    return response


@login_required(login_url="/login/")
@check_user_able_to_see_page(GroupEnum.wfm, GroupEnum.supervisor, GroupEnum.employee)
def rejectShiftTimeTrading(request, id):
    record = ShiftTimeTrading.objects.get(id=id)
    success = False
    errorMessage = "Failed to Reject"
    successMessage = ""
    if request.user.is_Employee():
        employee = getEmployee(request.user.id)
        if employee.is_supervisor():
            if record.supervisor_approval_status == None:
                try:
                    record.supervisor = employee
                    record.supervisor_approval_status = "rejected"
                    record.supervisor_approval_status_datetime = datetime.now()
                    record.trading_status = "rejected"
                    record.save()
                    success = True
                    logging.info(
                        f"|Success| ShiftTimeTrading |id:{id}| Rejected Successfully by Supervisor {request.user}"
                    )
                    successMessage = "Rejected Successfully"
                except Exception as e:
                    logging.error(f"|Failed| ShiftTimeTrading |id:{id}| Exception:{e}")
            else:
                errorMessage = "Decision already taken"
                logging.warning(f"|Failed| {errorMessage} |id:{id}|")
        else:
            if record.requestee_approval_status == None:
                try:
                    record.requestee_approval_status = "rejected"
                    record.requestee_approval_status_datetime = datetime.now()
                    record.trading_status = "rejected"
                    record.save()
                    success = True
                    logging.info(
                        f"|Success| ShiftTimeTrading |id:{id}| Rejected Successfully by Employee {request.user}"
                    )
                    successMessage = "Rejected Successfully"
                except Exception as e:
                    logging.error(f"|Failed| ShiftTimeTrading |id:{id}| Exception:{e}")
            else:
                errorMessage = "Decision already taken"
    response = JsonResponse(
        {
            "success": success,
            "message": successMessage if success is True else errorMessage,
        }
    )

    return response


class ShiftTimeTradingListJson(BaseDatatableView):
    model = ShiftTimeTrading
    columns = [
        "requestor",
        "requestor_swap_roster",
        "requestor_start_time",
        "requestor_end_time",
        "requestee",
        "requestee_start_time",
        "requestee_end_time",
        "trading_status" "actions",
    ]
    order_columns = [
        "requestor",
        "requestor_swap_roster",
        "requestor_start_time",
        "requestor_end_time",
        "requestee",
        "requestee_start_time",
        "requestee_end_time",
        "trading_status" "",
    ]

    def get_initial_queryset(self):
        # Filter ShiftTimeTrading instances for the current user
        if self.request.user.is_Employee():
            employee = getEmployee(self.request.user.id)
            if employee.is_supervisor():
                isSupervisor = True
                supervised_employees = Employee.objects.filter(
                    Q(supervisor_1=employee) | Q(supervisor_2=employee)
                )
                return ShiftTimeTrading.objects.filter(
                    Q(requestor__in=supervised_employees)
                    | Q(requestee__in=supervised_employees)
                ).order_by("-created_At")
            else:
                return ShiftTimeTrading.objects.filter(
                    Q(requestor=employee) | Q(requestee=employee)
                ).order_by("-created_At")

    def filter_queryset(self, qs):
        # Handle POST parameters for filtering the queryset
        search = self.request.POST.get("search[value]", None)
        if search:
            qs = qs.filter(requestor__user__name__icontains=search)

        return qs

    def prepare_results(self, qs):
        data = []
        if self.request.user.is_Employee():
            employee = getEmployee(self.request.user.id)
            if employee.is_supervisor():
                for item in qs:
                    # Fetch the related field and use it directly in the data dictionary
                    row = {
                        "requestor": item.requestor.user.name,
                        "requestor_swap_roster": item.requestor_swap_roster.start_date,
                        "requestee": item.requestee.user.name,
                        "requestor_start_time": item.requestor_start_time.strftime(
                            "%H:%M %p"
                        ),
                        "requestor_end_time": item.requestor_end_time.strftime(
                            "%H:%M %p"
                        ),
                        "requestee_start_time": item.requestee_start_time.strftime(
                            "%H:%M %p"
                        ),
                        "requestee_end_time": item.requestee_end_time.strftime(
                            "%H:%M %p"
                        ),
                        "trading_status": item.trading_status.title().title(),
                        "actions": (
                            ""
                            if item.supervisor_approval_status != None
                            else self.get_actions_html(item)
                        ),
                    }
                    data.append(row)
            else:
                for item in qs:
                    # Fetch the related field and use it directly in the data dictionary
                    row = {
                        "requestor": item.requestor.user.name,
                        "requestor_swap_roster": item.requestor_swap_roster.start_date,
                        "requestee": item.requestee.user.name,
                        "requestor_start_time": item.requestor_start_time.strftime(
                            "%H:%M %p"
                        ),
                        "requestor_end_time": item.requestor_end_time.strftime(
                            "%H:%M %p"
                        ),
                        "requestee_start_time": item.requestee_start_time.strftime(
                            "%H:%M %p"
                        ),
                        "requestee_end_time": item.requestee_end_time.strftime(
                            "%H:%M %p"
                        ),
                        "trading_status": item.trading_status.title().title(),
                        "actions": (
                            ""
                            if self.request.user == item.requestor.user
                            or item.requestee_approval_status != None
                            else self.get_actions_html(item)
                        ),
                    }
                    data.append(row)

        return data

    def render_column(self, row, column):
        return super(ShiftTimeTradingListJson, self).render_column(row, column)

    def get_actions_html(self, item):
        accept_url = reverse("accept_shift_time_trading", args=[item.id])
        reject_url = reverse("reject_shift_time_trading", args=[item.id])

        accept_link = format_html(
            '<a href="{}" data-toggle="modal" data-target="#confirmModal" class="btn btn-success">Accept</a>',
            accept_url,
        )
        reject_link = format_html(
            '<a href="{}" data-toggle="modal" data-target="#rejectModal" class="btn btn-danger">Reject</a>',
            reject_url,
        )

        return format_html("{} {}", accept_link, reject_link)


class DayOffTradingListJson(BaseDatatableView):
    model = DayOffTrading
    columns = [
        "requestor",
        "requestor_swap_roster",
        "requestor_trade_roster",
        "requestee",
        "requestee_swap_roster",
        "requestee_trade_roster",
        "trading_status" "actions",
    ]
    order_columns = [
        "requestor",
        "requestor_swap_roster",
        "requestor_trade_roster",
        "requestee",
        "requestee_swap_roster",
        "requestee_trade_roster",
        "trading_status",
        "actions",
    ]

    def get_initial_queryset(self):
        # Filter ShiftTimeTrading instances for the current user
        now = timezone.localtime()
        # now = datetime(2024, 9, 20, 14, 00, 45)
        if self.request.user.is_Employee():
            employee = getEmployee(self.request.user.id)
            return (
                DayOffTrading.objects.filter(
                    Q(requestor=employee) | Q(requestee=employee)
                )
                .exclude(
                    Q(requestor_swap_roster__start_date__lt=now.date())
                    | Q(requestor_trade_roster__start_date__lt=now.date())
                    | (
                        Q(requestor_swap_roster__start_date=now.date())
                        & Q(requestor_swap_roster__start_time__lt=now.time())
                    )
                    | (
                        Q(requestor_trade_roster__start_date=now.date())
                        & Q(requestor_trade_roster__start_time__lt=now.time())
                    )
                )
                .exclude(
                    Q(requestee_swap_roster__start_date__lt=now.date())
                    | Q(requestee_trade_roster__start_date__lt=now.date())
                    | (
                        Q(requestee_swap_roster__start_date=now.date())
                        & Q(requestee_swap_roster__start_time__lt=now.time())
                    )
                    | (
                        Q(requestee_trade_roster__start_date=now.date())
                        & Q(requestee_trade_roster__start_time__lt=now.time())
                    )
                )
                .order_by("-created_At")
            )
        elif self.request.user.is_Supervisor():
            employee = getEmployee(self.request.user.id)
            supervised_employees = Employee.objects.filter(
                Q(supervisor_1=employee) | Q(supervisor_2=employee)
            )

            return (
                DayOffTrading.objects.filter(
                    Q(requestor__in=supervised_employees)
                    | Q(requestee__in=supervised_employees)
                )
                .exclude(
                    Q(requestor_swap_roster__start_date__lt=now.date())
                    | Q(requestor_trade_roster__start_date__lt=now.date())
                    | (
                        Q(requestor_swap_roster__start_date=now.date())
                        & Q(requestor_swap_roster__start_time__lt=now.time())
                    )
                    | (
                        Q(requestor_trade_roster__start_date=now.date())
                        & Q(requestor_trade_roster__start_time__lt=now.time())
                    )
                )
                .exclude(
                    Q(requestee_swap_roster__start_date__lt=now.date())
                    | Q(requestee_trade_roster__start_date__lt=now.date())
                    | (
                        Q(requestee_swap_roster__start_date=now.date())
                        & Q(requestee_swap_roster__start_time__lt=now.time())
                    )
                    | (
                        Q(requestee_trade_roster__start_date=now.date())
                        & Q(requestee_trade_roster__start_time__lt=now.time())
                    )
                )
                .order_by("-created_At")
            )
        elif self.request.user.is_WFM() or self.request.user.is_MIS_GROUP_1():
            return DayOffTrading.objects.all()

    def filter_queryset(self, qs):
        # Handle POST parameters for filtering the queryset
        search = self.request.POST.get("search[value]", None)
        if search:
            qs = qs.filter(requestor__user__name__icontains=search)

        return qs

    def prepare_results(self, qs):
        data = []
        if self.request.user.is_Employee():
            for item in qs:
                # Fetch the related field and use it directly in the data dictionary
                row = {
                    "requestor": item.requestor.user.name,
                    "requestor_swap_roster": item.requestor_swap_roster.start_date,
                    "requestor_trade_roster": item.requestor_trade_roster.start_date,
                    "requestee": item.requestee.user.name,
                    "requestee_swap_roster": item.requestee_swap_roster.start_date,
                    "requestee_trade_roster": item.requestee_trade_roster.start_date,
                    "trading_status": item.trading_status.title(),
                    "actions": (
                        ""
                        if self.request.user == item.requestor.user
                        or item.requestee_approval_status != None
                        else self.get_actions_html(item)
                    ),
                }
                data.append(row)
        elif self.request.user.is_Supervisor():
            for item in qs:
                # Fetch the related field and use it directly in the data dictionary
                logger.info(f"supervisor approval:{item.supervisor_approval_status}")
                logger.info(f"requestee approval:{item.requestee_approval_status}")
                actions = ""

                if item.trading_status in ["approved", "rejected"]:
                    actions = ""
                else:
                    if item.requestee_approval_status is not None:
                        actions = self.get_actions_html(item)
                row = {
                    "requestor": item.requestor.user.name,
                    "requestor_swap_roster": item.requestor_swap_roster.start_date,
                    "requestor_trade_roster": item.requestor_trade_roster.start_date,
                    "requestee": item.requestee.user.name,
                    "requestee_swap_roster": item.requestee_swap_roster.start_date,
                    "requestee_trade_roster": item.requestee_trade_roster.start_date,
                    "trading_status": item.trading_status.title(),
                    "actions": actions,
                }
                data.append(row)
        return data

    def render_column(self, row, column):
        return super(DayOffTradingListJson, self).render_column(row, column)

    def get_actions_html(self, item):
        accept_link = ""
        reject_link = ""
        accept_url = reverse("accept_day_off_trading", args=[item.id])
        reject_url = reverse("reject_day_off_trading", args=[item.id])

        accept_link = format_html(
            '<a href="{}" data-toggle="modal" data-target="#confirmModal" class="btn btn-success">Accept</a>',
            accept_url,
        )
        reject_link = format_html(
            '<a href="{}" data-toggle="modal" data-target="#rejectModal" class="btn btn-danger">Reject</a>',
            reject_url,
        )
        button = format_html("{} {}", accept_link, reject_link)
        return button


def test(request):
    template = "changeRequest/shift_time_trading_list.html"
    # table = None
    # if request.user.is_Employee():
    #     employee = getEmployee(request.user.id)
    #     queryset = ShiftTimeTrading.objects.filter(
    #         requestee=employee, requestee_approval_status=None
    #     )
    #     table = ShiftTimeTradingTableEmployee(queryset)
    # if request.user.is_Supervisor():
    #     supervisor = getSupervisor(request.user.id)
    #     # Get the employees supervised by the given supervisor
    #     supervised_employees = Employee.objects.filter(
    #         Q(supervisor_1=supervisor.id) | Q(supervisor_2=supervisor.id),
    #     )
    #     # Get the ShiftTimeTrading instances where requestor or requestee is one of the supervised employees
    #     queryset = ShiftTimeTrading.objects.filter(
    #         Q(requestor__in=supervised_employees)
    #         | Q(requestee__in=supervised_employees),
    #         Q(requestee_approval_status="approved"),
    #         Q(trading_status="in process"),
    #     )
    #     table = ShiftTimeTradingTableSupervisor(queryset)
    # tables.RequestConfig(request, paginate={"per_page": 10}).configure(table)
    context = {}
    return render(request, template, context)
