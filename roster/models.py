from django.db import models
from accounts.models import Employee
from accounts.models import Process, LOB, Site, WorkRole
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta


# Create your models here.
class BaseModel(models.Model):
    created_At = models.DateTimeField(auto_now_add=True)
    updated_At = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ShiftLegend(BaseModel):
    shift_name = models.CharField(max_length=20, null=True, blank=True)
    shift_count = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    shift_start_time = models.TimeField(null=True, blank=True)
    shift_end_time = models.TimeField(null=True, blank=True)
    login_start_hour = models.PositiveIntegerField(
        editable=False, null=True, blank=True
    )
    duty_hour = models.DurationField(editable=False, null=True, blank=True)
    target_break = models.TimeField(editable=True, null=True, blank=True)
    target_ready = models.TimeField(editable=True, null=True, blank=True)
    hour_0 = models.BooleanField(null=True, editable=True)
    hour_1 = models.BooleanField(null=True, editable=True)
    hour_2 = models.BooleanField(null=True, editable=True)
    hour_3 = models.BooleanField(null=True, editable=True)
    hour_4 = models.BooleanField(null=True, editable=True)
    hour_5 = models.BooleanField(null=True, editable=True)
    hour_6 = models.BooleanField(null=True, editable=True)
    hour_7 = models.BooleanField(null=True, editable=True)
    hour_8 = models.BooleanField(null=True, editable=True)
    hour_9 = models.BooleanField(null=True, editable=True)
    hour_10 = models.BooleanField(null=True, editable=True)
    hour_11 = models.BooleanField(null=True, editable=True)
    hour_12 = models.BooleanField(null=True, editable=True)
    hour_13 = models.BooleanField(null=True, editable=True)
    hour_14 = models.BooleanField(null=True, editable=True)
    hour_15 = models.BooleanField(null=True, editable=True)
    hour_16 = models.BooleanField(null=True, editable=True)
    hour_17 = models.BooleanField(null=True, editable=True)
    hour_18 = models.BooleanField(null=True, editable=True)
    hour_19 = models.BooleanField(null=True, editable=True)
    hour_20 = models.BooleanField(null=True, editable=True)
    hour_21 = models.BooleanField(null=True, editable=True)
    hour_22 = models.BooleanField(null=True, editable=True)
    hour_23 = models.BooleanField(null=True, editable=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shiftLegend_created_by",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shiftLegend_updated_by",
    )

    def clean(self):
        if self.shift_count == 1:
            # Check if both times are present
            if self.shift_start_time and self.shift_end_time:
                # Calculate shift_name
                self.shift_name = f"{self.shift_start_time.strftime('%H%M')}-{self.shift_end_time.strftime('%H%M')}"
                self.calculate_login_start_hour()
                self.calculate_duty_hour()
                self.calculate_target_break()
                self.calculate_target_ready()
                self.fill_hour_columns()
        else:
            self.shift_start_time = None
            self.shift_end_time = None

    def calculate_login_start_hour(self):
        # Calculate login_start_hour
        start_time = datetime.combine(datetime.today(), self.shift_start_time)
        # Convert start_time to minutes
        start_minutes = start_time.hour * 60 + start_time.minute

        # Subtract one hour (60 minutes)
        result_minutes = start_minutes - 60

        # Ensure the result is non-negative
        result_minutes = max(result_minutes, 0)

        # Convert result_minutes back to hours
        result_hours = result_minutes // 60
        self.login_start_hour = result_hours

    def calculate_duty_hour(self):
        # Convert times to timedelta objects
        start_timedelta = timedelta(
            hours=self.shift_start_time.hour, minutes=self.shift_start_time.minute
        )
        end_timedelta = timedelta(
            hours=self.shift_end_time.hour, minutes=self.shift_end_time.minute
        )

        # Calculate duty hour as timedelta
        # print(f"end time delta:{end_timedelta}")
        # print(f"start time delta:{start_timedelta}")
        # print(f"difference:{end_timedelta - start_timedelta}")
        if start_timedelta < end_timedelta:
            self.duty_hour = timedelta(
                hours=self.shift_end_time.hour - self.shift_start_time.hour,
                minutes=self.shift_end_time.minute - self.shift_start_time.minute,
            )
        else:
            self.duty_hour = timedelta(
                hours=24 - self.shift_start_time.hour + self.shift_end_time.hour,
                minutes=self.shift_end_time.minute - self.shift_start_time.minute,
            )

    def calculate_target_break(self):
        target_break_percentage = 0.11  # 11%
        target_break_seconds = self.duty_hour.total_seconds() * target_break_percentage
        target_break_timedelta = abs(timedelta(seconds=target_break_seconds))
        self.target_break = (datetime.min + target_break_timedelta).time()

    def calculate_target_ready(self):
        target_ready_percentage = 0.89  # 89%
        target_ready_seconds = self.duty_hour.total_seconds() * target_ready_percentage
        target_ready_timedelta = abs(timedelta(seconds=target_ready_seconds))
        self.target_ready = (datetime.min + target_ready_timedelta).time()

    def fill_hour_columns(self):
        # Clear existing hour columns
        for i in range(24):
            setattr(self, f"hour_{i}", False)

        # Set hour columns based on shift_start_time and shift_end_time
        start_hour = self.shift_start_time.hour
        end_hour = self.shift_end_time.hour
        end_minute = self.shift_end_time.minute
        print(f"start_hour:{start_hour}")
        print(f"end_hour:{end_hour}")
        print(f"end_minute:{end_minute}")
        if end_minute > 0:
            if end_hour > start_hour:
                for i in range(start_hour, end_hour + 1):
                    setattr(self, f"hour_{i}", True)
            else:
                # Handle shift end time on the next day
                for i in range(start_hour, 24):
                    setattr(self, f"hour_{i}", True)
                for i in range(0, end_hour + 1):
                    setattr(self, f"hour_{i}", True)
        else:
            if end_hour > start_hour:
                for i in range(start_hour, end_hour):
                    setattr(self, f"hour_{i}", True)
            else:
                # Handle shift end time on the next day
                for i in range(start_hour, 24):
                    setattr(self, f"hour_{i}", True)
                for i in range(0, end_hour):
                    setattr(self, f"hour_{i}", True)

    def save(self, *args, **kwargs):
        self.clean()  # Ensure clean is called before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return self.shift_name


