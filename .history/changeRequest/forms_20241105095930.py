from django import forms
from roster.models import Roster
from django.db.models import Q
from django.forms import ModelChoiceField
from accounts.models import Employee
from django.utils import timezone
from datetime import datetime


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
