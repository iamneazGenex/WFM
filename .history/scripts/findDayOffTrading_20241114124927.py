import logging
from datetime import datetime, timedelta
from accounts.models import Employee
from roster.models import Roster, WorkRule
from changeRequest.models import DayOffTrading
from django.db import transaction
from changeRequest.utils import *

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def run():
    # Set the month for which you want to test trades
    month_start_date = datetime(year=2024, month=11, day=1)
    month_end_date = month_start_date + timedelta(days=10)
    logging.info(
        f"Testing trades for roster period: {month_start_date} to {month_end_date}"
    )

    # Get all employees and rosters within the specified month
    employees = Employee.objects.all()
    rosters = Roster.objects.filter(
        start_date__range=(month_start_date, month_end_date)
    )
    work_rule = WorkRule.objects.first()  # Assuming a single work rule
    logging.info(f"Loaded {employees.count()} employees and {rosters.count()} rosters")

    successful_trades = []
    failed_trades = []

    # Iterate over all employee pairs
    for requestor in employees:
        for requestee in employees:
            if requestor == requestee:
                continue  # Skip trading with self

            logging.info(
                f"Checking trades between Requestor: {requestor.id} and Requestee: {requestee.id}"
            )

            # Iterate over all roster dates for the month
            for requestor_roster in rosters.filter(employee=requestor):
                for requestee_roster in rosters.filter(employee=requestee):
                    swap_date_id = requestor_roster.id
                    trade_date_id = requestee_roster.id
                    logging.info(
                        f"Checking trade between dates {swap_date_id} <-> {trade_date_id}"
                    )

                    # Check business rules
                    with transaction.atomic():  # Ensure a rollback in case of any rule failure
                        try:
                            # Consecutive working days rule
                            (
                                requestor_consecutive_result,
                                requestor_consecutive_error,
                            ) = checkConsecutiveWorkingDays(
                                swapRosterID=swap_date_id,
                                tradeRosterID=trade_date_id,
                                employee=requestor,
                                workRule=work_rule,
                            )
                            (
                                requestee_consecutive_result,
                                requestee_consecutive_error,
                            ) = checkConsecutiveWorkingDays(
                                swapRosterID=trade_date_id,
                                tradeRosterID=swap_date_id,
                                employee=requestee,
                                workRule=work_rule,
                            )

                            if not (
                                requestor_consecutive_result
                                and requestee_consecutive_result
                            ):
                                raise ValueError(
                                    f"Consecutive working days error: {requestor_consecutive_error or requestee_consecutive_error}"
                                )
                            logging.info("Consecutive working days check passed")

                            # Shift end gap rule
                            gap_result, gap_error = (
                                checkGapBetweenShiftEndToTheNextShiftStartTime(
                                    requestor=requestor,
                                    requestee=requestee,
                                    swapDateID=swap_date_id,
                                    tradeDateID=trade_date_id,
                                    workRule=work_rule,
                                )
                            )
                            if not gap_result:
                                raise ValueError(f"Gap check error: {gap_error}")
                            logging.info("Gap check passed")

                            # Female shift time rule
                            if requestor.gender == "F":
                                (
                                    requestor_female_shift_result,
                                    requestor_female_shift_error,
                                ) = checkFemaleShiftTimeFollowsWorkRule(
                                    startTime=requestor_roster.start_time,
                                    endTime=requestor_roster.end_time,
                                    workRule=work_rule,
                                )
                                if not requestor_female_shift_result:
                                    raise ValueError(
                                        f"Requestor female shift time error: {requestor_female_shift_error}"
                                    )
                            if requestee.gender == "F":
                                (
                                    requestee_female_shift_result,
                                    requestee_female_shift_error,
                                ) = checkFemaleShiftTimeFollowsWorkRule(
                                    startTime=requestee_roster.start_time,
                                    endTime=requestee_roster.end_time,
                                    workRule=work_rule,
                                )
                                if not requestee_female_shift_result:
                                    raise ValueError(
                                        f"Requestee female shift time error: {requestee_female_shift_error}"
                                    )
                            logging.info("Female shift time check passed")

                            # Regular shift duration rule
                            (
                                requestor_shift_duration_result,
                                requestor_shift_duration_error,
                            ) = checkRegularShiftDuration(
                                roster=requestor_roster, workRule=work_rule
                            )
                            (
                                requestee_shift_duration_result,
                                requestee_shift_duration_error,
                            ) = checkRegularShiftDuration(
                                roster=requestee_roster, workRule=work_rule
                            )
                            if not requestor_shift_duration_result:
                                raise ValueError(
                                    f"Requestor shift duration error: {requestor_shift_duration_error}"
                                )
                            if not requestee_shift_duration_result:
                                raise ValueError(
                                    f"Requestee shift duration error: {requestee_shift_duration_error}"
                                )
                            logging.info("Regular shift duration check passed")

                            # Prohibited time check
                            (
                                requestor_prohibited_time_result,
                                requestor_prohibited_time_error,
                            ) = checkShiftEndInProhibitedTime(
                                roster=requestor_roster, workRule=work_rule
                            )
                            (
                                requestee_prohibited_time_result,
                                requestee_prohibited_time_error,
                            ) = checkShiftEndInProhibitedTime(
                                roster=requestee_roster, workRule=work_rule
                            )
                            if not requestor_prohibited_time_result:
                                raise ValueError(
                                    f"Requestor prohibited time error: {requestor_prohibited_time_error}"
                                )
                            if not requestee_prohibited_time_result:
                                raise ValueError(
                                    f"Requestee prohibited time error: {requestee_prohibited_time_error}"
                                )
                            logging.info("Prohibited time check passed")

                            # If all checks pass, record the successful trade
                            successful_trades.append(
                                (
                                    requestor.id,
                                    requestee.id,
                                    swap_date_id,
                                    trade_date_id,
                                )
                            )
                            logging.info(
                                f"Trade possible between Requestor: {requestor.id} and Requestee: {requestee.id} for dates {swap_date_id} <-> {trade_date_id}"
                            )

                        except Exception as e:
                            # Record the failed trade
                            failed_trades.append(
                                (
                                    requestor.id,
                                    requestee.id,
                                    swap_date_id,
                                    trade_date_id,
                                    str(e),
                                )
                            )
                            logging.error(
                                f"Trade failed between Requestor: {requestor.id} and Requestee: {requestee.id} for dates {swap_date_id} <-> {trade_date_id}. Error: {e}"
                            )
                            continue  # Move to the next possible trade

    # Output summary of trades
    logging.info(f"Total successful trades: {len(successful_trades)}")
    logging.info(f"Total failed trades: {len(failed_trades)}")
