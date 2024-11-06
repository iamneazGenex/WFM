from django import forms
from roster.models import Roster
from django.db.models import Q
from django.forms import ModelChoiceField
from accounts.models import Employee
from django.utils import timezone
from datetime import datetime
from django.core.exceptions import ValidationError
from datetime import timedelta, time
import logging

# Configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set level to debug to capture detailed logs


class MyModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return "{date}".format(date=obj.start_date)


class DayOffTradingForm(forms.Form):
    swapDate = forms.ModelChoiceField(
        queryset=Roster.objects.none(), label="Date To Swap"
    )  # Set an empty initial queryset
    tradeDate = MyModelChoiceField(
        queryset=Roster.objects.none(), label="Select the week of want to trade off"
    )  # Set an empty initial queryset
    requestee = forms.ModelChoiceField(
        queryset=Employee.objects.none(), label="Requestee"
    )

    def __init__(self, employee, swapDateID, tradeDateID, requesteeID, *args, **kwargs):
        super(DayOffTradingForm, self).__init__(*args, **kwargs)
        self.fields["swapDate"].widget.attrs.update({"class": "select2"})
        self.fields["tradeDate"].widget.attrs.update({"class": "select2"})
        self.fields["requestee"].widget.attrs.update({"class": "select2"})

        currentDate = timezone.localtime().date()
        # currentDate = datetime(2024, 1, 1, tzinfo=timezone.utc)

        # Build the querysets for swapDate and tradeDate
        swap_date_queryset = Roster.objects.filter(
            Q(employee=employee) & ~Q(start_time=None) & Q(start_date__gt=currentDate)
        )
        trade_date_queryset = Roster.objects.filter(
            Q(employee=employee) & Q(start_time=None) & Q(start_date__gt=currentDate)
        )
        requestee_queryset = Employee.objects.filter(
            Q(process=employee.process)
            & Q(site=employee.site)
            & Q(work_role=employee.work_role)
            & Q(lob=employee.lob)
            & ~Q(user=employee.user)
        )
        # Set the initial values for swapDate and tradeDate fields
        self.fields["swapDate"].queryset = swap_date_queryset
        self.fields["tradeDate"].queryset = trade_date_queryset
        self.fields["requestee"].queryset = requestee_queryset

        if swapDateID is not None:
            self.fields["swapDate"].initial = swapDateID
        if tradeDateID is not None:
            self.fields["tradeDate"].initial = tradeDateID
        if requesteeID is not None:
            self.fields["requestee"].initial = requesteeID


class SelectRequestee(forms.Form):
    def __init__(self, querySet, requesteeID, swapDateID, tradeDateID, *args, **kwargs):
        super(SelectRequestee, self).__init__(*args, **kwargs)
        if querySet is not None:
            self.fields["requestee"].queryset = querySet
        if swapDateID is not None and tradeDateID is not None:
            self.fields["swapDateID"].initial = swapDateID
            self.fields["tradeDateID"].initial = tradeDateID
        if requesteeID is not None:
            self.fields["requestee"].initial = requesteeID

    requestee = forms.ModelChoiceField(
        queryset=Employee.objects.all(), label="Requestee"
    )
    swapDateID = forms.IntegerField(label="Date To Swap")
    tradeDateID = forms.IntegerField(label="Select the week of want to trade off")


