from ..models import Roster, RosterCount, RosterSeatCount, Forecast, ShiftLegend
from accounts.models import Employee
from django.contrib import messages
from accounts.models import CustomUser
import logging
import traceback
from accounts.models import *
from django.utils.dateparse import parse_time
from django.utils.dateformat import time_format


logger = logging.getLogger(__name__)


def createRosterCount(roster):
    """Create or update RosterCount Instance

    Args:
        roster (Roster): _description_

    Returns:
        boolean: success or failure of the execution
    """
    logging.info(f"----Trying to create RosterCount of {roster} id:|{roster.id}|")
    success = False
    if roster.start_time is not None:
        try:
            rosterCount = RosterCount.objects.get(
                site=roster.employee.site,
                process=roster.employee.process,
                lob=roster.employee.lob,
                workRole=roster.employee.work_role,
                start_date=roster.start_date,
                start_time=roster.start_time,
                end_date=roster.end_date,
                end_time=roster.end_time,
            )
            rosterCount.count += 1
            rosterCount.save()
            success = True
            logging.info(f"----|Success| Roster Count Updated Successfully")
        except RosterCount.DoesNotExist:
            try:
                rosterCount = RosterCount.objects.create(
                    site=roster.employee.site,
                    process=roster.employee.process,
                    lob=roster.employee.lob,
                    workRole=roster.employee.work_role,
                    start_date=roster.start_date,
                    start_time=roster.start_time,
                    end_date=roster.end_date,
                    end_time=roster.end_time,
                    count=1,
                )
                success = True
                logging.info(f"----|Success| Roster Count Created Successfully")
            except Exception as e:
                logging.error(
                    f"----|Failed| Roster Count Creation failed.Exception: {e}"
                )
    else:
        success = True
        logging.info(f"----|Success| Did not create Roster Count as start time is none")
    return success


def roster_creation(data, request, index=None):
    """Create a Roster

    Args:
        data (dict): Roster Creation Data
        request (HttpRequest): Request from view

    Returns:
        bool: If the creation is successful, False otherwise
    """
    success = False
    logging.info(
        f"----Attempting to create roster with data: {', '.join(map(str, data.items()))}"
    )
    try:
        # Check if roster already exists with exact details
        Roster.objects.get(
            employee=data["employee"],
            start_date=data["start_date"],
            start_time=data["start_time"],
            end_date=data["end_date"],
            end_time=data["end_time"],
        )
    except Roster.DoesNotExist:
        logging.info(f"----Roster does not exist, proceeding with creation.")
        try:
            # Check if a roster already exists for the employee on the given start date
            existing_roster = Roster.objects.get(
                employee=data["employee"], start_date=data["start_date"]
            )
            message = f"A roster already exists on {existing_roster.start_date.strftime('%d-%m-%Y')} for {existing_roster.employee.user.name} {' at row index ' + str(index) if index else ''}"
            logging.error(f"----|Failed| Roster Creation : {message}")
            messages.error(request, message)
        except Roster.DoesNotExist:
            logging.info("----No conflicting roster found, creating new roster.")
            try:
                roster = Roster(
                    employee=data["employee"],
                    shiftLegend=data["shift_legend"],
                    process=data["process"],
                    gender=data["gender"],
                    site=data["site"],
                    work_role=data["work_role"],
                    lob=data["lob"],
                    pick_drop_location=data["pick_drop_location"],
                    start_date=data["start_date"],
                    start_time=data["start_time"],
                    end_date=data["end_date"],
                    end_time=data["end_time"],
                    supervisor_1=data["supervisor_1"],
                    supervisor_2=data["supervisor_2"],
                    created_by=CustomUser.objects.get(id=request.user.id),
                )
                logging.info(f"----Trying to create Roster Count")
                if createRosterCount(roster):
                    roster.save()
                    success = True
                    logging.info(f"----|Success| Roster Created Successfully")
                else:
                    message = f"Failed to create RosterCount {' at row index ' + str(index) if index else ''}"
                    logging.error(f"----|Failed| {message}")
                    messages.error(request, message)
            except Exception as e:
                logging.error(f"----|Failed| Failed to create Roster. Exception:{e}")
                messages.error(
                    request,
                    f"Failed to create Roster{' at row index ' + str(index) if index else ''}",
                )
    except Exception as e:
        logging.error(f"----|Failed| Failed to create Roster. Exception:{e}")
        messages.error(
            request,
            f"Failed to create Roster{' at row index ' + str(index) if index else ''}",
        )

    return success


