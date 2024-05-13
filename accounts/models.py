from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager
from django.utils import timezone
from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.db.models import Q
from django.contrib.auth.signals import user_logged_in

# Create your models here.


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Site(BaseModel):
    name = models.CharField(max_length=200)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="site_created_by",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="site_updated_by",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Process(BaseModel):
    name = models.CharField(max_length=200)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="process_created_by",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="process_updated_by",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class LOB(BaseModel):
    name = models.CharField(max_length=200)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lob_created_by",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lob_updated_by",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class WorkRole(BaseModel):
    name = models.CharField(max_length=200)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="workRole_created_by",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="workRole_updated_by",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Skill(BaseModel):
    name = models.CharField(max_length=200)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="skill_created_by",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="skill_updated_by",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class CustomUser(AbstractBaseUser, PermissionsMixin, BaseModel):
    # username = None
    email = models.EmailField(verbose_name="email address", max_length=255, unique=True)
    name = models.CharField(max_length=255)
    employee_id = models.IntegerField(default=0, blank=True)
    # system_id = models.IntegerField(default=0, blank=True)
    system_id = models.CharField(max_length=50, default="0", blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customUser_created_by",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customUser_updated_by",
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.name

    def is_WFM(self):
        return self.groups.filter(name="WFM").exists()

    def is_Supervisor(self):
        return self.groups.filter(name="Supervisor").exists()

    def is_Employee(self):
        return self.groups.filter(name="Employee").exists()

    def userType(self):
        if self.groups.filter(name="WFM").exists():
            return "WFM"
        elif self.groups.filter(name="Supervisor").exists():
            return "Supervisor"
        else:
            return "Employee"


class Supervisor(BaseModel):
    GENDER_CHOICES = (("", "----"), ("M", "Male"), ("F", "Female"))

    SITE_CHOICES = (("", "----"), ("DHK", "Dhaka"), ("CTG", "Chittagong"))

    WORKROLE_CHOICES = (
        ("", "----"),
        ("TL", "Team Leader"),
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="supervisor",
    )
    process = models.ForeignKey(
        Process,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supervisorProcess",
    )
    gender = models.CharField(
        default="N/A", max_length=50, null=True, choices=GENDER_CHOICES, blank=True
    )
    site = models.ForeignKey(
        Site,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supervisorSite",
    )
    work_role = models.ForeignKey(
        WorkRole,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supervisorWorkRole",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supervisor_created_by",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supervisor_updated_by",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.user.name


class Employee(BaseModel):
    GENDER_CHOICES = (("M", "Male"), ("F", "Female"))

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="employee",
    )
    process = models.ForeignKey(
        Process,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employeeProcess",
    )
    gender = models.CharField(
        default="N/A", max_length=50, null=True, choices=GENDER_CHOICES
    )
    site = models.ForeignKey(
        Site,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employeeSite",
    )
    work_role = models.ForeignKey(
        WorkRole,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employeeWorkRole",
    )
    lob = models.ForeignKey(
        LOB,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employeeLOB",
    )
    pick_drop_location = models.CharField(max_length=255, blank=True, null=True)
    vdi = models.CharField(max_length=255, default="", blank=True, null=True)
    avaya_id = models.IntegerField(default=0, blank=True, null=True)
    doj = models.DateField(null=True, blank=True)
    is_absent = models.IntegerField(null=True, blank=True, editable=False, default=0)
    supervisor_1 = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supervisor1",
    )
    supervisor_2 = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supervisor2",
    )
    is_previously_logged_in = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_created_by",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_updated_by",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.user.name

    def is_supervisor(self):
        """
        Check if the current employee is listed as a supervisor for any other employees.
        Returns True if listed as a supervisor for any other employee, False otherwise.
        """
        return (
            Employee.objects.filter(Q(supervisor_1=self) | Q(supervisor_2=self))
            .exclude(id=self.id)
            .exists()
        )


@receiver(pre_delete, sender=Employee)
def delete_related_user(sender, instance, **kwargs):
    # Disconnect the signal to avoid recursion
    pre_delete.disconnect(delete_related_user, sender=Employee)
    # Check if the related user exists before attempting to delete
    if instance.user:
        instance.user.delete()
    # Reconnect the signal for future deletions
    pre_delete.connect(delete_related_user, sender=Employee)


# Connect the signal receiver function
pre_delete.connect(delete_related_user, sender=Employee)
