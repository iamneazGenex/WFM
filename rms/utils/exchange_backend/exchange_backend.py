from django.core.mail.backends.base import BaseEmailBackend
from exchangelib import Credentials, Account, Message, Mailbox, Configuration, DELEGATE
from django.conf import settings


class ExchangeEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        credentials = Credentials(
            username=settings.EXCHANGE_USERNAME, password=settings.EXCHANGE_PASSWORD
        )
        config = Configuration(server=settings.EXCHANGE_SERVER, credentials=credentials)
        account = Account(
            primary_smtp_address=settings.EXCHANGE_EMAIL,
            config=config,
            autodiscover=False,
            access_type=DELEGATE,
        )

        for email_message in email_messages:
            msg = Message(
                account=account,
                subject=email_message.subject,
                body=email_message.body,
                to_recipients=[Mailbox(email=to) for to in email_message.to],
            )
            msg.send()

        return len(email_messages)