class Roster(BaseModel):
    GENDER_CHOICES = (("M", "Male"), ("F", "Female"))
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="rosterEmployee",
    )
    shiftLegend = models.ForeignKey(
        ShiftLegend,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="rosterShiftLegend",
        editable=False,  # Make it non-editable
    )
    process = models.ForeignKey(
        Process, on_delete=models.SET_NULL, null=True, related_name="rosterProcess"
    )
    gender = models.CharField(
        default="N/A", max_length=50, null=True, choices=GENDER_CHOICES
    )
    site = models.ForeignKey(
        Site, on_delete=models.SET_NULL, null=True, related_name="rosterSite"
    )
    work_role = models.ForeignKey(
        WorkRole, on_delete=models.SET_NULL, null=True, related_name="rosterWorkRole"
    )
    lob = models.ForeignKey(
        LOB, on_delete=models.SET_NULL, null=True, related_name="rosterLOB"
    )
    pick_drop_location = models.CharField(max_length=255, null=True)
    start_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_date = models.DateField()
    end_time = models.TimeField(null=True, blank=True)
    supervisor_1 = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rosterSupervisor1",
    )
    supervisor_2 = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rosterSupervisor2",
    )
    is_absent = models.IntegerField(null=True, blank=True, editable=False, default=1)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="roster_created_by",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="roster_updated_by",
    )

    def clean(self):
        if self.shiftLegend is None:
            shiftLegend = ShiftLegend.objects.filter(
                shift_start_time=self.start_time, shift_end_time=self.end_time
            ).first()

            if not shiftLegend:
                raise ValidationError(
                    "No Shift Legend found for the specified time range."
                )

            self.shiftLegend = shiftLegend

    def save(self, *args, **kwargs):
        self.clean()  # Ensure clean is called before saving
        super().save(*args, **kwargs)

    def __str__(self):
        # return "{user} on {date} from {start} to {end}".format(user=self.employee.user.name,date=self.start_date,start = self.start_time,end=self.end_time)
        return "{employeeName} : {date} from {start} to {end}".format(
            employeeName=self.employee.user.name,
            date=self.start_date,
            start=self.start_time,
            end=self.end_time,
        )


