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
        swap_date_id = cleaned_data.get("swapDate")
        requestee_id = cleaned_data.get("requestee")
        requestee = Employee.objects.get(id=requestee_id)
        if swap_date_id and requestee_id:
            employee_roster = Roster.objects.get(id=swap_date_id)
            requestee_roster = Roster.objects.filter(
                employee__id=requestee_id, start_date=swap_date_id
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
        self.check_shift_gap(temp_employee_roster.employee)
        self.check_shift_gap(temp_requestee_roster.employee)
        self.check_female_shift_times(
            temp_employee_roster.employee, temp_employee_roster
        )
        self.check_female_shift_times(
            temp_requestee_roster.employee, temp_requestee_roster
        )
        self.check_prohibited_shift_end(temp_employee_roster)
        self.check_prohibited_shift_end(temp_requestee_roster)
        self.check_consecutive_working_days(temp_employee_roster.employee)
        self.check_consecutive_working_days(temp_requestee_roster.employee)

    def check_shift_duration(self, roster):
        shift_duration = (roster.end_time - roster.start_time).total_seconds() / 3600
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

    def check_shift_gap(self, employee):
        previous_roster = (
            Roster.objects.filter(
                employee=employee, start_date__lt=timezone.localdate()
            )
            .order_by("-start_date")
            .first()
        )
        if previous_roster:
            gap = (roster.start_time - previous_roster.end_time).total_seconds() / 3600
            logger.debug(f"Checking shift gap for {employee}: {gap} hours")
            if gap < self.work_rule.gap_between_shift_end_to_the_next_shift_start_time:
                logger.error("Insufficient gap between shifts.")
                raise ValidationError("A minimum gap is required between shifts.")

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

    def check_consecutive_working_days(self, employee):
        recent_rosters = Roster.objects.filter(
            employee=employee, start_date__lte=timezone.localdate()
        ).order_by("-start_date")[: self.work_rule.consecutive_working_days]
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
