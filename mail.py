#!/usr/bin/env python3

import email.message
import mimetypes
import os.path
from smtplib import SMTP_SSL
from smtplib import SMTPAuthenticationError
import ssl
from decouple import config  # pip3 install python-decouple


SENDER = config('SDR')
RECEIVER = config('RVR')
SERVER = config('SRV')
PORT = config('PORT')
NAME = config('NAME')
KWD = config('KWD')


def generate(subject, body, attachment_path):
    """Creates an email with an attachement."""
    # Basic Email formatting
    message = email.message.EmailMessage()
    message["From"] = SENDER
    message["To"] = RECEIVER
    message["Subject"] = subject
    message.set_content(body)

    # Process the attachment and add it to the email
    attachment = os.path.basename(attachment_path)
    mime_type, _ = mimetypes.guess_type(attachment_path)
    mime_type, mime_subtype = mime_type.split('/', 1)

    with open(attachment_path, 'rb') as ap:
        message.add_attachment(ap.read(),
                            maintype=mime_type,
                            subtype=mime_subtype,
                            filename=attachment)
    return message


def send(msg):
    """Sends the message to the configured SMTP server."""
    ssl_context = ssl.create_default_context()
    mail_server = SMTP_SSL(SERVER, port=PORT, context=ssl_context)

    try:
        mail_server.login(SENDER, KWD)
    except SMTPAuthenticationError:
        print("Fail to ligin SMTP server")

    mail_server.send_message(msg)
    print('A message sent to', RECEIVER)
    mail_server.quit()
