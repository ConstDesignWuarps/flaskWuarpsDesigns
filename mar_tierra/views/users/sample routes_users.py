import os
from google.cloud import storage  # Import Google Cloud Storage client
import sqlite3
from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from mar_tierra import db, bcrypt
from mar_tierra.models import User, Home, Visit
from mar_tierra.views.users.forms import RegistrationForm, LoginForm

# Add this line to set the environment variable for the service account key
json_credentials_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'service-account-key.json')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = json_credentials_path

users = Blueprint('users', __name__)
consent_yes = Blueprint('consent_yes', __name__)


users = Blueprint('users', __name__)
consent_yes = Blueprint('consent_yes', __name__)


# Function to download the SQLite .db file from Google Cloud Storage
def download_db_from_gcs(bucket_name, source_blob_name, destination_file_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    # Download the .db file from the bucket to the local file system
    blob.download_to_filename(destination_file_name)
    print(f"Downloaded {source_blob_name} to {destination_file_name}.")


@users.route("/registration", methods=['GET', 'POST'])
def registration():
    # Download the database file before using it
    bucket_name = 'wuarps_design'  # Replace with your bucket name
    source_blob_name = 'wuarps_designs_objectStorage/mar_tierra.db'  # Replace with the .db file name in your bucket
    destination_file_name = os.path.join(os.path.dirname(__file__), 'mar_tierra.db')

    # Download the database from GCS
    download_db_from_gcs(bucket_name, source_blob_name, destination_file_name)

    # Now, connect to the downloaded SQLite database
    conn = sqlite3.connect(destination_file_name)
    cursor = conn.cursor()

    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Hash the password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        # Insert the new user into the database
        cursor.execute("""
            INSERT INTO user (email, password) VALUES (?, ?)
        """, (form.email.data, hashed_password))

        conn.commit()
        conn.close()  # Close the SQLite connection after committing

        flash('Your Account was created, Congrats!!!', 'success')
        return redirect(url_for('users.login'))

    return render_template('users/register.html', title='Register', form=form)



@users.route("/login", methods=['GET', 'POST'])
def login():
    # Download the database file before using it
    bucket_name = 'wuarps_design'  # Replace with your bucket name
    source_blob_name = 'wuarps_designs_objectStorage/mar_tierra.db'  # Replace with the .db file name in your bucket
    destination_file_name = os.path.join(os.path.dirname(__file__), 'mar_tierra.db')

    download_db_from_gcs(bucket_name, source_blob_name, destination_file_name)

    # Now, connect to the downloaded SQLite database
    conn = sqlite3.connect(destination_file_name)
    cursor = conn.cursor()

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
                visit = Visit(ip_address=ip_address, visit_count=1, consent_given=True, user_id=user.id,
                              user_email=user.email)
            db.session.add(visit)
            db.session.commit()
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('We do not have you registered, please Register to set your home', 'danger')

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


