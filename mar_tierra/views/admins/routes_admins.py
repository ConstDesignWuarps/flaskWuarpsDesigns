from flask import render_template, url_for, flash, redirect, Blueprint
from flask_login import login_required
from sqlalchemy import func
from mar_tierra import db
from mar_tierra.models import User, Home, Project
import requests
from bs4 import BeautifulSoup


admins = Blueprint('admins', __name__)


def search(keyword, zipcode):
    url = f"https://www.google.com/search?q={keyword}+in+zip+code+{zipcode}&num=10"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    result_div = soup.find_all('div', attrs={'class': 'g'})
    search_results = []
    for r in result_div:
        try:
            link = r.find('a', href=True)
            if link != '':
                header = r.find('h3').text
                search_results.append({'link': link['href'], 'header': header})
        except:
            continue
    return search_results


@admins.route("/admin", methods=['GET', 'POST'])
@login_required
def index():
    user_count = db.session.query(User.id).count()
    homes = Home.query.all()
    home_count = db.session.query(Home.id).count()

    cost_by_category = db.session.query(Project.category, func.sum(Project.cost_estimate)).group_by(Project.category).all()

    return render_template('admin/admin.html',
                           user_count=user_count,
                           homes=homes, home_count=home_count,
                           cost_by_category=cost_by_category)


#################### Need to work on the rest ####################

@admins.route("/move_to_incomplete/<id>", methods=['GET', 'POST'])
@login_required
def move_appointment_to_incomplete(id):
    appointment = Home.query.filter_by(id=int(id)).first()
    user = str(appointment.creator_email)
    print(user)
    appointment_date = str(appointment.home_date)
    body_1 = open('mar_tierra/Notifications/IncompleteAppointment.html').read()
    body_3 = open('mar_tierra/Notifications/Signature.html').read()
    body_1 = body_1.format(user, body_3)
    body = [body_1]

    ####################### Mail section end #######################

    appointment.status = "InCompleted"
    db.session.commit()

    flash('The Appoinment has been move to inComplete, an email to the user will be send!', 'warning')
    return redirect(url_for('admins.index'))



########################## Users ###############################

@admins.route("/admin/user_roles", methods=['GET', 'POST'])
@login_required
def user_roles():
    user_count = db.session.query(User.id).count()
    user = User.query.all()
    return render_template('admin/user_role.html',
                           user_count=user_count, user=user)


@admins.route("/admin/update_user_role/<int:id>", methods=['GET', 'POST'])
@login_required
def update_user_role_admin(id):
    user = User.query.filter_by(id=int(id)).first()
    user.role = "admin"
    db.session.commit()
    flash('The User was Update to Admin!', 'success')
    return redirect(url_for('admins.user_roles'))


@admins.route("/admin/update_user_role_backToAdmin/<int:id>", methods=['GET', 'POST'])
@login_required
def update_user_role_user(id):
    user = User.query.filter_by(id=int(id)).first()
    user.role = "user"
    db.session.commit()
    flash('The User was Update to User!', 'success')
    return redirect(url_for('admins.user_roles'))
