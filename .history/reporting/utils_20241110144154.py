from .models import *
from accounts.models import CustomUser
import logging
import traceback
from django.utils.timezone import make_aware
from django.db.models import Sum, F, Subquery, OuterRef
from django.db.models import Sum, F, Case, When, Value, IntegerField, BooleanField
from django.db.models import Sum, F, Case, When, Value, IntegerField, Q
import datetime
import calendar
import time

logger = logging.getLogger(__name__)


def avayaCDRCreation(data, request):
    """Create a Avaya CDR

    Args:
        data (_type_): Avaya CDR Creation Data
        request (_type_): Request from view

    Returns:
        bool: If the creation is successful or not
    """
    success = False
    try:
        avayaCDRInstance = AvayaCDR.objects.get(
            date=data["date"],
            skill=data["skill"],
            time_interval=data["time_interval"],
        )
        logger.info(f"|Failed| Avaya CDR already exists")
    except AvayaCDR.DoesNotExist:
        data["created_by"] = CustomUser.objects.get(id=request.user.id)
        try:
            avayaCDRInstance = AvayaCDR.objects.create(**data)
            success = True
            logger.info(f"|Success| Avaya CDR Created Successfully")
        except Exception as e:
            message = traceback.format_exc()
            logger.info(
                f"|Failed| Failed to create Avaya CDR. Exception:{e} | Traceback:{message}"
            )
    except Exception as e:
        message = traceback.format_exc()
        logger.info(
            f"|Failed| Failed to create Avaya CDR. Exception:{e} | Traceback:{message}"
        )
    return success


def agentHourlyPerformanceCreation(data, request):
    """Create a Agent Hourly Performance

    Args:
        data (_type_): Agent Hourly Performance Creation Data
        request (_type_): Request from view

    Returns:
        bool: If the creation is successful or not
    """
    success = False
    # try:
    #     agentHourlyPerformanceInstance = AgentHourlyPerformance.objects.get(
    #         date=data["date"],
    #         skill=data["skill"],
    #         employee=data["employee"],
    #         time_interval_start=data["time_interval_start"],
    #     )
    #     logger.info(f"|Failed| Agent Hourly Performance already exists")
    # except AgentHourlyPerformance.DoesNotExist:
    #     data["created_by"] = CustomUser.objects.get(id=request.user.id)
    #     try:
    #         agentHourlyPerformanceInstance = AgentHourlyPerformance.objects.create(
    #             **data
    #         )
    #         success = True
    #         logger.info(f"|Success| Agent Hourly Performance Created Successfully")
    #     except Exception as e:
    #         message = traceback.format_exc()
    #         logger.info(
    #             f"|Failed| Failed to create Agent Hourly Performance. Exception:{e} | Traceback:{message}"
    #         )
    # except Exception as e:
    #     message = traceback.format_exc()
    #     logger.info(
    #         f"|Failed| Failed to create Agent Hourly Performance. Exception:{e} | Traceback:{message}"
    #     )
    data["created_by"] = CustomUser.objects.get(id=request.user.id)
    try:
        agentHourlyPerformanceInstance = AgentHourlyPerformance.objects.create(**data)
        success = True
        logger.info(f"|Success| Agent Hourly Performance Created Successfully")
    except Exception as e:
        message = traceback.format_exc()
        logger.info(
            f"|Failed| Failed to create Agent Hourly Performance. Exception:{e} | Traceback:{message}"
        )
    return success


def loginLogoutTimeCreation(data, request):
    """Create a Login Logout Time

    Args:
        data (_type_): Login Logout Time Creation Data
        request (_type_): Request from view

    Returns:
        bool: If the creation is successful or not
    """
    success = False
    try:
        login_time = make_aware(data["login_time"])
        logout_time = make_aware(data["logout_time"])
        loginLogoutTimeInstance = LoginLogoutTime.objects.get(
            employee=data["employee"],
            login_time=login_time,
            logout_time=logout_time,
        )
        logger.info(f"|Failed| Login Logout Time already exists")
    except LoginLogoutTime.DoesNotExist:
        data["created_by"] = CustomUser.objects.get(id=request.user.id)
        # Make sure login_time and logout_time are aware
        data["login_time"] = make_aware(data["login_time"])
        data["logout_time"] = make_aware(data["logout_time"])
        try:
            loginLogoutTimeInstance = LoginLogoutTime.objects.create(**data)
            success = True
            logger.info(f"|Success|Login Logout Time Created Successfully")
        except Exception as e:
            message = traceback.format_exc()
            logger.info(
                f"|Failed| Failed to create Login Logout Time. Exception:{e} | Traceback:{message}"
            )
    except Exception as e:
        message = traceback.format_exc()
        logger.info(
            f"|Failed| Failed to create Login Logout Time. Exception:{e} | Traceback:{message}"
        )
    return success


