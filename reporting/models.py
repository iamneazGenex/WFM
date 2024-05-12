from django.db import models
from accounts.models import *
from roster.models import *

# Create your models here.
from django.db import models


# Create your models here.
class BaseModel(models.Model):
    created_At = models.DateTimeField(auto_now_add=True)
    updated_At = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AgentHourlyPerformance(BaseModel):
    date = models.DateField()
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="agentHourlyPerformance_employee",
        blank=True,  # Set this to True to allow the field to be blank
        null=True,  # Also set null to True to allow the field to be nullable in the database
    )
    skill = models.ForeignKey(
        Skill, on_delete=models.CASCADE, related_name="agentHourlyPerformance_skill"
    )
    roster = models.ForeignKey(
        Roster,
        on_delete=models.SET_NULL,
        null=True,
        related_name="agentHourlyPerformance_roster",
        editable=False,
    )
    time_interval_start = models.TimeField(null=True, blank=True)
    time_interval_end = models.TimeField(null=True, blank=True)
    hour = models.IntegerField(null=True, blank=True, editable=False)
    hold_time = models.FloatField(null=True, blank=True, editable=False)
    handling_time = models.FloatField(null=True, blank=True, editable=False)
    ready_time = models.FloatField(null=True, blank=True, editable=False)
    acd_calls = models.IntegerField(null=True, blank=True)
    avg_acd_time = models.FloatField(null=True, blank=True)
    avg_acw_time = models.FloatField(null=True, blank=True)
    percent_agent_occup_with_acw = models.IntegerField(null=True, blank=True)
    percent_agent_occup_without_acw = models.IntegerField(null=True, blank=True)
    extn_in_calls = models.IntegerField(null=True, blank=True)
    avg_extn_in_time = models.FloatField(null=True, blank=True)
    extn_out_calls = models.IntegerField(null=True, blank=True)
    avg_extn_out_time = models.FloatField(null=True, blank=True)
    acd_time = models.IntegerField(null=True, blank=True)
    acw_time = models.IntegerField(null=True, blank=True)
    agent_ring_time = models.IntegerField(null=True, blank=True)
    other_time = models.IntegerField(null=True, blank=True)
    aux_time = models.IntegerField(null=True, blank=True)
    avail_time = models.IntegerField(null=True, blank=True)
    percent_skills_avail = models.IntegerField(null=True, blank=True)
    staffed_time = models.IntegerField(null=True, blank=True)
    trans_out = models.IntegerField(null=True, blank=True)
    held_calls = models.IntegerField(null=True, blank=True)
    avg_hold_time = models.FloatField(null=True, blank=True)
    aux_work_on_login = models.IntegerField(null=True, blank=True)
    short_break = models.IntegerField(null=True, blank=True)
    lunch_break = models.IntegerField(null=True, blank=True)
    training = models.IntegerField(null=True, blank=True)
    one_to_one = models.IntegerField(null=True, blank=True)
    meeting = models.IntegerField(null=True, blank=True)
    outbound_callback = models.IntegerField(null=True, blank=True)
    cfs_meeting = models.IntegerField(null=True, blank=True)
    hour_8 = models.IntegerField(null=True, blank=True)
    hour_9 = models.IntegerField(null=True, blank=True)
    ti_auxtime10 = models.IntegerField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="agentHourlyPerformance_created_by",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="agentHourlyPerformance_updated_by",
    )

    def clean(self):
        time_interval = self.time_interval_start
        if time_interval:
            self.hour = time_interval.strftime("%H")
        avg_hold_time = self.avg_hold_time
        if avg_hold_time:
            self.hold_time = self.held_calls * self.avg_hold_time
        else:
            self.hold_time = 0
        self.handling_time = self.acd_time + self.acw_time + self.hold_time
        self.ready_time = (
            self.acd_time
            + self.acw_time
            + self.agent_ring_time
            + self.other_time
            + self.avail_time
            + self.training
            + self.one_to_one
            + self.meeting
            + self.outbound_callback
            + self.cfs_meeting
        )
        try:
            self.roster = Roster.objects.get(
                employee=self.employee, start_date=self.date
            )
        except Roster.DoesNotExist:
            print(f"Roster does not exist of employee {self.employee}")
            self.roster = None
        except Exception as e:
            print(f"Exception : {e}")
            self.roster = None
        if self.roster != None:
            if self.roster.shiftLegend.shift_count == 1 and self.staffed_time > 0:
                if self.roster.is_absent != 0:
                    self.roster.is_absent = 0
                    self.roster.save()

    def save(self, *args, **kwargs):
        self.clean()  # Ensure clean is called before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.date} - {self.employee}"


class AvayaCDR(BaseModel):
    date = models.DateField()
    skill = models.ForeignKey(
        Skill, on_delete=models.CASCADE, related_name="avayaCDR_skill"
    )
    time_interval = models.TimeField()
    hour = models.IntegerField(editable=False)
    offer = models.IntegerField(null=True, blank=True)
    answer = models.IntegerField(null=True, blank=True)
    ans_th = models.IntegerField(null=True, blank=True)
    aban_calls = models.IntegerField(null=True, blank=True)
    abn_th = models.IntegerField(null=True, blank=True)
    avg_acd_time = models.FloatField(null=True, blank=True)
    avg_hold_time = models.FloatField(null=True, blank=True)
    avg_acw_time = models.FloatField(null=True, blank=True)
    avg_speed_ans = models.FloatField(null=True, blank=True)
    staffed_time = models.IntegerField(null=True, blank=True)
    acd_time = models.IntegerField(null=True, blank=True)
    acw_time = models.IntegerField(null=True, blank=True)
    hold_time = models.IntegerField(null=True, blank=True)
    avail_time = models.IntegerField(null=True, blank=True)
    aux_time = models.IntegerField(null=True, blank=True)
    agent_ring_time = models.IntegerField(null=True, blank=True)
    other_time = models.IntegerField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="avayaCDR_created_by",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="avayaCDR_updated_by",
    )

    def clean(self):
        time_interval = self.time_interval
        if time_interval:
            self.hour = time_interval.strftime("%H")

    def save(self, *args, **kwargs):
        self.clean()  # Ensure clean is called before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.date} - {self.skill} - {self.time_interval}"


class LoginLogoutTime(BaseModel):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="loginLogout_employee",
    )
    login_date = models.DateField()
    login_time = models.DateTimeField()
    logout_date = models.DateField(null=True, blank=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="loginLogout_created_by",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="loginLogout_updated_by",
    )

    def __str__(self):
        return f"{self.employee} - {self.login_time} to  {self.logout_time}"
