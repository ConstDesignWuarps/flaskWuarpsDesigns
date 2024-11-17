#%%libraries

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import formatdate
from email import encoders
import random
import time
import os
#%% functions

# function to generate a message id
def generate_message_id(msg_from):
    domain = msg_from.split("@")[1]
    r = "%s.%s" % (time.time(), random.randint(0, 100))
    mid = "<%s@%s>" % (r, domain)
    return mid

def send_mail_html_cc(msg_from, to, cc, subject, text, files, picture=None, debug=False):
    msg = MIMEMultipart()
    msg['From'] = msg_from
    msg['To'] = to
    msg['Cc'] = cc
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject


    for i in text:
        texto = MIMEText(i, 'html')
        msg.attach(texto)

    msg.add_header('Message-ID', generate_message_id(msg_from))


    # recipients
    rec = [to] + cc.split(',')

    if not debug:
        server = smtplib.SMTP('northrelay.us.ibm.com', 25)
        server.starttls()
        text = msg.as_string()
        server.sendmail(msg_from, rec, text)
        server.close()

    return msg