def getAvayaCDRMappingByDate(date, skill):
    """Get Avaya CDR mapping

    Args:
        date (datetime): date
        skill (Skill): selected skill

    Returns:
        dict: Avaya CDR mapping
    """
    start_time = time.time()
    logger.info("Fetching Avaya CDR mapping for date: %s, skill: %s", date, skill)

    try:
        avayaCDRResult = (
            AvayaCDR.objects.filter(date=date, skill=skill)
            .values("hour")
            .annotate(
                offeredCalls=Sum("offer"),
                answeredCalls=Sum("answer"),
                handlingTime=Sum("acd_time") + Sum("acw_time") + Sum("hold_time"),
            )
        )
        logger.info("Avaya CDR result retrieved with %d records", len(avayaCDRResult))

        avayaCDRMapping = {
            item["hour"]: {
                "offeredCalls": item["offeredCalls"],
                "answeredCalls": item["answeredCalls"],
                "aht": (
                    format(item["handlingTime"] / item["answeredCalls"], ".2f")
                    if item["answeredCalls"]
                    else "0.00"
                ),
            }
            for item in avayaCDRResult
        }
        logger.info("Successfully created Avaya CDR mapping")

    except Exception as e:
        logger.error(
            "Error fetching Avaya CDR mapping for date: %s, skill: %s - %s",
            date,
            skill,
            e,
        )
        avayaCDRMapping = {}

    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(
        "Execution time for getAvayaCDRMappingByDate: %.4f seconds", elapsed_time
    )

    return avayaCDRMapping


def getAvayaCDRMappingByMonth(month, year, skill):
    """Get Avaya CDR mapping

    Args:
        month (int): month
        year (int): year
        skill (Skill): selected skill

    Returns:
        dict: Avaya CDR mapping
    """
    # Start the timer to calculate execution time
    start_time = time.time()

    logger.info(
        f"Starting to fetch Avaya CDR data for Month: {month}, Year: {year}, Skill: {skill.name}"
    )

    avayaCDRResult = (
        AvayaCDR.objects.filter(date__month=month, date__year=year, skill=skill)
        .values("date")
        .annotate(
            offeredCalls=Sum("offer"),
            answeredCalls=Sum("answer"),
            handlingTime=Sum("acd_time") + Sum("acw_time") + Sum("hold_time"),
        )
    )
    logger.info(f"Fetched {avayaCDRResult.count()} records from the database.")

    avayaCDRMapping = {
        item["date"].strftime("%Y-%m-%d"): {
            "offeredCalls": item["offeredCalls"],
            "answeredCalls": item["answeredCalls"],
            "aht": format(item["handlingTime"] / item["answeredCalls"], ".2f"),
        }
        for item in avayaCDRResult
    }
    logger.info(
        f"Data mapped successfully. Number of days processed: {len(avayaCDRMapping)}"
    )
    # Calculate execution time
    execution_time = time.time() - start_time
    logger.info(
        f"Execution time for fetching and processing Avaya CDR data: {execution_time:.4f} seconds"
    )

    return avayaCDRMapping


