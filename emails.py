import ssl, smtplib
from os import environ as env
from constants import constants
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

c = constants()

class email_sender:

    def __init__(self):
        self._context = ssl.create_default_context()
        self._server = smtplib.SMTP_SSL(c.SOURCE_EMAIL_HOST)

        self._server.login(c.SOURCE_EMAIL_ADDRESS, env.get("SOURCE_EMAIL_PASSWORD"))

    def send(self, email, content_html, content_text=""):
        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Confirmação de conta Pets.io"
        msg['From'] = c.SOURCE_EMAIL_ADDRESS
        msg['To'] = email

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(content_text, 'plain')
        part2 = MIMEText(content_html.encode('utf-8'), 'html', 'utf-8')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)
        self._server.sendmail(c.SOURCE_EMAIL_ADDRESS, email, msg.as_string())
