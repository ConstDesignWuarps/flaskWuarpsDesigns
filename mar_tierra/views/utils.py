import os
import secrets
import subprocess
from datetime import datetime

from PIL import Image
from flask import request
from flask_login import current_user
from mar_tierra import app_root
from mar_tierra.views.homes.forms import NewHomeFom
from mar_tierra.views.functions import send_mail_html_cc


# SEND AUTOMATION EMAIL - Standard - Functions
def send_confimation_email():
    form = NewHomeFom(request.form)
    appointment_date = form.appointment_date.data
    appointment_hour = form.appointment_hour.data
    Description = "New Devices"
    user = str(current_user)

    body_1 = open('mar_tierra/Notifications/confirmation_email.html').read()
    body_3 = open('mar_tierra/Notifications/Signature.html').read()
    body_1 = body_1.format(user, appointment_date, appointment_hour, Description, body_3)

    body = [body_1]

    send_mail_html_cc(msg_from='NonReply@ibm.com',
                      to=user,
                      cc="ferjg@ibm.com",
                      subject='Devices Operations home Confirmation',
                      text=body,
                      picture='mar_tierra/views/imageDevices.png',
                      files=[],
                      debug=False)

def return_device_send_confimation_email():
    form = AppointmentForm(request.form)
    appointment_date = form.appointment_date.data
    appointment_hour = form.appointment_hour.data
    Description = "Return Device"
    user = str(current_user)

    body_1 = open('mar_tierra/Notifications/return_confirmation_email.html').read()
    body_3 = open('mar_tierra/Notifications/Signature.html').read()
    body_1 = body_1.format(user, appointment_date, appointment_hour, Description, body_3)

    body = [body_1]

    send_mail_html_cc(msg_from='NonReply@ibm.com',
                      to=user,
                      cc="ferjg@ibm.com",
                      subject='Devices Operations home Confirmation',
                      text=body,
                      picture='mar_tierra/views/imageDevices.png',
                      files=[],
                      debug=False)



def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app_root, 'static/photos/', picture_fn)

    output_size = (3024, 4032)
    i = Image.open(form_picture)
    rgb_i = i.convert('RGB')
    rgb_i.thumbnail(output_size)
    rgb_i.save(picture_path)

    return picture_fn


def upload_image(form_picture):
    target = os.path.join(app_root, 'photos/')
    print(target)

    if not os.path.isdir(target):
        os.mkdir(target)

    for file in request.files.getlist("file"):
        print(file)
        filename = file.filename
        destination = "/".join([target, filename])
        print(destination)
        file.save(destination)