def getAgentHourlyPerformanceMapping(date, skill):
    """Get Agent Hourly Performance Mapping

    Args:
        date (datetime): date
        skill (Skill): selected skill

    Returns:
        dict: Agent Hourly Performance Mapping
    """
    agentHourlyPerformances = AgentHourlyPerformance.objects.filter(
        date=date,
        skill=skill,
    )

    # Get the field names dynamically (excluding 'hour' and 'id')
    fieldNames = [
        field.name
        for field in AgentHourlyPerformance._meta.get_fields()
        if field.name
        not in [
            "date",
            "employee",
            "skill",
            "hour",
            "id",
            "time_interval_start",
            "time_interval_end",
            "created_by",
            "updated_by",
            "created_At",
            "updated_At",
        ]
    ]

    # Create a dictionary to store the sums for each field
    sums = {field_name: Sum(F(field_name)) for field_name in fieldNames}

    # Sum the values for each field based on the 'hour' column
    aggregated_data = agentHourlyPerformances.values("hour").annotate(**sums)

    agentHourlyPerformanceMapping = {
        performance["hour"]: performance for performance in aggregated_data
    }

    return agentHourlyPerformanceMapping, fieldNames


def getAgentHourlyPerformanceMappingWithRosterNew(date, skill):
    """Get Agent Hourly Performance Mapping

    Args:
        date (datetime): date
        skill (Skill): selected skill

    Returns:
        dict: Agent Hourly Performance Mapping
    """
    start_time = time.time()
    logger.info(
        "Fetching Agent Hourly Performance mapping for date: %s, skill: %s", date, skill
    )

    # Initialize dictionary to store results
    agentHourlyPerformanceMapping = {
        hour: {"shiftCount": 0, "absent": 0} for hour in range(24)
    }

    try:
        # Aggregate `shiftCount` and `absent` directly in the database using a single query
        aggregated_data = (
            AgentHourlyPerformance.objects.filter(date=date, skill=skill)
            .values("hour")
            .annotate(
                shiftCount=Sum("roster__shiftLegend__shift_count"),
                absent=Sum(
                    Case(
                        When(roster__is_absent=True, then=1),
                        output_field=IntegerField(),
                    )
                ),
            )
        )

        # Populate the mapping with results from the aggregation
        for data in aggregated_data:
            hour = data["hour"]
            agentHourlyPerformanceMapping[hour]["shiftCount"] = data["shiftCount"] or 0
            agentHourlyPerformanceMapping[hour]["absent"] = data["absent"] or 0
            logger.debug(
                "Hour %d | Shift Count: %d | Absent: %d",
                hour,
                data["shiftCount"] or 0,
                data["absent"] or 0,
            )

        logger.info("Successfully created Agent Hourly Performance mapping")

    except Exception as e:
        logger.error(
            "Error fetching Agent Hourly Performance mapping for date: %s, skill: %s - %s",
            date,
            skill,
            e,
        )

    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(
        "Execution time for getAgentHourlyPerformanceMappingWithRoster: %.4f seconds",
        elapsed_time,
    )

    return agentHourlyPerformanceMapping