class RosterCount(BaseModel):
    site = models.ForeignKey(
        Site, on_delete=models.SET_NULL, null=True, related_name="roster_count_site"
    )
    process = models.ForeignKey(
        Process,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="roster_count_process",
    )
    lob = models.ForeignKey(
        LOB,
        on_delete=models.SET_NULL,
        null=True,
        related_name="roster_count_lob",
    )
    workRole = models.ForeignKey(
        WorkRole,
        on_delete=models.SET_NULL,
        null=True,
        related_name="roster_count_workRole",
    )
    start_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_date = models.DateField()
    end_time = models.TimeField(null=True, blank=True)
    hour_00 = models.IntegerField(blank=True, null=True, default=0)
    hour_01 = models.IntegerField(blank=True, null=True, default=0)
    hour_02 = models.IntegerField(blank=True, null=True, default=0)
    hour_03 = models.IntegerField(blank=True, null=True, default=0)
    hour_04 = models.IntegerField(blank=True, null=True, default=0)
    hour_05 = models.IntegerField(blank=True, null=True, default=0)
    hour_06 = models.IntegerField(blank=True, null=True, default=0)
    hour_07 = models.IntegerField(blank=True, null=True, default=0)
    hour_08 = models.IntegerField(blank=True, null=True, default=0)
    hour_09 = models.IntegerField(blank=True, null=True, default=0)
    hour_10 = models.IntegerField(blank=True, null=True, default=0)
    hour_11 = models.IntegerField(blank=True, null=True, default=0)
    hour_12 = models.IntegerField(blank=True, null=True, default=0)
    hour_13 = models.IntegerField(blank=True, null=True, default=0)
    hour_14 = models.IntegerField(blank=True, null=True, default=0)
    hour_15 = models.IntegerField(blank=True, null=True, default=0)
    hour_16 = models.IntegerField(blank=True, null=True, default=0)
    hour_17 = models.IntegerField(blank=True, null=True, default=0)
    hour_18 = models.IntegerField(blank=True, null=True, default=0)
    hour_19 = models.IntegerField(blank=True, null=True, default=0)
    hour_20 = models.IntegerField(blank=True, null=True, default=0)
    hour_21 = models.IntegerField(blank=True, null=True, default=0)
    hour_22 = models.IntegerField(blank=True, null=True, default=0)
    hour_23 = models.IntegerField(blank=True, null=True, default=0)
    count = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        isNewInstance = self.pk is None  # Check if the instance is being newly saved

        # if isNewInstance:
        #     self.count = 1
        # else:
        #     self.count += 1

        # Calculate the hours between start_time and end_time
        if self.start_time and self.end_time:
            start_hour = self.start_time.hour
            end_hour = self.end_time.hour
            # Update the corresponding hour fields
            for hour in range(start_hour, end_hour + 1):
                fieldName = f"hour_{hour:02d}"
                setattr(self, fieldName, self.count)

        # Save the updated instance
        super().save(*args, **kwargs)

        # If the instance is being newly saved, save the updated hour fields
        if isNewInstance:
            self.save(
                update_fields=[
                    f"hour_{hour:02d}" for hour in range(start_hour, end_hour + 1)
                ]
            )

    def __str__(self):
        return f"Date: {self.start_date} {self.start_time} - {self.end_date} {self.end_time}, Site:{self.site}, Process: {self.process}, LOB: {self.lob} Count: {self.count}"


class RosterSeatCount(BaseModel):
    site = models.ForeignKey(
        Site,
        on_delete=models.SET_NULL,
        null=True,
        related_name="roster_seat_count_site",
    )
    process = models.ForeignKey(
        Process,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="roster_seat_count_process",
    )
    lob = models.ForeignKey(
        LOB,
        on_delete=models.SET_NULL,
        null=True,
        related_name="roster_seat_count_lob",
    )
    total = models.IntegerField(default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="roster_seat_count_created_by",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="roster_seat_count_updated_by",
    )

    def __str__(self):
        return f"Site: {self.site} Process: {self.process} LOB: {self.lob} Total: {self.total}"


class WorkRule(BaseModel):
    consecutive_working_days = models.IntegerField(default=0)
    maximum_regular_shift_duration = models.IntegerField(default=0)
    minimum_regular_shift_duration = models.IntegerField(default=0)
    gap_between_shift_end_to_the_next_shift_start_time = models.IntegerField(default=0)
    female_shift_start_time = models.TimeField()
    female_shift_end_time = models.TimeField()
    prohibited_time_for_end_of_a_shift_start_time = models.TimeField()
    prohibited_time_for_end_of_a_shift_end_time = models.TimeField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="workRule_created_by",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="workRule_updated_by",
    )


class Forecast(BaseModel):
    date = models.DateField()
    process = models.ForeignKey(
        Process,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="forecast_process",
    )
    lob = models.ForeignKey(
        LOB,
        on_delete=models.SET_NULL,
        null=True,
        related_name="forecast_lob",
    )
    interval = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(23)]
    )
    forecast = models.IntegerField()
    required_hc = models.IntegerField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="forecast_created_by",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="forecast_updated_by",
    )

    def __str__(self):
        return f"{self.date} - {self.process} - {self.lob} - Interval {self.interval}"


class ACD(BaseModel):
    MONTH_CHOICES = [
        ("January", "January"),
        ("February", "February"),
        ("March", "March"),
        ("April", "April"),
        ("May", "May"),
        ("June", "June"),
        ("July", "July"),
        ("August", "August"),
        ("September", "September"),
        ("October", "October"),
        ("November", "November"),
        ("December", "December"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="acd_employee",
    )
    month = models.CharField(max_length=20, choices=MONTH_CHOICES)
    year = models.PositiveIntegerField()
    acd_calls = models.IntegerField()
    avg_acd_time = models.FloatField()
    avg_acw_time = models.FloatField()
    agent_occupancy_with_acw = models.IntegerField()
    agent_occupancy_without_acw = models.IntegerField()
    extn_in_calls = models.IntegerField()
    avg_extn_in_time = models.FloatField()
    extn_out_calls = models.IntegerField()
    avg_extn_out_time = models.FloatField()
    acd_time = models.BigIntegerField()
    acw_time = models.BigIntegerField()
    agent_ring_time = models.IntegerField()
    other_time = models.IntegerField()
    aux_time = models.BigIntegerField()
    avail_time = models.BigIntegerField()
    staffed_time = models.BigIntegerField()