class ShiftTimeTradingForm(forms.Form):
    swapDate = forms.ModelChoiceField(
        queryset=Roster.objects.none(), label="Date To Swap"
    )
    requestee = forms.ModelChoiceField(
        queryset=Employee.objects.none(), label="Requestee"
    )
    time_display = forms.CharField(
        label="Time Details",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    def __init__(
        self, employee, work_rule, swapDateID=None, requesteeID=None, *args, **kwargs
    ):
        super(ShiftTimeTradingForm, self).__init__(*args, **kwargs)
        self.employee = employee
        self.work_rule = work_rule
        currentDate = datetime(2024, 1, 1, tzinfo=timezone.utc)
        logger.debug(
            f"Initializing ShiftTimeTradingForm for employee: {employee} on {currentDate}"
        )

        # Build the querysets for swapDate and requestee
        swap_date_queryset = Roster.objects.filter(
            Q(employee=employee) & ~Q(start_time=None) & Q(start_date__gte=currentDate)
        )
        requestee_queryset = Employee.objects.filter(
            Q(process=employee.process)
            & Q(site=employee.site)
            & Q(work_role=employee.work_role)
            & Q(lob=employee.lob)
            & ~Q(user=employee.user)
        )
        self.fields["swapDate"].queryset = swap_date_queryset
        self.fields["requestee"].queryset = requestee_queryset

        # if swapDateID is not None:
        #     self.fields["swapDate"].initial = swapDateID
        # if requesteeID is not None:
        #     self.fields["requestee"].initial = requesteeID
        # if requesteeID is not None and swapDateID is not None:
        #     self.set_time_details(requesteeID, swapDateID)

    def set_time_details(self, requesteeID, swapDateID):
        try:
            roster_entry = Roster.objects.get(
                employee__id=requesteeID, start_date=swapDateID
            )
            self.fields["time_display"].initial = (
                f"Start: {roster_entry.start_time}, End: {roster_entry.end_time}"
            )
            logger.debug(
                f"Set time details for requestee {requesteeID} on {swapDateID}: {self.fields['time_display'].initial}"
            )
        except Roster.DoesNotExist:
            self.fields["time_display"].initial = "No roster entry found."
            logger.warning(
                f"No roster entry found for requestee {requesteeID} on {swapDateID}"
            )

    def clean(self):
        cleaned_data = super().clean()
        employee_roster = cleaned_data.get("swapDate")
        requestee = cleaned_data.get("requestee")
        if employee_roster and requestee:
            requestee_roster = Roster.objects.filter(
                employee=requestee, start_date=employee_roster.start_date
            ).first()

            if not employee_roster or not requestee_roster:
                logger.error(
                    "Both employee and requestee must have roster entries on the swap date."
                )
                raise ValidationError(
                    "Both employee and requestee must have roster entries on the swap date."
                )

            logger.debug("Initiating temporary roster swap for validation.")
            self.validate_swap(employee_roster, requestee_roster)

    def validate_swap(self, employee_roster, requestee_roster):
        temp_employee_roster = Roster(
            employee=requestee_roster.employee,
            start_date=employee_roster.start_date,
            start_time=employee_roster.start_time,
            end_date=employee_roster.end_date,
            end_time=employee_roster.end_time,
        )
        temp_requestee_roster = Roster(
            employee=employee_roster.employee,
            start_date=requestee_roster.start_date,
            start_time=requestee_roster.start_time,
            end_date=requestee_roster.end_date,
            end_time=requestee_roster.end_time,
        )

        logger.debug("Validating swapped rosters for business rule compliance.")
        self.check_shift_duration(temp_employee_roster)
        self.check_shift_duration(temp_requestee_roster)
        self.check_shift_gap(temp_employee_roster)
        self.check_shift_gap(temp_requestee_roster)
        if temp_employee_roster.employee.gender == "F":
            self.check_female_shift_times(
                temp_employee_roster.employee, temp_employee_roster
            )
        if temp_employee_roster.employee.gender == "F":
            self.check_female_shift_times(
                temp_requestee_roster.employee, temp_requestee_roster
            )
        self.check_prohibited_shift_end(temp_employee_roster)
        self.check_prohibited_shift_end(temp_requestee_roster)
        self.check_consecutive_working_days(temp_employee_roster)
        self.check_consecutive_working_days(temp_requestee_roster)

    def check_shift_duration(self, roster):
        # Convert start_time and end_time to datetime.datetime
        start_datetime = datetime.combine(roster.start_date, roster.start_time)
        end_datetime = datetime.combine(roster.end_date, roster.end_time)
        shift_duration = (end_datetime - start_datetime).total_seconds() / 3600
        logger.debug(
            f"Checking shift duration: {shift_duration} hours for {roster.employee}"
        )
        if not (
            self.work_rule.minimum_regular_shift_duration
            <= shift_duration
            <= self.work_rule.maximum_regular_shift_duration
        ):
            logger.error("Shift duration does not meet the allowed range.")
            raise ValidationError("Shift duration must be within the allowed range.")

    def check_shift_gap(self, roster):
        previous_roster = (
            Roster.objects.filter(
                employee=roster.employee, start_date__lt=roster.start_date
            )
            .order_by("-start_date")
            .first()
        )
        if previous_roster:
            if previous_roster.start_time != None:
                current_roster_start_datetime = datetime.combine(
                    roster.start_date, roster.start_time
                )
                previous_roster_end_datetime = datetime.combine(
                    previous_roster.end_date, previous_roster.end_time
                )
                logger.debug(
                    f"Current Roster {current_roster_start_datetime}| Previous Roster{previous_roster_end_datetime} "
                )
                gap = (
                    current_roster_start_datetime - previous_roster_end_datetime
                ).total_seconds() / 3600
                logger.debug(f"Checking shift gap for {roster.employee}: {gap} hours")
                if (
                    gap
                    < self.work_rule.gap_between_shift_end_to_the_next_shift_start_time
                ):
                    logger.error("Insufficient gap between shifts.")
                    raise ValidationError(
                        f"A minimum gap {self.work_rule.gap_between_shift_end_to_the_next_shift_start_time} is required between shifts | Agent:{roster.employee.user.name} | Gap:{gap}"
                    )
            else:
                logger.debug(f"Previous roster time is none")

    def check_female_shift_times(self, employee, roster):
        if employee.gender == "F":
            logger.debug(f"Checking female shift time for {employee}")
            if not (
                self.work_rule.female_shift_start_time
                <= roster.start_time
                <= self.work_rule.female_shift_end_time
            ):
                logger.error(
                    "Shift start time for female employee outside allowed range."
                )
                raise ValidationError(
                    "Female employees can only work shifts within allowed times."
                )

    def check_prohibited_shift_end(self, roster):
        if (
            self.work_rule.prohibited_time_for_end_of_a_shift_start_time
            <= roster.end_time
            <= self.work_rule.prohibited_time_for_end_of_a_shift_end_time
        ):
            logger.error("Shift end time falls within prohibited range.")
            raise ValidationError("Shifts cannot end during prohibited hours.")

    def check_consecutive_working_days(self, roster):
        # Define date range to fetch rosters around the swap and trade dates
        days_before = roster.start_date - timedelta(
            days=self.work_rule.consecutive_working_days_limit
        )
        days_after = roster.end_date + timedelta(
            days=self.work_rule.consecutive_working_days_limit
        )

        # Fetch all rosters within this date range
        rosters = Roster.objects.filter(
            employee=roster.employee,
            start_date__range=(days_before, days_after),
        ).order_by("start_date")

        # Collect roster details with dates and times
        roster_dates = []
        for r in rosters:
            roster_dates.append(
                {
                    "start_date": r.start_date,
                    "end_date": r.end_date,
                    "start_time": r.start_time,
                    "end_time": r.end_time,
                }
            )

        # Sort rosters by start date to ensure correct ordering
        roster_dates.sort(key=lambda x: x["start_date"])

        # Track consecutive working days and identify gaps
        consecutive_count = 0
        previous_end_date = None

        for roster_entry in roster_dates:
            if (
                previous_end_date
                and (roster_entry["start_date"] - previous_end_date).days > 1
            ):
                # Gap found, reset consecutive count
                consecutive_count = 0

            if (
                roster_entry["start_time"] is not None
                and roster_entry["end_time"] is not None
            ):
                # Increment count for a valid shift
                consecutive_count += 1
                previous_end_date = roster_entry["end_date"]
            else:
                # Reset if there’s a roster without valid start and end times
                consecutive_count = 0
                break

            # Check if consecutive days exceed the limit
            if consecutive_count > self.work_rule.consecutive_working_days_limit:
                error_message = f"Consecutive working days ({consecutive_count}) exceed the limit ({self.work_rule.consecutive_working_days_limit}) for {roster.employee.user.name}"
                logger.info(error_message)
                raise ValidationError("\n".join(error_message))

        # If within limit, no validation error is raised
        if consecutive_count <= consecutive_working_days_limit:
            logger.info(
                f"Consecutive working days ({consecutive_count}) are within the allowed limit."
            )

        recent_rosters = Roster.objects.filter(
            employee=roster.employee, start_date__lte=roster.start_date
        ).order_by("-start_date")[: self.work_rule.consecutive_working_days]
        print(recent_rosters)
        print(recent)
        if len(recent_rosters) == self.work_rule.consecutive_working_days:
            if all(
                (recent_rosters[i].start_date - recent_rosters[i + 1].start_date).days
                == 1
                for i in range(len(recent_rosters) - 1)
            ):
                logger.error("Exceeded maximum consecutive working days.")
                raise ValidationError(
                    "Employees cannot work more than the allowed consecutive days."
                )
