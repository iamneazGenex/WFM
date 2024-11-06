import logging
from .utils import *
from django.conf import settings

logger = logging.getLogger(__name__)

subject = "[RMS] Shift Time Trading Request"


def tradeDetails(self):
    return (
        "<div style='padding: 10px;'>"
        "<h4><b>Trading Details</b></h4>"
        "<table style='width: 100%; border-collapse: collapse;'>"
        "<tr><td><b>Trade Date:</b></td><td>{}</td></tr>"
        "<tr><td><b>Requestor:</b></td><td>{}</td></tr>"
        "<tr><td><b>Current Roster Time:</b></td><td>{} to {}</td></tr>"
        "<tr><td colspan='2' style='padding-top: 15px;'><b>Requestee Details</b></td></tr>"
        "<tr><td><b>Requestee:</b></td><td>{}</td></tr>"
        "<tr><td><b>Current Roster Time:</b></td><td>{} to {}</td></tr>"
        "</table>"
        "</div>"
    ).format(
        self.requestee_swap_roster.start_date,
        self.requestor.user.name,
        self.requestor_start_time,
        self.requestor_end_time,
        self.requestee.user.name,
        self.requestee_start_time,
        self.requestee_end_time,
    )


def isCreated(self):
    """
    Send Email to REQUESTEE when the requestor submits a SHIFT TIME TRADING request
    """
    trade_details = tradeDetails(self)
    message = f"Dear {self.requestee.user.name},\n{self.requestor.user.name} has sent you a Shift Time Trade Off Request.\n{trade_details}\n\n Please Visit the website to accept or decline the request."
    if settings.PRODUCTION_TYPE == "local":
        recipientList = [
            "alamin.neaz@genexinfosys.com",
        ]
    else:
        recipientList = [
            self.requestee.user.email,
        ]
    result = sendEmail(
        subject=subject,
        message=message,
        recipientList=recipientList,
        html_message=message,
    )


def requesteeApproves(self):
    """
    Send email to REQUESTOR and the SUPERVISORS of the requestor and requestee after the requestee approves of the SHIFT TIME TRADING
    """
    logging.info(
        "Trying to send email to requestor({requestor}) after requestee({requestee}) approval".format(
            requestor=self.requestor.user.email,
            requestee=self.requestee.user.email,
        )
    )
    #   Send Email notification to requestor after approved
    message = "Dear {requestorName},\n{requesteeName} has accepted your shift time trade off request. Your trade request is being forwared to the superviosors for further approval.\n".format(
        requesteeName=self.requestee.user.name, requestorName=self.requestor.user.name
    )
    if settings.PRODUCTION_TYPE == "local":
        recipientList = [
            "alamin.neaz@genexinfosys.com",
        ]
    else:
        recipientList = [
            self.requestor.user.email,
        ]
    result = sendEmail(subject=subject, message=message, recipientList=recipientList)
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
    message = "Dear {supervisorName},\n{requestorName} has sent shift time trade off request to {requesteeName}.\nRequestor Trade Details:\n\n\nPlease Visit the website to accept or decline the request.".format(
        requesteeName=self.requestee.user.name,
        requestorName=self.requestor.user.name,
        supervisorName=supervisor.user.name,
    )
    if settings.PRODUCTION_TYPE == "local":
        recipientList = ["alamin.neaz@genexinfosys.com"]
    else:
        recipientList = [supervisor.user.email]
    result = sendEmail(subject=subject, message=message, recipientList=recipientList)
    #   Requestee supervisors
    logging.info(
        "Trying to send email to requestee({requestee})  Supervisor({supervisor}) after requestee({requestee}) approval".format(
            supervisor=self.requestee.supervisor_1.user.email,
            requestee=self.requestee.user.email,
        )
    )
    supervisor = self.requestee.supervisor_1
    message = "Dear {supervisorName},\n{requestorName} has sent shift time trade off request to {requesteeName}.\nRequestor Trade Details:\n".format(
        requesteeName=self.requestee.user.name,
        requestorName=self.requestor.user.name,
        supervisorName=supervisor.user.name,
    )
    if settings.PRODUCTION_TYPE == "local":
        recipientList = ["alamin.neaz@genexinfosys.com"]
    else:
        recipientList = [supervisor.user.email]
    result = sendEmail(subject=subject, message=message, recipientList=recipientList)


def requesteeRejects(self):
    """
    Send email to REQUESTOR after the requestee rejects the SHIFT TIME TRADING
    """
    logging.info(
        "Trying to send email to requestor({requestor}) after requestee({requestee}) rejection".format(
            requestor=self.requestor.user.email,
            requestee=self.requestee.user.email,
        )
    )
    #   Send Email notification to requestor after rejected
    message = "Dear {requestorName},\n{requesteeName} has rejected your shift time trade off request.".format(
        requesteeName=self.requestee.user.name,
        requestorName=self.requestor.user.name,
    )

    if settings.PRODUCTION_TYPE == "local":
        recipientList = [
            "alamin.neaz@genexinfosys.com",
        ]
    else:
        recipientList = [
            self.requestor.user.email,
        ]
    result = sendEmail(subject=subject, message=message, recipientList=recipientList)


def supervisorApproves(self):
    """
    Send Email to REQUESTOR and REQUESTEE after SUPERVISOR approves the SHIFT TIME TRADING
    """
    logging.info(
        "Trying to send email to requestor({requestor}) and requestee({requestee}) after supervisor({supervisor}) approves".format(
            requestor=self.requestor.user.email,
            requestee=self.requestee.user.email,
            supervisor=self.supervisor.user.email,
        )
    )
    #   Send Email notification to requestor after approved
    message = (
        "The Shift Time Trade Request has been granted by {supervisorName}\n\nT".format(
            supervisorName=self.supervisor.user.name,
        )
    )
    if settings.PRODUCTION_TYPE == "local":
        recipientList = [
            "alamin.neaz@genexinfosys.com",
            "neazahmedneaz@gmail.com",
        ]
    else:
        recipientList = [
            self.requestor.user.email,
            self.requestee.user.email,
        ]
    result = sendEmail(subject=subject, message=message, recipientList=recipientList)


def supervisorDeclines(self):
    """
    Send Email to REQUESTOR and REQUESTEE after SUPERVISOR declines the SHIFT TIME TRADING
    """
    logging.info(
        "Trying to send email to requestor({requestor}) and requestee({requestee}) after supervisor({supervisor}) declined".format(
            requestor=self.requestor.user.email,
            requestee=self.requestee.user.email,
            supervisor=self.supervisor.user.email,
        )
    )
    #   Send Email notification to requestor after approved
    message = (
        "The Day Off trade Request has been rejected by {supervisorName}\n\nT".format(
            supervisorName=self.supervisor.user.name,
        )
    )
    if settings.PRODUCTION_TYPE == "local":
        recipientList = [
            "alamin.neaz@genexinfosys.com",
            "neazahmedneaz@gmail.com",
        ]
    else:
        recipientList = [
            self.requestor.user.email,
            self.requestee.user.email,
        ]
    result = sendEmail(subject=subject, message=message, recipientList=recipientList)