def rosterModification(id, data):
    """Modify a Roster

    Args:
        id (int): Id of the roster
        data (_type_): Roster Modification Data


    Returns:
        bool: If the Modification is successful or not
    """
    roster = Roster.objects.get(id=id)
    logging.info(f"Trying to update Roster{id} : {roster}")
    success = False
    try:
        roster.start_date = data["start_date"]
        roster.start_time = data["start_time"]
        roster.end_date = data["end_date"]
        roster.end_time = data["end_time"]
        roster.save()
        logging.info("|Success| Roster updated successfully")
        success = True
    except Exception as e:
        logging.info(f"|Failed| Exception: {e}")
    return success


def rosterSeatCountCreation(data, request):
    """Create a Roster Seat Count

    Args:
        data (_type_): Roster Seat Count Creation Data
        request (_type_): Request from view

    Returns:
        bool: If the creation is successful or not
    """
    success = False
    try:
        rosterSeatCount = RosterSeatCount.objects.get(
            site=data["site"],
            process=data["process"],
            lob=data["lob"],
        )
    except RosterSeatCount.DoesNotExist:
        try:
            rosterSeatCount = RosterSeatCount(
                site=data["site"],
                process=data["process"],
                lob=data["lob"],
                total=data["total"],
                created_by=CustomUser.objects.get(id=request.user.id),
            )
            rosterSeatCount.save()
            success = True
            logging.info(f"|Success| Roster Seat Count Created Successfully")
        except Exception as e:
            logging.info(f"|Failed| Failed to create Roster Seat Count. Exception:{e}")
            messages.error(request, "Failed to create Roster Seat Count")
    except Exception as e:
        logging.info(f"|Failed| Failed to create Roster Seat Count. Exception:{e}")
        messages.error(request, "Failed to create Roster Seat Count")
    return success


def rosterSeatCountEdit(id, data, updated_by):
    """Edit a Roster Seat Count

    Args:
        data (_type_): Roster Seat Count Creation Data
        request (_type_): Request from view

    Returns:
        bool: If the creation is successful or not
    """
    success = False
    try:
        instance = RosterSeatCount.objects.get(id=id)
        try:
            instance.site = data["site"]
            instance.process = data["process"]
            instance.lob = data["lob"]
            instance.total = data["total"]
            instance.updated_by = CustomUser.objects.get(id=updated_by)
            instance.save()
            success = True
            logging.info(f"|Success| Roster Seat Count Created Successfully")
        except Exception as e:
            logging.info(f"|Failed| Failed to create Roster Seat Count. Exception:{e}")
    except RosterSeatCount.DoesNotExist:
        logging.error(f"|Failed| Roster Seat Count with ID {id} does not exist.")
    except Exception as e:
        logging.info(f"|Failed| Failed to create Roster Seat Count. Exception:{e}")
    return success


def forecastingCreation(data, request):
    """Create a Forecasting

    Args:
        data (_type_): Forecasting Creation Data
        request (_type_): Request from view

    Returns:
        bool: If the creation is successful or not
    """
    success = False
    try:
        forecastingInstance = Forecast.objects.get(
            date=data["date"],
            process=data["process"],
            lob=data["lob"],
            interval=data["interval"],
        )
    except Forecast.DoesNotExist:
        try:
            forecastingInstance = Forecast(
                date=data["date"],
                process=data["process"],
                lob=data["lob"],
                interval=data["interval"],
                forecast=data["forecast"],
                required_hc=data["required_hc"],
                created_by=CustomUser.objects.get(id=request.user.id),
            )
            forecastingInstance.save()
            success = True
            logging.info(f"|Success| Forecasting Created Successfully")
        except Exception as e:
            logging.info(f"|Failed| Forecasting already exists. Exception:{e}")
    except Exception as e:
        logging.info(f"|Failed| Failed to create Forecasting. Exception:{e}")
    return success


