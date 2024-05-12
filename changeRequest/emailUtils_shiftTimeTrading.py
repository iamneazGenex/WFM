import logging
from .utils import *

logger = logging.getLogger(__name__)

subject = "[RMS] Shift Time Trading Request"


def isCreated(self):
    """
    Send Email to REQUESTEE when the requestor submits a SHIFT TIME TRADING request
    """
    message = "Dear {requesteeName},\n{requestorName} has sent you a Shift Time Trade Off Request.\nYour Trade Details:\nDate:{date}\n:Start Time From {requesteeStartTime} To {requestorStartTime}\nEnd Time From {requesteeEndTime} To {requestorEndTime}\n\n Please Visit the website to accept or decline the request.".format(
        requesteeName=self.requestee.user.name,
        requestorName=self.requestor.user.name,
        date=self.requestee_swap_roster.start_date,
        requestorStartTime=self.requestor_start_time,
        requestorEndTime=self.requestor_end_time,
        requesteeStartTime=self.requestee_start_time,
        requesteeEndTime=self.requestee_end_time,
    )
    # recipientList = [
    #     self.requestee.user.email,
    # ]
    recipientList = [
        "alamin.neaz@genexinfosys.com",
    ]
    result = sendEmail(subject=subject, message=message, recipientList=recipientList)


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
    message = "Dear {requestorName},\n{requesteeName} has accepted your day trade off request. Your trade request is being forwared to the superviosors for further approval.\n".format(
        requesteeName=self.requestee.user.name, requestorName=self.requestor.user.name
    )
    # recipientList = [
    #     self.requestor.user.email,
    # ]
    recipientList = [
        "alamin.neaz@genexinfosys.com",
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
    message = "Dear {supervisorName},\n{requestorName} has sent day trade off request to {requesteeName}.\nRequestor Trade Details:\n\n\nPlease Visit the website to accept or decline the request.".format(
        requesteeName=self.requestee.user.name,
        requestorName=self.requestor.user.name,
        supervisorName=supervisor.user.name,
    )
    # recipientList = [
    #     supervisor.user.email,
    # ]
    recipientList = [
        "alamin.neaz@genexinfosys.com",
    ]
    result = sendEmail(subject=subject, message=message, recipientList=recipientList)
    #   Requestee supervisors
    logging.info(
        "Trying to send email to requestee({requestee})  Supervisor({supervisor}) after requestee({requestee}) approval".format(
            supervisor=self.requestee.supervisor_1.user.email,
            requestee=self.requestee.user.email,
        )
    )
    supervisor = self.requestee.supervisor_1
    message = "Dear {supervisorName},\n{requestorName} has sent day trade off request to {requesteeName}.\nRequestor Trade Details:\n".format(
        requesteeName=self.requestee.user.name,
        requestorName=self.requestor.user.name,
        supervisorName=supervisor.user.name,
    )
    # recipientList = [
    #     supervisor.user.email,
    # ]
    recipientList = [
        "alamin.neaz@genexinfosys.com",
    ]
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
    # recipientList = [
    #     self.requestor.user.email,
    #     self.requestee.user.email,
    # ]
    recipientList = ["alamin.neaz@genexinfosys.com", "neazahmedneaz@gmail.com"]
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
    # recipientList = [
    #     self.requestor.user.email,
    #     self.requestee.user.email,
    # ]
    recipientList = ["alamin.neaz@genexinfosys.com", "neazahmedneaz@gmail.com"]
    result = sendEmail(subject=subject, message=message, recipientList=recipientList)