def getAgentHourlyPerformanceMappingWithRosterOld(date, skill):
    """Get Agent Hourly Performance Mapping

    Args:
        date (datetime): date
        skill (Skill): selected skill

    Returns:
        dict: Agent Hourly Performance Mapping
    """
    start_time = time.time()
    logger.info(
        "Fetching Agent Hourly Performance mapping for date: %s, skill: %s", date, skill
    )
    hour_list = list(range(24))
    agentHourlyPerformanceMapping = {}
    for hour in hour_list:
        if hour == 1:
            pass
            # print(f"Hour - {hour}")
        shiftCount = 0
        absent = 0
        tempShiftCount = 0
        tempAbsent = 0
        # Filter agentHourlyPerformances for the current hour
        agentHourlyPerformances = AgentHourlyPerformance.objects.filter(
            date=date, skill=skill, hour=hour
        ).select_related(
            "roster__shiftLegend"
        )  # Fetch related ShiftLegend objects

        if hour == 1:
            pass
            # print("------")
            # rosterList = []
            # for agentHourlyPerformance in agentHourlyPerformances:
            #     roster = Roster.objects.get(
            #         employee=agentHourlyPerformance.employee,
            #         start_date=agentHourlyPerformance.date,
            #     )

            #     if roster.id not in rosterList:
            #         #print(roster)
            #         #print(
            #             f"ShiftLegend- {roster.shiftLegend} | ID- {roster.shiftLegend.id}"
            #         )
            #         rosterList.append(roster.id)

            #         hour_column_name = f"hour_{hour}"
            #         hour_value = getattr(roster.shiftLegend, hour_column_name)

            #         # #print(hour_value)
            #         if hour_value is True:
            #             tempShiftCount += 1
            #         if hour_value is None:
            #             tempAbsent += 1
            #     # **{f"roster__shiftLegend__hour_{hour}": True},
            #     # start_time__gte=agentHourlyPerformance.time_interval_start,
            #     # end_time__lte=agentHourlyPerformance.time_interval_end,
            # #print(f"ShiftCount: {tempShiftCount} | Absent: {tempAbsent}")
            # print("------")
            # #print(
            #     f"Initial agentHourlyPerformances count {agentHourlyPerformances.count()}"
            # )
            # for item in agentHourlyPerformances:
            #     #print(
            #         f"ahp_id- {item.id} {item.roster_id} - {item.roster.shiftLegend.shift_name}"
            #     )
        # Get the distinct roster IDs for the current hour
        unique_roster_ids = (
            agentHourlyPerformances.values_list("roster_id", flat=True)
            .filter(roster_id__isnull=False)
            .distinct()
        )
        logger.info(f"unique_roster_ids count {unique_roster_ids.count()}")
        if hour == 1:
            # print(f"unique_roster_ids count {unique_roster_ids.count()}")
            pass
        for item in unique_roster_ids:
            # print(item)
            roster = Roster.objects.get(id=item)
            shiftCount += roster.shiftLegend.shift_count
            absent += roster.is_absent
            if hour == 1:
                # print(f"roster: {roster.id} | shift name: {roster.shiftLegend.shift_name}")
                pass
        if hour == 1:
            pass
            # print(f"ShiftCount: {shiftCount} | Absent: {absent}")

        # Update the agentHourlyPerformanceMapping dictionary with the aggregated data for this hour
        # agentHourlyPerformanceMapping[hour] = {
        #     performance["hour"]: performance for performance in aggregated_data
        # }
        agentHourlyPerformanceMapping[hour] = {
            "shiftCount": shiftCount,
            "absent": absent,
        }

    # #print("Values in agentHourlyPerformanceMapping:")
    # for value in agentHourlyPerformanceMapping.values():
    #     #print(value)
    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(
        "Execution time for getAgentHourlyPerformanceMappingWithRoster: %.4f seconds",
        elapsed_time,
    )
    return agentHourlyPerformanceMapping


def getAgentHourlyPerformanceMappingWithRoster(date, skill):
    """Get Agent Hourly Performance Mapping

    Args:
        date (datetime): date
        skill (Skill): selected skill

    Returns:
        dict: Agent Hourly Performance Mapping
    """
    start_time = time.time()
    logger.info(
        "Fetching Agent Hourly Performance mapping for date: %s, skill: %s", date, skill
    )
    hour_list = list(range(24))
    agentHourlyPerformanceMapping = {}
    # Iterate over hours
    agentHourlyPerformances = (
        AgentHourlyPerformance.objects.filter(date=date, skill=skill)
        .filter(roster_id__isnull=False)
        .select_related("roster__shiftLegend")  # Fetch related ShiftLegend data
        .values(
            "hour", "roster_id", "roster__shiftLegend__shift_count", "roster__is_absent"
        )
    )

    logger.info("Fetching Agent Hourly Performances completed")

    # Initialize a dictionary to store shift count and absence for each hour
    hourly_data = {hour: {"shiftCount": 0, "absent": 0} for hour in range(24)}

    # Initialize a set to track unique rosters per hour
    unique_rosters_per_hour = {hour: set() for hour in range(24)}

    logger.info("Aggregating data for each hour...")

    # Iterate over the fetched records and aggregate data by hour and roster
    for item in agentHourlyPerformances:
        hour = item["hour"]
        roster_id = item["roster_id"]

        # Ensure the roster is counted only once per hour
        if roster_id not in unique_rosters_per_hour[hour]:
            unique_rosters_per_hour[hour].add(roster_id)

            # Aggregate the shift count and absence
            shift_count = item["roster__shiftLegend__shift_count"] or 0
            absent = item["roster__is_absent"] or 0

            # Update the hourly data with the aggregated values
            hourly_data[hour]["shiftCount"] += shift_count
            hourly_data[hour]["absent"] += absent

            # Log each roster data that is being processed
            logger.debug(
                f"Hour: {hour} | Roster ID: {roster_id} | ShiftCount: {shift_count} | Absent: {absent}"
            )

    logger.info("Data aggregation completed")

    # Now, we can log the data for each hour and update the final mapping
    agentHourlyPerformanceMapping = {}

    logger.info("Logging the aggregated results for each hour:")
    for hour, data in hourly_data.items():
        logger.info(
            f"Hour: {hour} | ShiftCount: {data['shiftCount']} | Absent: {data['absent']}"
        )
        print(
            f"Hour: {hour} | ShiftCount: {data['shiftCount']} | Absent: {data['absent']}"
        )

        # Store the results in the final mapping
        agentHourlyPerformanceMapping[hour] = {
            "shiftCount": data["shiftCount"],
            "absent": data["absent"],
        }

    logger.info("Final Agent Hourly Performance Mapping completed")

    # #print("Values in agentHourlyPerformanceMapping:")
    # for value in agentHourlyPerformanceMapping.values():
    #     #print(value)
    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(
        "Execution time for getAgentHourlyPerformanceMappingWithRoster: %.4f seconds",
        elapsed_time,
    )
    return agentHourlyPerformanceMapping


