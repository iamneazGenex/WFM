from django.db import models
from accounts.models import Employee, Supervisor
from roster.models import Roster
import logging
from .emailUtils_shiftTimeTrading import *
from django.db.models.signals import post_save
from django.db.models.signals import Signal
from django.dispatch import receiver

logger = logging.getLogger(__name__)


# Create your models here.
class BaseModel(models.Model):
    created_At = models.DateTimeField(auto_now_add=True)
    updated_At = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class DayOffTrading(BaseModel):
    APPROVALSTATUS_CHOICES = (
        ("", "----"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )
    TRADINGSTATUS_CHOICES = (
        ("", "----"),
        ("in process", "In Process"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )
    requestor = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="day_off_trading_requestor"
    )
    requestee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="day_off_trading_requestee"
    )
    requestor_swap_roster = models.ForeignKey(
        Roster, on_delete=models.CASCADE, related_name="requestor_swap_roster"
    )
    requestor_trade_roster = models.ForeignKey(
        Roster, on_delete=models.CASCADE, related_name="requestor_trade_roster"
    )
    requestee_swap_roster = models.ForeignKey(
        Roster, on_delete=models.CASCADE, related_name="requestee_swap_roster"
    )
    requestee_trade_roster = models.ForeignKey(
        Roster, on_delete=models.CASCADE, related_name="requestee_trade_roster"
    )
    requestee_approval_status = models.CharField(
        default=None,
        max_length=50,
        null=True,
        choices=APPROVALSTATUS_CHOICES,
        blank=True,
    )
    requestee_approval_status_datetime = models.DateTimeField(null=True, blank=True)
    supervisor = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dayOffTradingSupervisor",
    )
    supervisor_approval_status = models.CharField(
        default=None,
        max_length=50,
        null=True,
        choices=APPROVALSTATUS_CHOICES,
        blank=True,
    )
    supervisor_approval_status_datetime = models.DateTimeField(null=True, blank=True)
    trading_status = models.CharField(
        default=None,
        max_length=50,
        choices=TRADINGSTATUS_CHOICES,
    )

    def save(self, *args, **kwargs):
        subject = "[RMS] Day Trade Off Request"

        def sendEmailToRequesteeWhenDayOffTradingIsCreated():
            """
            Send Email notification to requestee
            """
            message = "Dear {requesteeName},\n{requestorName} has sent you a day trade off request.\nYour Trade Details:\nTrade Day:{tradeDate}\nSwap Day: {swapDate}\n\n Please Visit the website to accept or decline the request.".format(
                requesteeName=self.requestee.user.name,
                requestorName=self.requestor.user.name,
                tradeDate=self.requestee_trade_roster.start_date,
                swapDate=self.requestee_swap_roster.start_date,
            )
            # recipientList = [
            #     self.requestee.user.email,
            # ]
            recipientList = [
                "alamin.neaz@genexinfosys.com",
            ]
            result = sendEmail(
                subject=subject, message=message, recipientList=recipientList
            )

        def sendEmailToPeopleWhenRequesteeApproves():
            logging.info(
                "Trying to send email to requestor({requestor}) after requestee({requestee}) approval".format(
                    requestor=self.requestor.user.email,
                    requestee=self.requestee.user.email,
                )
            )
            #   Send Email notification to requestor after approved
            message = "Dear {requestorName},\n{requesteeName} has accepted your day trade off request. Your trade request is being forwared to the superviosors for further approval.\nYour Trade Details:\nTrade Day:{tradeDate}\nSwap Day: {swapDate}.".format(
                requesteeName=self.requestee.user.name,
                requestorName=self.requestor.user.name,
                tradeDate=self.requestor_trade_roster.start_date,
                swapDate=self.requestor_swap_roster.start_date,
            )
            # recipientList = [
            #     self.requestor.user.email,
            # ]
            recipientList = [
                "alamin.neaz@genexinfosys.com",
            ]
            result = sendEmail(
                subject=subject, message=message, recipientList=recipientList
            )
            if result is True:
                logging.info(
                    "Email sent to {user} SUCCESSFULLY".format(
                        user=self.requestor.user.email
                    )
                )
            else:
                logging.error(
                    "FAILED to send Email to {user}".format(
                        user=self.requestor.user.email
                    )
                )
            #   Send Email notification to the supervisors
            #   Requestor supervisors
            logging.info(
                "Trying to send email to requestor({requestor})  Supervisor({supervisor}) after requestee({requestee}) approval".format(
                    requestor=self.requestor.user.email,
                    supervisor=self.requestor.supervisor_1.user.email,
                    requestee=self.requestee.user.email,
                )
            )
            supervisor = self.requestor.supervisor_1
            message = "Dear {supervisorName},\n{requestorName} has sent day trade off request to {requesteeName}.\nRequestor Trade Details:\nTrade Day:{requestorTradeDate}\nSwap Day: {requestorSwapDate}\n\nRequestee Trade Details:\nTrade Day:{requesteeTradeDate}\nSwap Day: {requesteeSwapDate}\n\nPlease Visit the website to accept or decline the request.".format(
                requesteeName=self.requestee.user.name,
                requestorName=self.requestor.user.name,
                requestorTradeDate=self.requestor_trade_roster.start_date,
                requestorSwapDate=self.requestor_swap_roster.start_date,
                requesteeTradeDate=self.requestee_trade_roster.start_date,
                requesteeSwapDate=self.requestee_swap_roster.start_date,
                supervisorName=supervisor.user.name,
            )
            # recipientList = [
            #     supervisor.user.email,
            # ]
            recipientList = [
                "alamin.neaz@genexinfosys.com",
            ]
            result = sendEmail(
                subject=subject, message=message, recipientList=recipientList
            )
            if result is True:
                logging.info(
                    "Email sent to {user} SUCCESSFULLY".format(
                        user=supervisor.user.name
                    )
                )
            else:
                logging.error(
                    "FAILED to send Email to {user}".format(user=supervisor.user.name)
                )
            #   Requestee supervisors
            logging.info(
                "Trying to send email to requestor({requestor})  Supervisor({supervisor}) after requestee({requestee}) approval".format(
                    requestor=self.requestor.user.email,
                    supervisor=self.requestee.supervisor_1.user.email,
                    requestee=self.requestee.user.email,
                )
            )
            supervisor = self.requestee.supervisor_1
            message = "Dear {supervisorName},\n{requestorName} has sent day trade off request to {requesteeName}.\nRequestor Trade Details:\nTrade Day:{requestorTradeDate}\nSwap Day: {requestorSwapDate}\n\nRequestee Trade Details:\nTrade Day:{requesteeTradeDate}\nSwap Day: {requesteeSwapDate}\n\nPlease Visit the website to accept or decline the request.".format(
                requesteeName=self.requestee.user.name,
                requestorName=self.requestor.user.name,
                requestorTradeDate=self.requestor_trade_roster.start_date,
                requestorSwapDate=self.requestor_swap_roster.start_date,
                requesteeTradeDate=self.requestee_trade_roster.start_date,
                requesteeSwapDate=self.requestee_swap_roster.start_date,
                supervisorName=supervisor.user.name,
            )
            # recipientList = [
            #     supervisor.user.email,
            # ]
            recipientList = [
                "alamin.neaz@genexinfosys.com",
            ]
            result = sendEmail(
                subject=subject, message=message, recipientList=recipientList
            )
            if result is True:
                logging.info(
                    "Email sent to {user} SUCCESSFULLY".format(
                        user=supervisor.user.name
                    )
                )
            else:
                logging.error(
                    "FAILED to send Email to {user}".format(user=supervisor.user.name)
                )

        def sendEmailToPeopleWhenRequesteeRejects():
            logging.info(
                "Trying to send email to requestor({requestor}) after requestee({requestee}) rejection".format(
                    requestor=self.requestor.user.email,
                    requestee=self.requestee.user.email,
                )
            )
            #   Send Email notification to requestor after rejected
            message = "Dear {requestorName},\n{requesteeName} has rejected your day trade off request.".format(
                requesteeName=self.requestee.user.name,
                requestorName=self.requestor.user.name,
            )
            # recipientList = [
            #     self.requestor.user.email,
            # ]
            recipientList = [
                "alamin.neaz@genexinfosys.com",
            ]
            result = sendEmail(
                subject=subject, message=message, recipientList=recipientList
            )
            if result is True:
                logging.info(
                    "Email sent to {user} SUCCESSFULLY".format(
                        user=self.requestor.user.name
                    )
                )
            else:
                logging.error(
                    "FAILED to send Email to {user}".format(
                        user=self.requestor.user.name
                    )
                )

        def sendEmailToPeopleWhenSupervisorApproves():
            """
            Send Email notification to requestor and requestee after Supervisor approves
            """
            logging.info(
                "Trying to send email to requestor({requestor}) and requestee({requestee}) after supervisor({supervisor}) approves".format(
                    requestor=self.requestor.user.email,
                    requestee=self.requestee.user.email,
                    supervisor=self.supervisor.user.email,
                )
            )
            #   Send Email notification to requestor after approved
            message = "The Day Off trade Request has been granted by {supervisorName}\n\nT".format(
                supervisorName=self.supervisor.user.name,
            )
            # recipientList = [
            #     self.requestor.user.email,
            #     self.requestee.user.email,
            # ]
            recipientList = ["alamin.neaz@genexinfosys.com", "neazahmedneaz@gmail.com"]
            result = sendEmail(
                subject=subject, message=message, recipientList=recipientList
            )
            if result is True:
                logging.info(
                    "Email sent to {user} SUCCESSFULLY".format(
                        user="".join(recipientList)
                    )
                )
            else:
                logging.error(
                    "FAILED to send Email to {user}".format(user="".join(recipientList))
                )

        def sendEmailToPeopleWhenSupervisorDeclines():
            """
            Send Email notification to requestor and requestee after Supervisor declines
            """
            logging.info(
                "Trying to send email to requestor({requestor}) and requestee({requestee}) after supervisor({supervisor}) declined".format(
                    requestor=self.requestor.user.email,
                    requestee=self.requestee.user.email,
                    supervisor=self.supervisor.user.email,
                )
            )
            #   Send Email notification to requestor after approved
            message = "The Day Off trade Request has been rejected by {supervisorName}\n\nT".format(
                supervisorName=self.supervisor.user.name,
            )
            # recipientList = [
            #     self.requestor.user.email,
            #     self.requestee.user.email,
            # ]
            recipientList = ["alamin.neaz@genexinfosys.com", "neazahmedneaz@gmail.com"]
            result = sendEmail(
                subject=subject, message=message, recipientList=recipientList
            )
            if result is True:
                logging.info(
                    "Email sent to {user} SUCCESSFULLY".format(
                        user="".join(recipientList)
                    )
                )
            else:
                logging.error(
                    "FAILED to send Email to {user}".format(user="".join(recipientList))
                )

        # you can check if object just created by comparing "pk" attr to None
        # you can also use _state attr see doc link below
        is_created = self.pk is None
        super(DayOffTrading, self).save(*args, **kwargs)

        if is_created:
            #   Send Email notification to requestee
            sendEmailToRequesteeWhenDayOffTradingIsCreated()
        else:
            if self.supervisor_approval_status is not None:
                if self.supervisor_approval_status == "approved":
                    sendEmailToPeopleWhenSupervisorApproves()
                elif self.supervisor_approval_status == "rejected":
                    sendEmailToPeopleWhenSupervisorDeclines()
            else:
                if self.requestee_approval_status == "approved":
                    sendEmailToPeopleWhenRequesteeApproves()
                elif self.requestee_approval_status == "rejected":
                    sendEmailToPeopleWhenRequesteeRejects()


