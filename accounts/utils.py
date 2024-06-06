from .models import *
from django.contrib import messages
from django.contrib.auth.models import Group
import logging
from django.db import transaction
from rms.global_utilities import *

logger = logging.getLogger(__name__)


def customUserCreation(request, data, groupName):
    logger.info("Trying to create user")
    success = False
    error = ""
    user = None
    skip = False
    try:
        user = CustomUser.objects.get(email=data["email"])

        error = "User with this email: {email} already exist".format(
            email=data["email"]
        )
        messages.error(request, error)
        logger.error(f"----{error}")
        skip = True
    except CustomUser.DoesNotExist:
        try:
            CustomUser.objects.get(employee_id=data["employee_id"])
            user = None
            error = "User with this Employee Id: {employee_id} already exist".format(
                employee_id=data["employee_id"]
            )
            logger.error(f"----{error}")
            messages.error(request, error)
            skip = True
        except CustomUser.DoesNotExist:
            try:
                user = CustomUser(
                    email=data["email"].lower(),
                    name=data["name"],
                    employee_id=data["employee_id"],
                    system_id=data["system_id"],
                )
                user.set_password(str(data["password1"]))
                if "is_active" in data:
                    user.is_active = data["is_active"]
                else:
                    user.is_active = True
                user.created_by = CustomUser.objects.get(id=request.user.id)
                user.save()
                employeeGroup = Group.objects.get(name=groupName)
                user.groups.add(employeeGroup)
                user.save()
                success = True
                logger.info("User Created Successfully")
            except Exception as e:
                logger.error(
                    f"----|Failed| Could not create CustomUser. Exception: {e}"
                )
                success = False
                user = None
    return success, user, skip


def createSingleNameModel(request, model, formType):
    success = False
    form = formType(request.POST)
    if form.is_valid():
        data = form.cleaned_data
        name = data["name"].lower()
        if model.objects.filter(name=name).exists():
            messages.error(
                request,
                '{model} with the name "{name}" already exists.'.format(
                    model=model._meta.verbose_name.title(), name=name
                ),
            )
        else:
            try:
                instance = model(
                    name=name, created_by=CustomUser.objects.get(id=request.user.id)
                )
                instance.save()
                messages.success(
                    request,
                    "{model} Created successfully.".format(
                        model=model._meta.verbose_name.title()
                    ),
                )
                success = True
            except Exception as e:
                messages.error(request, "Exception:{exception}".format(exception=e))
    else:
        messages.error(request, "Form is not valid")

    return success


def supervisorCreation(data, request, bulk):
    success = False
    userCreationResult, user = customUserCreation(request, data, "Supervisor")
    if userCreationResult == True:
        try:
            process = Process.objects.get(name=data["process"])
            site = Site.objects.get(name=data["site"])
            workRole = WorkRole.objects.get(name=data["work_role"])
            supervisor = Supervisor(
                user=user,
                process=process,
                gender=data["gender"],
                site=site,
                work_role=workRole,
                created_by=CustomUser.objects.get(id=request.user.id),
            )
            supervisor.save()
            success = True
            if bulk == False:
                messages.success(request, "Supervisor Created successfully.")
        except Exception as e:
            messages.error(request, "Exception:{exception}".format(exception=e))

    return success


def employeeCreation(data, request, bulk, group="Employee", index=0):
    logger.info("Trying to create employee")
    success = False
    with transaction.atomic():
        userCreationResult, user, skip = customUserCreation(request, data, group)
        if skip == True:
            success = True
            message = f"Skipping {group} creation for index {index}"
            logging.info(f"----{message}")
            messages.success(request, message)
        else:
            if userCreationResult == True:
                process = get_or_none(Process, data.get("process"))
                site = get_or_none(Site, data.get("site"))
                workRole = get_or_none(WorkRole, data.get("work_role"))
                lob = get_or_none(LOB, data.get("lob"))
                try:
                    employee = Employee(
                        user=user,
                        process=process,
                        gender=data["gender"],
                        site=site,
                        work_role=workRole,
                        lob=lob,
                        pick_drop_location=data["pick_drop_location"],
                        supervisor_1=data["supervisor_1"],
                        supervisor_2=data["supervisor_2"],
                        created_by=CustomUser.objects.get(id=request.user.id),
                    )
                    employee.save()
                    if bulk == False:
                        logging.info("Employee Created successfully.")
                        messages.success(request, "Employee Created successfully.")
                    success = True
                except Exception as e:
                    user.delete()
                    logging.error("Exception:{exception}".format(exception=e))
                    messages.error(request, "Exception:{exception}".format(exception=e))

    return success
