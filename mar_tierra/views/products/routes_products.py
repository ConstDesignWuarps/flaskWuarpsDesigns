from flask import (render_template, url_for, flash,
                   redirect, request, Blueprint)
from flask_login import current_user, login_required
from mar_tierra import db
from mar_tierra.models import Home, Product
from mar_tierra.views.products.forms import NewProductFom
from datetime import datetime

products = Blueprint('products', __name__)


@products.route("/product/new", methods=['GET', 'POST'])
@login_required
def new_product():
    form = NewProductFom(request.form)
    current_home_id = request.args.get('home_item')
    if form.validate_on_submit():
        product = Product(name=form.name.data,
                          description=form.description.data,
                          price=form.target_cost_estimate.data,
                          home_item_id=current_home_id)
        db.session.add(product)
        db.session.commit()
        flash('Amazing selections moving to our next phase', 'success')
        return redirect(url_for('products.product_detail', id=current_home_id))
    return render_template('product/new_product.html', title='New Product', form=form)


@products.route("/detail_home_project/<int:id>")
@login_required
def product_detail(id):
        home = Home.query.get_or_404(id)
        return render_template('home/home_detail.html', home=home)


@products.route("/cancel_Product/<int:id>", methods=['GET', 'POST'])
@login_required
def cancel_product(id):
    product_item = Product.query.get_or_404(id)
    product_item.phase = 'Cancel'
    db.session.commit()

    current_home_id = product_item.home_item_id
    flash('The Product was canceled', 'danger')
    return redirect(url_for('users.account', id=current_home_id))




@products.route("/update_product/update/<int:id>", methods=['GET', 'POST'])
@login_required
def update_product_item(id):
    product_item = Product.query.get_or_404(id)
    #current_home_id = request.args.get('id')
    current_home_id = product_item.home_item_id
    form = NewProductFom(request.form)

    if form.validate_on_submit():
        product_item.name = form.name.data
        product_item.description = form.description.data
        product_item.price = form.target_cost_estimate.data
        db.session.commit()

        flash('Your home project has been update Congrats', 'success')
        return redirect(url_for('homes.home_detail', id=current_home_id))

    elif request.method == 'GET':
        form.name.data = product_item.name
        form.description.data = product_item.description
        form.target_cost_estimate.data = product_item.price

    return render_template('product/new_product.html', title='Update product', form=form,
                           product_item=product_item)


