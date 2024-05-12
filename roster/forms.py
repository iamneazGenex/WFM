from django import forms
from .models import Forecast, Roster, ShiftLegend, WorkRule, RosterSeatCount
from accounts.models import CustomUser, Employee
from django.db.models import Q
from rms.global_utilities import *
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError

# class CreateRosterForm(forms.Form):
#     dateWidget = widget = forms.widgets.DateInput(
#         attrs={
#             "type": "date",
#             "placeholder": "yyyy-mm-dd (DOB)",
#             "class": "form-control",
#         }
#     )
#     timeWidget = forms.widgets.TimeInput(
#         format="%H:%M", attrs={"type": "time", "class": "form-control"}
#     )

#     employee = forms.ModelChoiceField(
#         label="Employee",
#         queryset=CustomUser.objects.filter(groups__name__in=["Employee"]),
#         required=True,
#     )
#     start_date = forms.DateField(label="Start Date", required=True, widget=dateWidget)
#     start_time = forms.TimeField(label="Start Time", required=False, widget=timeWidget)
#     end_date = forms.DateField(label="End Date", required=True, widget=dateWidget)
#     end_time = forms.TimeField(label="End Time", required=False, widget=timeWidget)


class RosterForm(forms.ModelForm):
    class Meta:
        model = Roster
        fields = ["employee", "start_date", "start_time", "end_date", "end_time"]

    def __init__(self, *args, **kwargs):
        super(RosterForm, self).__init__(*args, **kwargs)
        # Customize form fields if needed
        # customselect2
        dateWidget = getDateWidget()
        timeWidget = getTimeWidget()
        self.fields["employee"].widget.attrs.update({"class": "form-control"})
        self.fields["start_date"].widget.attrs.update(
            {"class": "form-control datepicker"}
        )
        self.fields["start_time"].widget.attrs.update(
            {"class": "form-control timepicker"}
        )
        self.fields["end_date"].widget.attrs.update(
            {"class": "form-control datepicker"}
        )
        self.fields["end_time"].widget.attrs.update(
            {"class": "form-control timepicker"}
        )
        self.fields["start_date"].widget = dateWidget
        self.fields["start_time"].widget = timeWidget
        self.fields["end_date"].widget = dateWidget
        self.fields["end_time"].widget = timeWidget
        self.fields["employee"].label_from_instance = self.employee_label_from_instance
        self.fields["employee"].widget.attrs.update({"class": "select2"})

    def employee_label_from_instance(self, obj):
        return f"{obj.user.name} | {obj.user.email} | {obj.user.employee_id}"


class EditRosterForm(forms.ModelForm):
    class Meta:
        model = Roster
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(EditRosterForm, self).__init__(*args, **kwargs)
        roster = kwargs.get("instance")
        self.fields["employee"].queryset = Employee.objects.filter(
            Q(id=roster.employee.id)
        )

        dateWidget = getDateWidget()
        timeWidget = getTimeWidget()

        self.fields["employee"].empty_label = None
        self.fields["employee"].initial = roster.employee.user.id
        self.fields["start_date"].widget = dateWidget
        self.fields["start_time"].widget = timeWidget
        self.fields["end_date"].widget = dateWidget
        self.fields["end_time"].widget = timeWidget
        # if roster is not None:

        #     self.fields["start_date"].initial = roster.start_date
        #     self.fields["start_time"].initial = roster.start_time
        #     self.fields["end_date"].initial = roster.end_date
        #     self.fields["end_time"].initial = roster.end_time

    # dateWidget = widget = forms.widgets.DateInput(
    #     attrs={
    #         "type": "date",
    #         "placeholder": "yyyy-mm-dd (DOB)",
    #         "class": "form-control",
    #     }
    # )
    # timeWidget = forms.widgets.TimeInput(
    #     format="%H:%M", attrs={"type": "time", "class": "form-control"}
    # )

    # employee = forms.ModelChoiceField(
    #     label="Employee",
    #     queryset=CustomUser.objects.filter(groups__name__in=["Employee"]),
    #     required=True,
    # )
    # start_date = forms.DateField(label="Start Date", required=True, widget=dateWidget)
    # start_time = forms.TimeField(label="Start Time", required=False, widget=timeWidget)
    # end_date = forms.DateField(label="End Date", required=True, widget=dateWidget)
    # end_time = forms.TimeField(label="End Time", required=False, widget=timeWidget)

    # def __init__(self, roster, *args, **kwargs):
    #     super(CreateRosterForm, self).__init__(*args, **kwargs)
    #     print(self)
    #     if roster is not None:
    #         self.fields["employee"].queryset = CustomUser.objects.filter(
    #             Q(id=roster.employee.user.id)
    #         )
    #         self.fields["employee"].empty_label = None
    #         self.fields["employee"].initial = roster.employee.user.id
    #         self.fields["start_date"].initial = roster.start_date
    #         self.fields["start_time"].initial = roster.start_time
    #         self.fields["end_date"].initial = roster.end_date
    #         self.fields["end_time"].initial = roster.end_time


class WorkRuleForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = WorkRule
        fields = "__all__"
        exclude = ["created_by", "updated_by"]

    def __init__(self, *args, **kwargs):
        super(WorkRuleForm, self).__init__(*args, **kwargs)

        timeWidget = getTimeWidget()
        self.fields["female_shift_start_time"].widget = timeWidget
        self.fields["female_shift_end_time"].widget = timeWidget
        self.fields["prohibited_time_for_end_of_a_shift_start_time"].widget = timeWidget
        self.fields["prohibited_time_for_end_of_a_shift_end_time"].widget = timeWidget


class RosterSeatCountForm(forms.ModelForm):
    class Meta:
        model = RosterSeatCount
        fields = ["site", "process", "lob", "total"]

    def site_label_from_instance(self, obj):
        return obj.name.upper()

    def process_label_from_instance(self, obj):
        return obj.name.title()

    def lob_label_from_instance(self, obj):
        return obj.name.title()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["site"].label_from_instance = self.site_label_from_instance
        self.fields["process"].label_from_instance = self.process_label_from_instance
        self.fields["lob"].label_from_instance = self.lob_label_from_instance
        self.fields["site"].widget.attrs.update({"class": "select2"})
        self.fields["process"].widget.attrs.update({"class": "select2"})
        self.fields["lob"].widget.attrs.update({"class": "select2"})


class ForecastingForm(forms.ModelForm):
    class Meta:
        model = Forecast
        fields = ["date", "process", "lob", "interval", "forecast", "required_hc"]
        labels = {
            "required_hc": "Required Head Count",
        }

    def process_label_from_instance(self, obj):
        return obj.name.title()

    def lob_label_from_instance(self, obj):
        return obj.name.title()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        dateWidget = getDateWidget()

        self.fields["process"].label_from_instance = self.process_label_from_instance
        self.fields["lob"].label_from_instance = self.lob_label_from_instance
        self.fields["process"].widget.attrs.update({"class": "select2"})
        self.fields["lob"].widget.attrs.update({"class": "select2"})
        self.fields["date"].widget.attrs.update({"class": "form-control datepicker"})
        self.fields["date"].widget = dateWidget


class ShiftLegendForm(forms.ModelForm):
    class Meta:
        model = ShiftLegend
        fields = ["shift_start_time", "shift_end_time", "shift_count", "shift_name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        timeWidget = getTimeWidget()
        self.fields["shift_start_time"].widget.attrs.update(
            {"class": "form-control timepicker"}
        )
        self.fields["shift_end_time"].widget.attrs.update(
            {"class": "form-control timepicker"}
        )

        self.fields["shift_start_time"].widget = timeWidget
        self.fields["shift_end_time"].widget = timeWidget

    def clean(self):
        cleaned_data = super().clean()
        shift_count = cleaned_data.get("shift_count")
        if shift_count == 1:
            # Retrieve values from the cleaned_data dictionary
            shift_start_time = cleaned_data.get("shift_start_time")
            shift_end_time = cleaned_data.get("shift_end_time")

            # Check if both times are present
            if shift_start_time and shift_end_time:
                # Convert times to timedelta objects
                start_timedelta = timedelta(
                    hours=shift_start_time.hour, minutes=shift_start_time.minute
                )
                end_timedelta = timedelta(
                    hours=shift_end_time.hour, minutes=shift_end_time.minute
                )

                # Check if shift start time is before shift end time
                # if start_timedelta >= end_timedelta:
                #     raise ValidationError(
                #         "Shift start time must be before shift end time."
                #     )
        elif shift_count == 0:
            if cleaned_data.get("shift_name") is None:
                raise ValidationError("Enter The Shift Name")
            cleaned_data["shift_start_time"] = None
            cleaned_data["shift_end_time"] = None
        return cleaned_data

    # def save(self, commit=True):
    #     instance = super().save(commit=False)
    #     # Additional processing or validations before saving
    #     if commit:
    #         instance.save()
    #     return instance
