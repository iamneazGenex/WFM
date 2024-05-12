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
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.http import JsonResponse
from rms.global_utilities import *
from rms.page_info_collection import PageInfoCollection
from django.contrib.auth.decorators import login_required
from rms.constants import GroupEnum
from rms.decorators import check_user_able_to_see_page

logger = logging.getLogger(__name__)

# Create your views here.
################################################################
#   Day Off Trading
################################################################


@login_required(login_url="/login/")
@check_user_able_to_see_page(GroupEnum.wfm, GroupEnum.supervisor, GroupEnum.employee)
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
            employeeSwapDayRoster = Roster.objects.get(id=swapDateID)
            # The roster selected by requestor to be trade
            employeeTradeDayRoster = Roster.objects.get(id=tradeDateID)
            try:
                requesteeSwapDayRoster = Roster.objects.get(
                    employee=requestee, start_date=employeeTradeDayRoster.start_date
                )
                requesteeTradeDayRoster = Roster.objects.get(
                    employee=requestee, start_date=employeeSwapDayRoster.start_date
                )
            except Exception as e:
                messages.error(request, "Exception:{exception}".format(exception=e))
                logging.error(logString(f"Exception:{e}", 5))

            if (
                requesteeSwapDayRoster is not None
                and requesteeTradeDayRoster is not None
            ):
                #   The roster which the employee would swap with the requestee.
                employeeTradeRoster = Roster.objects.get(
                    employee=requestee, start_date=employeeTradeDayRoster.start_date
                )
                #   The roster which the requestee would swap with the requestee.
                requesteeTradeRoster = Roster.objects.get(
                    employee=employee, start_date=employeeSwapDayRoster.start_date
                )
                logging.info(logString("Checking Business Rules", 2))
                ###########################
                ##  Checking Business rules
                ###########################
                # checkMaxCountInAParticularInterval(
                #     requestor=employee,
                #     requestorSwapRoster=employeeSwapDayRoster,
                #     requestee=requestee,
                #     requesteeSwapRoster=requesteeSwapDayRoster,
                #     workRule=workRule,
                # )
                ##########################
                # Consecutive Working Days
                logging.info(logString("Consecutive Working Days", 2))
                employeeConsecutiveWorkingDaysResult = checkConsecutiveWorkingDays(
                    tradeRosterID=tradeDateID, employee=employee, workRule=workRule
                )
                if employeeConsecutiveWorkingDaysResult is True:
                    requesteeConsecutiveWorkingDaysResult = checkConsecutiveWorkingDays(
                        tradeRosterID=requesteeTradeDayRoster.id,
                        employee=requestee,
                        workRule=workRule,
                    )
                    if requesteeConsecutiveWorkingDaysResult is True:
                        logging.info(logString("Consecutive Working Days", 3))
                        ####################
                        # Day can be swaped
                        logging.info(logString("Days can be swapped", 2))
                        dayCanBeSwapedResult = dayCanBeSwaped(
                            requestee=requestee,
                            swapDateID=swapDateID,
                            tradeDateID=tradeDateID,
                            request=request,
                        )
                        if dayCanBeSwapedResult is True:
                            logging.info(logString("Days can be swapped", 3))

                            ####################################################
                            # Gap between shift end to the next shift start time
                            logging.info(logString("Gap Check", 2))
                            gapCheckingResult = (
                                checkGapBetweenShiftEndToTheNextShiftStartTime(
                                    employee=employee,
                                    requestee=requestee,
                                    swapDateID=swapDateID,
                                    tradeDateID=tradeDateID,
                                    workRule=workRule,
                                    request=request,
                                )
                            )
                            if gapCheckingResult:
                                logging.info(logString("Gap Check", 3))
                                ###################
                                # Female Shift time

                                # Made the flag true first as if the employee is male we do not need to check
                                employeeGenderResult = True
                                if employee.gender == "F":
                                    logging.info(
                                        logString("Female Shift Time - <Employee>", 2)
                                    )
                                    employeeGenderResult = (
                                        checkFemaleShiftTimeFollowsWorkRule(
                                            startTime=employeeTradeRoster.start_time,
                                            endTime=employeeTradeRoster.end_time,
                                            workRule=workRule,
                                            request=request,
                                        )
                                    )
                                # Made the flag true first as if the requeste is male we do not need to check
                                requesteeGenderResult = True
                                if requestee.gender == "F":
                                    logging.info(
                                        logString("Female Shift Time - <Requestee>", 2)
                                    )
                                    requesteeGenderResult = (
                                        checkFemaleShiftTimeFollowsWorkRule(
                                            startTime=requesteeTradeRoster.start_time,
                                            endTime=requesteeTradeRoster.end_time,
                                            workRule=workRule,
                                            request=request,
                                        )
                                    )
                                if (
                                    employeeGenderResult is True
                                    and requesteeGenderResult is True
                                ):
                                    logging.info(logString("Female Shift Time", 3))
                                    ########################
                                    # Regular Shift Duration
                                    logging.info(logString("Regular Shift Duration", 2))
                                    # Check Regular shift duration of the roster of the requestee which the employee want to swap with
                                    employeeRegularShiftDurationResult = (
                                        checkRegularShiftDuration(
                                            roster=employeeTradeRoster,
                                            workRule=workRule,
                                            request=request,
                                        )
                                    )
                                    #   Check Regular shift duration of the roster of the employee which the requestee want to swap with
                                    requesteeRegularShiftDurationResult = (
                                        checkRegularShiftDuration(
                                            roster=requesteeTradeRoster,
                                            workRule=workRule,
                                            request=request,
                                        )
                                    )
                                    if (
                                        employeeRegularShiftDurationResult is True
                                        and requesteeRegularShiftDurationResult is True
                                    ):
                                        logging.info(
                                            logString("Regular Shift Duration", 3)
                                        )
                                        ###################################################################
                                        # Check Roster end time of a shift is between the prohibitted time
                                        logging.info(
                                            logString(
                                                "Roster end time of a shift is between the prohibitted time",
                                                2,
                                            )
                                        )
                                        employeeProhibitedTimeResult = (
                                            checkShiftEndInProhibitedTime(
                                                roster=employeeTradeRoster,
                                                workRule=workRule,
                                            )
                                        )
                                        if employeeProhibitedTimeResult is False:
                                            dayOffTradingExists = DayOffTrading.objects.filter(
                                                Q(requestor=employee),
                                                Q(requestee=requestee),
                                                Q(
                                                    requestor_swap_roster=employeeSwapDayRoster
                                                ),
                                                Q(
                                                    requestor_trade_roster=employeeTradeDayRoster
                                                ),
                                                Q(
                                                    requestee_swap_roster=requesteeSwapDayRoster
                                                ),
                                                Q(
                                                    requestee_trade_roster=requesteeTradeDayRoster
                                                ),
                                                Q(trading_status="in process")
                                                | Q(trading_status="accepted"),
                                            ).exists()
                                            if dayOffTradingExists is True:
                                                messages.error(
                                                    request,
                                                    "Trading already exists",
                                                )
                                            else:
                                                try:
                                                    dayOffTradingInstance = DayOffTrading(
                                                        requestor=employee,
                                                        requestee=requestee,
                                                        requestor_swap_roster=employeeSwapDayRoster,
                                                        requestor_trade_roster=employeeTradeDayRoster,
                                                        requestee_swap_roster=requesteeSwapDayRoster,
                                                        requestee_trade_roster=requesteeTradeDayRoster,
                                                        trading_status="in process",
                                                    )
                                                    dayOffTradingInstance.save()
                                                    return redirect(
                                                        PageInfoCollection.DAYOFFTRADING_VIEW.urlName
                                                    )
                                                except Exception as e:
                                                    logging.info(
                                                        logString(
                                                            f"Could not create Day off Trading. Exception:{e}",
                                                            4,
                                                        )
                                                    )
                                                    messages.error(
                                                        request,
                                                        "Could not create Day off Trading",
                                                    )
                                    else:
                                        logging.info(
                                            logString("Regular Shift Duration", 4)
                                        )
                                        messages.error(
                                            request, "Could not create Day off Trading"
                                        )
                                else:
                                    logging.info(logString("Female Shift Time", 4))
                                    messages.error(
                                        request, "Could not create Day off Trading"
                                    )
                            else:
                                logging.info(logString("Gap Check", 4))
                                messages.error(
                                    request, "Could not create Day off Trading"
                                )
                        else:
                            logging.info(logString("Days can be swapped", 4))
                            messages.error(request, "Could not create Day off Trading")
                    else:
                        logging.info(
                            logString("Consecutive Working Days <Requestee>", 4)
                        )
                        messages.error(request, "Could not create Day off Trading")

                else:
                    logging.info(logString("Consecutive Working Days <Employee>", 4))
                    messages.error(request, "Could not create Day off Trading")

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
@check_user_able_to_see_page(GroupEnum.wfm, GroupEnum.supervisor, GroupEnum.employee)
def shiftTimeTrading(request):
    template = "changeRequest/shift_time_trading.html"
    employee = getEmployee(request.user.id)

    if request.method == "POST" and "btnform1" in request.POST:
        result = False
        swapDateID = int(request.POST.get("swapDate"))
        requesteeID = int(request.POST.get("requestee"))

        form1 = ShiftTimeTradingForm(
            employee=employee,
            swapDateID=swapDateID,
            requesteeID=requesteeID,
        )

        try:
            workRule = WorkRule.objects.get(id=1)
            logger.info("|Passed|WorkRule exists")
        except WorkRule.DoesNotExist:
            workRule = None
            messages.error(request, "WorkRule does not exist")
            logger.error("|Failed|WorkRule does not exist")
        if workRule is not None:
            requestee = Employee.objects.get(id=requesteeID)

            employeeRoster = Roster.objects.get(id=swapDateID)
            try:
                requesteeRosterFilter = Roster.objects.filter(
                    Q(employee=requestee),
                    Q(start_date=employeeRoster.start_date),
                    Q(end_date=employeeRoster.end_date),
                    # ~Q(start_time=employeeRoster.start_time),
                )
            except Exception as e:
                logger.error("Exception:{exception}".format(exception=e))
            if requesteeRosterFilter.count() > 0:
                requesteeRoster = requesteeRosterFilter.first()
                ###
                ##  Checking Business rules
                ###

                ##  Gap check
                employeeSwappedTimeRoster = Roster(
                    employee=employee,
                    start_date=employeeRoster.start_date,
                    start_time=requesteeRoster.start_time,
                    end_date=employeeRoster.end_date,
                    end_time=requesteeRoster.end_time,
                )
                employeeRosterGapCheck = gapCheck(
                    roster=employeeSwappedTimeRoster,
                    employee=employee,
                    workRule=workRule,
                )
                if employeeRosterGapCheck is True:
                    requesteeSwappedTimeRoster = Roster(
                        employee=requestee,
                        start_date=requesteeRoster.start_date,
                        start_time=employeeRoster.start_time,
                        end_date=requesteeRoster.end_date,
                        end_time=employeeRoster.end_time,
                    )

                    requesteeRosterGapCheck = gapCheck(
                        roster=requesteeSwappedTimeRoster,
                        employee=requestee,
                        workRule=workRule,
                    )
                    logger.info(
                        "Gap of {employee} and {requestee} EXISTS".format(
                            employee=employee.user.name, requestee=requestee.user.name
                        )
                    )
                    if requesteeRosterGapCheck is True:
                        ## Female Shift time
                        employeeGenderResult = True
                        if employee.gender == "F":
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
                                            Q(requestor=employee),
                                            Q(requestee=requestee),
                                            Q(requestor_swap_roster=employeeRoster),
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
                                                requestor=employee,
                                                requestee=requestee,
                                                requestor_swap_roster=employeeRoster,
                                                requestor_start_time=employeeRoster.start_time,
                                                requestor_end_time=employeeRoster.end_time,
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
            employee=employee, swapDateID=None, requesteeID=None
        )

    context = {"form1": form1}
    return render(request, template, context)


