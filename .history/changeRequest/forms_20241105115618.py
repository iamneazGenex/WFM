from django import forms
from roster.models import Roster
from django.db.models import Q
from django.forms import ModelChoiceField
from accounts.models import Employee
from django.utils import timezone
from datetime import datetime
from django.core.exceptions import ValidationError


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
    )  # Set an empty initial queryset
    requestee = forms.ModelChoiceField(
        queryset=Employee.objects.none(), label="Requestee"
    )
    time_display = forms.CharField(
        label="Time Details",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    def __init__(self, employee, swapDateID, requesteeID, *args, **kwargs):
        super(ShiftTimeTradingForm, self).__init__(*args, **kwargs)
        # currentDate = timezone.localtime().date()
        currentDate = datetime(2024, 1, 1, tzinfo=timezone.utc)
        # Build the querysets for swapDate and tradeDate
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
        # Set the initial values for swapDate and tradeDate fields
        self.fields["swapDate"].queryset = swap_date_queryset
        self.fields["requestee"].queryset = requestee_queryset

        if swapDateID is not None:
            self.fields["swapDate"].initial = swapDateID
        if requesteeID is not None:
            self.fields["requestee"].initial = requesteeID
        if requesteeID is not None and swapDateID is not None:
            self.set_time_details(requesteeID, swapDateID)

    def set_time_details(self, requesteeID, swapDateID):
        # Fetch the roster entry for the selected requestee and swap date
        try:
            roster_entry = Roster.objects.get(
                employee__id=requesteeID, start_date=swapDateID
            )
            self.fields["time_display"].initial = (
                f"Start: {roster_entry.start_time}, End: {roster_entry.end_time}"
            )
        except Roster.DoesNotExist:
            self.fields["time_display"].initial = "No roster entry found."

    def clean(self):
        """
        Validate the swap to ensure it adheres to business rules.
        """
        cleaned_data = super().clean()
        employee = self.employee
        swap_date_id = cleaned_data.get("swapDate")
        requestee_id = cleaned_data.get("requestee")

        # Load current roster entries for both employees on the specified swap date
        if swap_date_id and requestee_id:
            employee_roster = Roster.objects.filter(
                employee=employee, start_date=swap_date_id
            ).first()
            requestee_roster = Roster.objects.filter(
                employee__id=requestee_id, start_date=swap_date_id
            ).first()

            if not employee_roster or not requestee_roster:
                raise ValidationError(
                    "Both employee and requestee must have roster entries on the swap date."
                )

            # Temporarily swap rosters in memory to validate business rules
            self.validate_swap(employee_roster, requestee_roster)

    def validate_swap(self, employee_roster, requestee_roster):
        """
        Temporarily swap the rosters and validate them against business rules.
        """
        # Swap the `employee_roster` and `requestee_roster` in memory
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

        # Check each swapped roster against business rules
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