def shiftLegendCreation(data, request):
    """Create a Shift Legend

    Args:
        data (_type_): Shift Legend Creation Data
        request (_type_): Request from view

    Returns:
        bool: If the creation is successful or not
    """
    success = False
    try:
        if data["shift_count"] != 0:
            shiftLegendInstance = ShiftLegend.objects.get(
                shift_start_time=data["shift_start_time"],
                shift_end_time=data["shift_end_time"],
            )
        else:
            shiftLegendInstance = ShiftLegend.objects.get(
                shift_name=data["shift_name"],
            )
    except ShiftLegend.DoesNotExist:
        data["created_by"] = CustomUser.objects.get(id=request.user.id)
        if data["shift_count"] != 0:
            try:
                shiftLegendInstance = ShiftLegend.objects.create(**data)
                success = True
                logging.info(f"|Success| Shift Legend Created Successfully")
            except Exception as e:
                message = traceback.format_exc()
                logging.info(
                    f"|Failed| Failed to create Shift Legend. Exception:{e} | Traceback:{message}"
                )
        else:
            try:
                shiftLegendInstance = ShiftLegend.objects.create(**data)
                success = True
                logging.info(f"|Success| Shift Legend Created Successfully")
            except Exception as e:
                message = traceback.format_exc()
                logging.info(
                    f"|Failed| Failed to create Shift Legend. Exception:{e} | Traceback:{message}"
                )
    except Exception as e:
        message = traceback.format_exc()
        logging.info(
            f"|Failed| Failed to create Shift Legend. Exception:{e} | Traceback:{message}"
        )
    return success


def forecastingModification(id, data):
    """Modify a Forecast

    Args:
        id (int): Id of the forecast
        data (_type_): Roster Modification Data


    Returns:
        bool: If the Modification is successful or not
    """
    forecastInstance = Forecast.objects.get(id=id)
    logging.info(f"Trying to update Forecast{id} : {forecastInstance}")
    success = False
    try:
        forecastInstance.date = data["date"]
        forecastInstance.process = data["process"]
        forecastInstance.lob = data["lob"]
        forecastInstance.interval = data["interval"]
        forecastInstance.forecast = data["forecast"]
        forecastInstance.required_hc = data["required_hc"]
        forecastInstance.save()
        logging.info("|Success| Forecast updated successfully")
        success = True
    except Exception as e:
        logging.info(f"|Failed| Exception: {e}")
    return success


def shiftLegendModification(id, data):
    """Modify a Shift Legend

    Args:
        id (int): Id of the shift Legend
        data (_type_): Roster Modification Data


    Returns:
        bool: If the Modification is successful or not
    """
    shiftLegendInstance = ShiftLegend.objects.get(id=id)
    logging.info(f"Trying to update Shift Legend{id} : {shiftLegendInstance}")
    success = False
    try:
        # Update the instance with the new data
        for key, value in data.items():
            setattr(shiftLegendInstance, key, value)
        shiftLegendInstance.clean()
        shiftLegendInstance.save()
        logging.info("|Success| Shift Legend updated successfully")
        success = True
    except Exception as e:
        logging.info(f"|Failed| Exception: {e}")
    return success


def isTimeRange(value):
    return "-" in value and len(value.split("-")) == 2


def formatTimeToAmPm(timeString):
    timeObject = parse_time(timeString)
    if timeObject:
        return time_format(timeObject, "g:i A")
    return timeString


def formatShiftLegend(value):
    if isTimeRange(value):
        startTime, endTime = value.split("-")
        formattedStart = formatTimeToAmPm(startTime)
        formattedEnd = formatTimeToAmPm(endTime)
        return f"{formattedStart} - {formattedEnd}"
    return value


def convertTimeRange(start_time, end_time):
    """
    Convert start and end times to the format "HHMM-HHMM".

    Args:
        start_time (datetime): The start time.
        end_time (datetime): The end time.

    Returns:
        str: The time range in "HHMM-HHMM" format.
    """
    start_str = start_time.strftime("%H%M")
    end_str = end_time.strftime("%H%M")
    return f"{start_str}-{end_str}"