def getAgentHourlyPerformanceMappingWithRosterOptimized(date, skill):
    """Get Agent Hourly Performance Mapping with optimized query but equivalent result to original.

    Args:
        date (datetime): date
        skill (Skill): selected skill

    Returns:
        dict: Agent Hourly Performance Mapping
    """
    start_time = time.time()
    logger.info(
        "Fetching Agent Hourly Performance mapping for date: %s, skill: %s", date, skill
    )

    # Initialize dictionary to store results for each hour
    agentHourlyPerformanceMapping = {
        hour: {"shiftCount": 0, "absent": 0} for hour in range(24)
    }

    try:
        # Aggregate shift counts and absence flags for each hour in a single query
        aggregated_data = (
            AgentHourlyPerformance.objects.filter(date=date, skill=skill)
            .values("hour")
            .annotate(
                shiftCount=Sum("roster__shiftLegend__shift_count"),
                absent=Sum(
                    Case(
                        When(roster__is_absent=True, then=1),
                        default=0,
                        output_field=IntegerField(),
                    )
                ),
            )
        )

        # Populate the mapping based on aggregated data
        for data in aggregated_data:
            hour = data["hour"]
            # Set values from the aggregation, falling back to 0 if None
            agentHourlyPerformanceMapping[hour]["shiftCount"] = data["shiftCount"] or 0
            agentHourlyPerformanceMapping[hour]["absent"] = data["absent"] or 0
            logger.debug(
                "Hour %d | Shift Count: %d | Absent: %d",
                hour,
                agentHourlyPerformanceMapping[hour]["shiftCount"],
                agentHourlyPerformanceMapping[hour]["absent"],
            )

        # Log success
        logger.info("Successfully created Agent Hourly Performance mapping")

    except Exception as e:
        logger.error(
            "Error fetching Agent Hourly Performance mapping for date: %s, skill: %s - %s",
            date,
            skill,
            e,
        )

    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(
        "Execution time for getAgentHourlyPerformanceMappingWithRoster: %.4f seconds",
        elapsed_time,
    )

    return agentHourlyPerformanceMapping


