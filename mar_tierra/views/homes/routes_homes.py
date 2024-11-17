from flask import (render_template, url_for, flash,
                   redirect, request, Blueprint)
from flask_login import current_user, login_required
from mar_tierra import db
from mar_tierra.models import Home, Product
from mar_tierra.views.homes.forms import NewHomeFom
from datetime import datetime

homes = Blueprint('homes', __name__)


@homes.route("/home/new", methods=['GET', 'POST'])
@login_required
def new_home():
    form = NewHomeFom(request.form)
    type_holder = None
    if form.desired_budget.data and form.desired_budget.data.isnumeric():
        type_holder = int(form.desired_budget.data)
    if form.validate_on_submit():
        type = "Petite Design" if type_holder < 200000 else "Fair Design" if 200000 <= type_holder < 300000 else "Luxury Design"
        home = Home(name=form.name.data,
                    target_date=form.target_date.data,
                    desired_budget=form.desired_budget.data,
                    author=current_user,
                    creator_email=current_user.email,
                    type=type)
        db.session.add(home)
        db.session.commit()

        flash('Your are one step closer to your new Home, thanks for taking the first step', 'success')
        if int(form.desired_budget.data) < 200000:
            return redirect(url_for('homes.home_design_petite'))
        elif 200000 <= int(form.desired_budget.data) < 300000:
            return redirect(url_for('homes.home_design_fair'))
        else:
            return redirect(url_for('homes.home_design_luxury'))
    return render_template('home/new_home.html', title='New home', form=form)


@homes.route("/home/new/petite_design", methods=['GET', 'POST'])
@login_required
def home_design_petite():
    homes_items = Home.query.filter(Home.author == current_user, Home.type == 'Petite Design').all()
    return render_template('home/new_home_petite_design.html', homes_items=homes_items)


@homes.route("/home/new/fair_design", methods=['GET', 'POST'])
@login_required
def home_design_fair():
    homes_items = Home.query.filter(Home.author == current_user, Home.type == 'Fair Design').all()
    return render_template('home/new_home_fair_design.html', homes_items=homes_items)


@homes.route("/home/new/luxury_design", methods=['GET', 'POST'])
@login_required
def home_design_luxury():
    homes_items = Home.query.filter(Home.author == current_user, Home.type == 'Luxury Design').all()
    return render_template('home/new_home_luxury_design.html', homes_items=homes_items)


####################### Home Actions #################################

@homes.route("/detail_home_project/<int:id>")
@login_required
def home_detail(id):
        home = Home.query.get_or_404(id)
        home_item = Home.query.filter_by(id=id).first()
        products = Product.query.filter_by(home_item_id=id).all()
        return render_template('home/home_detail.html', home=home, home_item=home_item,
                               products=products)


@homes.route("/update_home/update/<int:id>", methods=['GET', 'POST'])
@login_required
def update_home(id):
    home = Home.query.get_or_404(id)
    form = NewHomeFom(request.form)
    type_holder = None
    if form.desired_budget.data and form.desired_budget.data.isnumeric():
        type_holder = int(form.desired_budget.data)
    if form.validate_on_submit():
        home.name = form.name.data
        home.desired_budget = form.desired_budget.data
        home.target_date = form.target_date.data
        db.session.commit()

        flash('Your home project has been update Congrats', 'success')
        if int(form.desired_budget.data) < 200000:
            return redirect(url_for('homes.home_design_petite'))
        elif 200000 <= int(form.desired_budget.data) < 300000:
            return redirect(url_for('homes.home_design_fair'))
        else:
            return redirect(url_for('homes.home_design_luxury'))

    elif request.method == 'GET':
        form.name.data = home.name
        form.desired_budget.data = home.desired_budget
        form.target_date.data = home.target_date

    return render_template('home/new_home.html', title='New home', form=form)


@homes.route("/cancel_homeProject/<int:id>", methods=['GET', 'POST'])
@login_required
def cancel_home_project(id):
    home_item = Home.query.filter_by(id=id).first()
    if home_item:
        home_item.status = 'Cancel'
        home_item.date_closed = datetime.utcnow()
        db.session.commit()
        print(request.method)
        flash('Your Home Request has been Cancel, '
              'please let us know if you wish to contact to '
              'follow up with any requirement or regard', 'danger')
    else:
        flash('No home item found with the provided ID or it is not in Phase One status', 'warning')
    return redirect(url_for('users.account'))


@homes.route("/complete_home_request_from_User/<int:id>", methods=['GET', 'POST'])
@login_required
def complete_home_request(id):
    home_item = Home.query.filter_by(author=current_user, id=id).first()
    if home_item:
        home_item.status = 'Working on Quote'
        home_item.date_closed = datetime.utcnow()
        db.session.commit()
        flash('Your Home Request has been captured. Congrats, an agent will be working to contact you and present our quotation', 'success')
    else:
        flash('No home item found with the provided ID or it is not in Phase One status', 'warning')
    return redirect(url_for('users.account'))




