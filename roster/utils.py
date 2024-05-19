from .models import Roster, RosterCount, RosterSeatCount, Forecast, ShiftLegend
from accounts.models import Employee
from django.contrib import messages
from accounts.models import CustomUser
import logging
import traceback
from accounts.models import *

logger = logging.getLogger(__name__)


def createRosterCount(roster):
    """Create or update RosterCount Instance

    Args:
        roster (Roster): _description_

    Returns:
        boolean: success or failure of the execution
    """
    logger.info(f"Trying to create RosterCount of {roster} id:|{roster.id}|")
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
            logger.info(f"|Success| Roster Count Updated Successfully")
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
                logger.info(f"|Success| Roster Count Created Successfully")
            except Exception as e:
                logger.info(f"|Failed| Roster Count Creation failed.Exception: {e}")
    else:
        success = True
        logger.info(f"|Success| Did not create Roster Count as start time is none")
    return success


def rosterCreation(data, request):
    """Create a Roster

    Args:
        data (_type_): Roster Creation Data
        request (_type_): Request from view

    Returns:
        bool: If the creation is successful or not
    """
    success = False
    try:
        roster = Roster.objects.get(
            employee=data["employee"],
            start_date=data["start_date"],
            start_time=data["start_time"],
            end_date=data["end_date"],
            end_time=data["end_time"],
        )
    except Roster.DoesNotExist:
        try:
            roster = Roster.objects.get(
                employee=data["employee"], start_date=data["start_date"]
            )
            message = f"A Roster on {roster.start_date.strftime('%d-%m-%Y')} exists of {roster.employee.user.name}"
            logger.info(f"|Failed| {message}")
            messages.error(request, message)
        except Roster.DoesNotExist:
            process = (
                None
                if data["process"] is None
                else Process.objects.get(name=data["process"].lower())
            )
            site = (
                None
                if data["site"] is None
                else Site.objects.get(name=data["site"].lower())
            )
            workRole = (
                None
                if data["work_role"] is None
                else WorkRole.objects.get(name=data["work_role"].lower())
            )
            lob = (
                None
                if data["lob"] is None
                else LOB.objects.get(name=str(data["lob"]).lower())
            )
            try:
                roster = Roster(
                    employee=data["employee"],
                    shiftLegend=data["shiftLegend"],
                    process=process,
                    gender=data["gender"],
                    site=site,
                    work_role=workRole,
                    lob=lob,
                    pick_drop_location=["pick_drop_location"],
                    start_date=data["start_date"],
                    start_time=data["start_time"],
                    end_date=data["end_date"],
                    end_time=data["end_time"],
                    supervisor_1=data["supervisor_1"],
                    created_by=CustomUser.objects.get(id=request.user.id),
                )

                logger.info(f"--Trying to create Roster Count")
                rosterCountCreationResult = createRosterCount(roster)
                if rosterCountCreationResult is True:
                    success = True
                    roster.save()
                    logger.info(f"|Success| Roster Created Successfully")
                else:
                    with open("newfile.txt", "a+") as file:
                        file.write(f"--{data}\n Roster Count Creation result")
                    logger.info(f"|Failed| Failed to create Roster")
            except Exception as e:
                with open("newfile.txt", "a+") as file:
                    file.write(f"--{data}\n Roster Creation Exception:{e}")
                logger.info(f"|Failed| Failed to create Roster. Exception:{e}")
                messages.error(request, "Failed to create Roster")
    except Exception as e:
        with open("newfile.txt", "a+") as file:
            file.write(f"--{data}\n Failed to create Roster. Exception:{e}")
        logger.info(f"|Failed| Failed to create Roster. Exception:{e}")
        messages.error(request, "Failed to create Roster")
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
    logger.info(f"Trying to update Roster{id} : {roster}")
    success = False
    try:
        roster.start_date = data["start_date"]
        roster.start_time = data["start_time"]
        roster.end_date = data["end_date"]
        roster.end_time = data["end_time"]
        roster.save()
        logger.info("|Success| Roster updated successfully")
        success = True
    except Exception as e:
        logger.info(f"|Failed| Exception: {e}")
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
            logger.info(f"|Success| Roster Seat Count Created Successfully")
        except Exception as e:
            logger.info(f"|Failed| Failed to create Roster Seat Count. Exception:{e}")
            messages.error(request, "Failed to create Roster Seat Count")
    except Exception as e:
        logger.info(f"|Failed| Failed to create Roster Seat Count. Exception:{e}")
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
            logger.info(f"|Success| Roster Seat Count Created Successfully")
        except Exception as e:
            logger.info(f"|Failed| Failed to create Roster Seat Count. Exception:{e}")
    except RosterSeatCount.DoesNotExist:
        logger.error(f"|Failed| Roster Seat Count with ID {id} does not exist.")
    except Exception as e:
        logger.info(f"|Failed| Failed to create Roster Seat Count. Exception:{e}")
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
            logger.info(f"|Success| Forecasting Created Successfully")
        except Exception as e:
            logger.info(f"|Failed| Forecasting already exists. Exception:{e}")
    except Exception as e:
        logger.info(f"|Failed| Failed to create Forecasting. Exception:{e}")
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
                logger.info(f"|Success| Shift Legend Created Successfully")
            except Exception as e:
                message = traceback.format_exc()
                logger.info(
                    f"|Failed| Failed to create Shift Legend. Exception:{e} | Traceback:{message}"
                )
        else:
            try:
                shiftLegendInstance = ShiftLegend.objects.create(**data)
                success = True
                logger.info(f"|Success| Shift Legend Created Successfully")
            except Exception as e:
                message = traceback.format_exc()
                logger.info(
                    f"|Failed| Failed to create Shift Legend. Exception:{e} | Traceback:{message}"
                )
    except Exception as e:
        message = traceback.format_exc()
        logger.info(
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
    logger.info(f"Trying to update Forecast{id} : {forecastInstance}")
    success = False
    try:
        forecastInstance.date = data["date"]
        forecastInstance.process = data["process"]
        forecastInstance.lob = data["lob"]
        forecastInstance.interval = data["interval"]
        forecastInstance.forecast = data["forecast"]
        forecastInstance.required_hc = data["required_hc"]
        forecastInstance.save()
        logger.info("|Success| Forecast updated successfully")
        success = True
    except Exception as e:
        logger.info(f"|Failed| Exception: {e}")
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
    logger.info(f"Trying to update Shift Legend{id} : {shiftLegendInstance}")
    success = False
    try:
        # Update the instance with the new data
        for key, value in data.items():
            setattr(shiftLegendInstance, key, value)
        shiftLegendInstance.clean()
        shiftLegendInstance.save()
        logger.info("|Success| Shift Legend updated successfully")
        success = True
    except Exception as e:
        logger.info(f"|Failed| Exception: {e}")
    return success
