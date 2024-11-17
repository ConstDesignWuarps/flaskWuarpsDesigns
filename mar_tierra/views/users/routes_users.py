import os
from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required

from mar_tierra import db, bcrypt
from mar_tierra.models import User, Home, Visit
from mar_tierra.views.users.forms import RegistrationForm, LoginForm

users = Blueprint('users', __name__)
consent_yes = Blueprint('consent_yes', __name__)


users = Blueprint('users', __name__)
consent_yes = Blueprint('consent_yes', __name__)



@users.route("/registration", methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(email=form.email.data,
                    password=hashed_password)

        db.session.add(user)
        db.session.commit()
        flash('Your Account was created, Congrats!!!', 'success')
        return redirect(url_for('users.login'))
    return render_template('users/register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    ip_address = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    consent_given = request.form.get('consent_given')
    if consent_given is not None:
        consent_given = bool(int(consent_given))
    print(f"ip_address: {ip_address}, consent_given: {consent_given}")

    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            visit = Visit.query.filter_by(ip_address=ip_address).first()
            if visit:
                visit.visit_count += 1
                visit.user_id = user.id
                visit.user_email = user.email
            else:
                visit = Visit(ip_address=ip_address, visit_count=1, consent_given=True, user_id=user.id, user_email=user.email)
            db.session.add(visit)
            db.session.commit()
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('We do not have you register please Register in order to set your home', 'danger')
    return render_template('users/login.html', title='Login', form=form)



@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    homes = Home.query.filter_by(author=current_user).order_by(Home.creator_email.desc())
    create = db.session.query(Home.status).filter_by(author=current_user)

    homes_count = homes.count()  # count the number of home items
    return render_template('users/account.html',
                           title='Account',
                           homes=homes,
                           create=create,
                           homes_count=homes_count)


@users.route("/delete_user/<int:id>", methods=['POST'])
@login_required
def delete_user(id):
    try:
        delete_user = User.query.get_or_404(id)

        db.session.delete(delete_user)
        db.session.commit()
        flash('The User was deleted', 'danger')
        return redirect(url_for('admins.index'))

    except:
        flash('Cannot Delete User since it has a pending appointment, Delete All apointments to delete User', 'danger')
        return redirect(url_for('admins.index'))



@users.route("/user/<int:id>")
def user(id):
        user = User.query.get_or_404(id)

        return render_template('users/user.html', user=user)




###################### RESETS ####################################


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Un mail ha sido enviado con instrucciones para resetear tu cuenta', 'info')
        return redirect(url_for('users.login'))
    return render_template('users/reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Ese es un Token Invalido', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Tu Contraseña fue actualizada! Ya puede iniciar sesion', 'success')
        return redirect(url_for('users.login'))
        return render_template('users/reset_token.html', title='Reset Password', form=form)


###################### IP ####################################

@consent_yes.route('/consent_yes', methods=['POST'])
def handle_consent_yes():
    ip_address = request.form['ip_address']
    consent_given = bool(int(request.form['consent_given']))
    print(f"ip_address: {ip_address}, consent_given: {consent_given}")

    if consent_given:
        visit = Visit.query.filter_by(ip_address=ip_address).first()
        if visit:
            visit.visit_count += 1
        else:
            visit = Visit(ip_address=ip_address, visit_count=1, consent_given=True)
        db.session.add(visit)
        db.session.commit()
        print("Visit added to the database")

    return '', 204


#@socketio.on('message', namespace='/test')
#def handle_message(message):
#    print('received message: ' + message)
#    emit('message', message, broadcast=True, namespace='/test')