@login_required(login_url="/login/")
@check_user_able_to_see_page(GroupEnum.wfm, GroupEnum.supervisor, GroupEnum.employee)
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
        employee = getEmployee(request.user.id)
        if employee.is_supervisor():
            if record.supervisor_approval_status == None:
                firstSwapResult = swapRosterTimes(
                    record.requestor_swap_roster, record.requestee_trade_roster
                )
                if firstSwapResult is True:
                    secondSwapResult = swapRosterTimes(
                        record.requestor_trade_roster, record.requestee_swap_roster
                    )
                    if secondSwapResult is True:
                        try:
                            record.supervisor = employee
                            record.supervisor_approval_status = "approved"
                            record.supervisor_approval_status_datetime = (
                                datetime.datetime.now()
                            )
                            record.trading_status = "approved"
                            record.save()
                            success = True
                            logging.info(
                                f"|Success| DayOffTrading |id:{id}| Accepted Successfully by Supervisor {request.user}"
                            )
                            successMessage = "Accepted Successfully"
                        except Exception as e:
                            logging.error(
                                f"|Failed| DayOffTrading |id:{id}| Exception:{e}"
                            )
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

        else:
            if record.requestee_approval_status == None:
                try:
                    record.requestee_approval_status = "approved"
                    record.requestee_approval_status_datetime = datetime.datetime.now()
                    record.save()
                    success = True
                    logging.info(
                        f"|Success| DayOffTrading |id:{id}| Accepted Successfully by Employee {request.user}"
                    )
                    successMessage = (
                        "Accepted Successfully. Sent to Approver for Approval"
                    )
                except Exception as e:
                    logging.error(f"|Failed| DayOffTrading |id:{id}| Exception:{e}")
            else:
                errorMessage = "Decision already taken"
                logging.error(f"|Failed| DayOffTrading |id:{id}| {errorMessage} ")
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
        if employee.is_supervisor():
            if record.supervisor_approval_status == None:
                try:
                    record.supervisor = employee
                    record.supervisor_approval_status = "rejected"
                    record.supervisor_approval_status_datetime = datetime.datetime.now()
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
        else:
            if record.requestee_approval_status == None:
                try:
                    record.requestee_approval_status = "rejected"
                    record.requestee_approval_status_datetime = datetime.datetime.now()
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
                        record.supervisor_approval_status_datetime = (
                            datetime.datetime.now()
                        )
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
                    record.requestee_approval_status_datetime = datetime.datetime.now()
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
                    record.supervisor_approval_status_datetime = datetime.datetime.now()
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
                    record.requestee_approval_status_datetime = datetime.datetime.now()
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
                        "trading_status": item.trading_status.title(),
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
                        "trading_status": item.trading_status.title(),
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
        "actions",
    ]
    order_columns = [
        "requestor",
        "requestor_swap_roster",
        "requestor_trade_roster",
        "requestee",
        "requestee_swap_roster",
        "requestee_trade_roster",
        "actions",
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
                return DayOffTrading.objects.filter(
                    Q(requestor__in=supervised_employees)
                    | Q(requestee__in=supervised_employees)
                ).order_by("-created_At")
            else:
                return DayOffTrading.objects.filter(
                    Q(requestor=employee) | Q(requestee=employee)
                ).order_by("-created_At")
        elif self.request.user.is_WFM():
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
            employee = getEmployee(self.request.user.id)
            if employee.is_supervisor():
                for item in qs:
                    # Fetch the related field and use it directly in the data dictionary
                    row = {
                        "requestor": item.requestor.user.name,
                        "requestor_swap_roster": item.requestor_swap_roster.start_date,
                        "requestor_trade_roster": item.requestor_trade_roster.start_date,
                        "requestee": item.requestee.user.name,
                        "requestee_swap_roster": item.requestee_swap_roster.start_date,
                        "requestee_trade_roster": item.requestee_trade_roster.start_date,
                        "actions": (
                            ""
                            if item.supervisor_approval_status != None
                            or item.requestee_approval_status != None
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
                        "requestor_trade_roster": item.requestor_trade_roster.start_date,
                        "requestee": item.requestee.user.name,
                        "requestee_swap_roster": item.requestee_swap_roster.start_date,
                        "requestee_trade_roster": item.requestee_trade_roster.start_date,
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
