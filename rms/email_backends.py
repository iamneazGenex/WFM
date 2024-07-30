from django.core.mail.backends.smtp import EmailBackend
from requests_ntlm import HttpNtlmAuth
import smtplib
from django.conf import settings
from base64 import b64encode
from email.mime.text import MIMEText
import logging

logger = logging.getLogger(__name__)


class NtlmEmailBackend(EmailBackend):
    def open(self):
        if self.connection:
            return False

        try:
            self.connection = smtplib.SMTP(self.host, self.port)
            self.connection.ehlo()
            if self.use_tls:
                self.connection.starttls()
                self.connection.ehlo()
            if self.username and self.password:
                domain = settings.EMAIL_DOMAIN  # Use your actual domain
                # auth_string = f"{self.username}:{self.password}"
                # auth = f"NTLM {b64encode(auth_string.encode()).decode()}"
                auth_string = f"{domain}\\{self.username}:{self.password}"
                auth = f"NTLM {b64encode(auth_string.encode()).decode()}"
                self.connection.docmd("AUTH", auth)
            return True
        except Exception as e:
            if not self.fail_silently:
                raise
            logger.error(f"Error opening connection: {e}")
            return False

    def send_messages(self, email_messages):
        # try:
        #     username = settings.EMAIL_HOST_USER
        #     password = settings.EMAIL_HOST_PASSWORD
        #     domain = "genexservices"

        #     smtp = smtplib.SMTP(settings.EMAIL_HOST, 25)
        #     smtp.starttls()

        #     # NTLM Authentication
        #     auth_string = f"{domain}\\{username}:{password}"
        #     auth = f"NTLM {b64encode(auth_string.encode()).decode()}"
        #     smtp.docmd("AUTH", auth)

        #     for message in email_messages:
        #         msg = MIMEText(message.body)
        #         msg["Subject"] = message.subject
        #         msg["From"] = message.from_email
        #         msg["To"] = ", ".join(message.to)
        #         smtp.sendmail(message.from_email, message.to, msg.as_string())

        #     smtp.quit()
        #     return len(email_messages)
        # except Exception as e:
        #     print(f"An error occurred while sending email: {e}")
        #     return 0
        if not self.open():
            logger.error("Failed to open SMTP connection")
            return 0
        sent_count = 0
        for message in email_messages:
            try:
                from_email = message.from_email
                to_emails = message.to
                body = message.body
                subject = message.subject
                msg = MIMEText(body)
                msg["Subject"] = subject
                msg["From"] = from_email
                msg["To"] = ", ".join(to_emails)
                self.connection.sendmail(from_email, to_emails, msg.as_string())
                logger.info(f"Successfully sent email to {', '.join(to_emails)}")
                sent_count += 1
            except Exception as e:
                if not self.fail_silently:
                    raise
                logger.error(f"Error sending message: {str(e)}")
        return sent_count
