from accounts.models import Employee, CustomUser, Supervisor
from django import forms
from django.utils import timezone


def getEmployee(id):
    """
    Get the employee

    Args:
        id (int): The id of CustomUser object

    Returns:
        Employee: An instance of Employee
    """
    user = CustomUser.objects.get(id=id)
    employee = Employee.objects.filter(user=user).first()
    return employee


def getSupervisor(id):
    """
    Get the supervisor

    Args:
        id (int): The id of CustomUser object

    Returns:
        Supervisor: An instance of Supervisor object
    """
    user = CustomUser.objects.get(id=id)
    supervisor = Supervisor.objects.get(user=user)
    return supervisor


def logString(value, type):
    """Builds a formatted string for logging

    Args:
        value (string): the string
        type (int): 1 = Header, 2 = Checking, 3 = Passed, 4 = Failed, 5 = Error

    Returns:
        string: formatted string
    """
    string = ""
    if type == 1:
        string = "------||" + value + "||------"
    elif type == 2:
        string = "--Checking--" + value
    elif type == 3:
        string = "|Passed| " + value
    elif type == 4:
        string = "|Failed| " + value
    elif type == 5:
        string = "|Error| " + value
    else:
        string = value
    return string


def getTimeWidget():
    return forms.widgets.TimeInput(
        format="%H:%M", attrs={"type": "time", "class": "form-control"}
    )


def getDateWidget():
    return forms.widgets.DateInput(
        attrs={
            "type": "date",
            "placeholder": "yyyy-mm-dd (DOB)",
            "class": "form-control",
        }
    )


def timedelta_to_timefield(timedelta_value):
    # Calculate hours, minutes, and seconds
    hours, remainder = divmod(timedelta_value.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Create a new timezone-aware datetime object with today's date and the calculated time
    time_value = timezone.now().replace(hour=hours, minute=minutes, second=seconds)

    return time_value.time()