def getAgentHourlyPerformanceMappingWithRosterExact(date, skill):
    """Get Agent Hourly Performance Mapping with per-hour roster checks for exact results.

    Args:
        date (datetime): date
        skill (Skill): selected skill

    Returns:
        dict: Agent Hourly Performance Mapping
    """
    start_time = time.time()
    logger.info(
        "Fetching Agent Hourly Performance mapping for date: %s, skill: %s", date, skill
    )

    # Initialize the results dictionary with placeholders for each hour
    agentHourlyPerformanceMapping = {
        hour: {"shiftCount": 0, "absent": 0} for hour in range(24)
    }

    try:
        # Fetch all AgentHourlyPerformance entries and related rosters for given date, skill
        agentHourlyPerformances = (
            AgentHourlyPerformance.objects.filter(date=date, skill=skill)
            .select_related("roster__shiftLegend")
            .only("hour", "roster__shiftLegend__shift_count", "roster__is_absent")
        )

        # Organize by hour, count unique rosters per hour, calculate shift count and absence
        hourly_data = {}
        for ahp in agentHourlyPerformances:
            hour = ahp.hour
            if hour not in hourly_data:
                hourly_data[hour] = {"shiftCount": 0, "absent": 0}

            # Track unique rosters per hour, ensuring no duplicates
            roster = ahp.roster
            if roster and roster.id not in hourly_data[hour]:
                hourly_data[hour][
                    roster.id
                ] = True  # Store seen rosters to avoid duplicates
                hourly_data[hour]["shiftCount"] += roster.shiftLegend.shift_count
                hourly_data[hour]["absent"] += int(roster.is_absent)

        # Finalize the results in the dictionary
        for hour, data in hourly_data.items():
            agentHourlyPerformanceMapping[hour]["shiftCount"] = data["shiftCount"]
            agentHourlyPerformanceMapping[hour]["absent"] = data["absent"]
            logger.debug(
                "Hour %d | Shift Count: %d | Absent: %d",
                hour,
                data["shiftCount"],
                data["absent"],
            )

        logger.info("Successfully created Agent Hourly Performance mapping")

    except Exception as e:
        logger.error(
            "Error fetching Agent Hourly Performance mapping for date: %s, skill: %s - %s",
            date,
            skill,
            e,
        )

    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(
        "Execution time for getAgentHourlyPerformanceMappingWithRosterExact: %.4f seconds",
        elapsed_time,
    )

    return agentHourlyPerformanceMapping


def getAgentHourlyPerformanceMappingWithRosterByMonth(month, year, skill):
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


def generate_hour_table_data():
    return [
        {"interval": "0", "hour": "0-1"},
        {"interval": "1", "hour": "1-2"},
        {"interval": "2", "hour": "2-3"},
        {"interval": "3", "hour": "3-4"},
        {"interval": "4", "hour": "4-5"},
        {"interval": "5", "hour": "5-6"},
        {"interval": "6", "hour": "6-7"},
        {"interval": "7", "hour": "7-8"},
        {"interval": "8", "hour": "8-9"},
        {"interval": "9", "hour": "9-10"},
        {"interval": "10", "hour": "10-11"},
        {"interval": "11", "hour": "11-12"},
        {"interval": "12", "hour": "12-13"},
        {"interval": "13", "hour": "13-14"},
        {"interval": "14", "hour": "14-15"},
        {"interval": "15", "hour": "15-16"},
        {"interval": "16", "hour": "16-17"},
        {"interval": "17", "hour": "17-18"},
        {"interval": "18", "hour": "18-19"},
        {"interval": "19", "hour": "19-20"},
        {"interval": "20", "hour": "20-21"},
        {"interval": "21", "hour": "21-22"},
        {"interval": "22", "hour": "22-23"},
        {"interval": "23", "hour": "23-24"},
    ]


def generate_date_table_data(month, year):
    """Generate date table data for the given month and year

    Args:
        month (int): month
        year (int): year

    Returns:
        list: Table data with date intervals
    """
    # Start the timer to calculate execution time
    start_time = time.time()

    logger.info(
        f"Starting to generate date table data for Month: {month}, Year: {year}"
    )

    # Get the number of days in the given month using calendar.monthrange
    num_days = calendar.monthrange(year, month)[1]
    logger.info(f"Number of days in {month}/{year}: {num_days}")

    # Generate table data with dates for the given month
    table_data = []
    for day in range(1, num_days + 1):
        # Create a new date object for each iteration
        date_obj = datetime.date(year, month, day)
        table_data.append({"interval": day, "date": date_obj.strftime("%Y-%m-%d")})

    logger.info(f"Generated {len(table_data)} rows of date table data.")

    # Calculate execution time
    execution_time = time.time() - start_time
    logger.info(
        f"Execution time for generating date table data: {execution_time:.4f} seconds"
    )

    return table_data