class ShiftTimeTrading(BaseModel):
    APPROVALSTATUS_CHOICES = (
        ("", "----"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )
    TRADINGSTATUS_CHOICES = (
        ("", "----"),
        ("in process", "In Process"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )
    requestor = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="shift_time_trading_requestor"
    )
    requestee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="shift_time_trading_requestee"
    )
    requestor_swap_roster = models.ForeignKey(
        Roster,
        on_delete=models.CASCADE,
        related_name="requestor_shift_time_swap_roster",
    )
    requestor_start_time = models.TimeField()
    requestor_end_time = models.TimeField()
    requestee_swap_roster = models.ForeignKey(
        Roster,
        on_delete=models.CASCADE,
        related_name="requestee_shift_time_swap_roster",
    )
    requestee_start_time = models.TimeField()
    requestee_end_time = models.TimeField()
    requestee_approval_status = models.CharField(
        default=None,
        max_length=50,
        null=True,
        choices=APPROVALSTATUS_CHOICES,
        blank=True,
    )
    requestee_approval_status_datetime = models.DateTimeField(null=True, blank=True)
    supervisor = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shift_time_trading_supervisor",
    )
    supervisor_approval_status = models.CharField(
        default=None,
        max_length=50,
        null=True,
        choices=APPROVALSTATUS_CHOICES,
        blank=True,
    )
    supervisor_approval_status_datetime = models.DateTimeField(null=True, blank=True)
    trading_status = models.CharField(
        default=None,
        max_length=50,
        choices=TRADINGSTATUS_CHOICES,
    )

    def save(self, *args, **kwargs):
        is_created = self.pk is None
        super(ShiftTimeTrading, self).save(*args, **kwargs)
        # you can check if object just created by comparing "pk" attr to None
        # you can also use _state attr see doc link below
        # if is_created:
        #     #   Send Email notification to requestee
        #     # isCreated(self)
        #     # post_save.connect(isCreated, sender=ShiftTimeTrading)
        #     pass
        # else:
        #     if self.supervisor_approval_status is not None:
        #         if self.supervisor_approval_status == "approved":
        #             supervisorApproves(self)
        #         elif self.supervisor_approval_status == "rejected":
        #             supervisorDeclines(self)
        #     else:
        #         if self.requestee_approval_status == "approved":
        #             requesteeApproves(self)
        #         elif self.requestee_approval_status == "rejected":
        #             requesteeRejects(self)


@receiver(post_save, sender=ShiftTimeTrading)
def shiftTimeTradingSignal(sender, instance, **kwargs):
    is_created = instance.pk is None
    if (
        instance.supervisor_approval_status is None
        and instance.requestee_approval_status is None
    ):
        #   Send Email notification to requestee
        logger.info("Here")
        # pass
        isCreated(instance)
    else:
        if instance.supervisor_approval_status is not None:
            if instance.supervisor_approval_status == "approved":
                supervisorApproves(instance)
            elif instance.supervisor_approval_status == "rejected":
                supervisorDeclines(instance)
        else:
            if instance.requestee_approval_status == "approved":
                requesteeApproves(instance)
            elif instance.requestee_approval_status == "rejected":
                requesteeRejects(instance)
