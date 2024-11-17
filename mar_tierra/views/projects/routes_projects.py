import urllib

from flask import render_template, url_for, flash, redirect, Blueprint, request, session, jsonify
from flask_login import current_user, login_required
from sqlalchemy import func
from mar_tierra import db
from mar_tierra.models import User, Home, Project

from mar_tierra.views.admins.forms import NewHome_Project_Form
from bs4 import BeautifulSoup
import requests
import urllib.parse

from mar_tierra.views.projects.forms import UpdateHome_Project_Form

projects = Blueprint('projects', __name__)


def search(keyword, zipcode):
    search_query = f"{keyword} in zip code {zipcode}"
    url = f"https://www.google.com/search?q={urllib.parse.quote_plus(search_query)}&num=7"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    search_results = []

    # Find all the search result items
    result_items = soup.find_all('a', href=True)

    # Iterate over each search result item
    for item in result_items:
        # Extract the link
        link = item['href']
        if link.startswith('/url?q='):
            # Extract the main name from the URL
            start_index = link.find("www.") + 4
            end_index = link.find(".com", start_index)

            # Skip if main_name is not found after "www." or if ".com" is not found
            if start_index < 4 or end_index == -1:
                continue

            main_name = link[start_index:end_index + 4]

            # Remove everything after ".com" in the link
            link = link[7:end_index + 4]

            # Create a dictionary to store the link and main name
            result_data = {
                'link': link,
                'main_name': main_name
            }

            # Append the result to the list
            search_results.append(result_data)

            # Break the loop if the desired number of results is reached
            if len(search_results) >= 7:
                break

    return search_results


@projects.route("/home_project_item/new", methods=['GET', 'POST'])
@login_required
def new_item_to_admin_project():
    form = NewHome_Project_Form(request.form)
    current_home_id = request.args.get('home_item')

    if request.method == 'POST' and request.form.get('submit') == 'search':
        # Handle search request
        keyword = request.form['keyword']
        print(keyword)
        zipcode = request.form['zipcode']
        print(zipcode)
        results = search(keyword, zipcode)
        print(results)
        return render_template('project/new_project_item.html', title='New Product', form=form,
                           current_home_id=current_home_id, id=current_home_id, results=results)

    elif request.method == 'POST' and request.form.get('submit') == 'submit':
        # Handle form submission
        if form.validate_on_submit():
            project_item = Project(
                category=form.category.data,
                action=form.action.data,
                description=form.description.data,
                provider=form.provider.data,
                target_date=form.target_date.data,
                cost_estimate=form.cost_estimate.data,
                actual_cost=form.actual_cost.data,
                home_item_id=current_home_id)

            db.session.add(project_item)
            db.session.commit()
            flash('Amazing selections moving to our next phase', 'success')
            return redirect(url_for('projects.project_detail', id=current_home_id))
        else:
            # Form validation failed, render the form again with error messages
            return render_template('project/new_project_item.html', title='New Product', form=form,
                               current_home_id=current_home_id, id=current_home_id)

    # Render the form if no POST request has been made yet
    return render_template('project/new_project_item.html', title='New Product', form=form,
                       current_home_id=current_home_id, id=current_home_id)



@projects.route("/product/<int:productid>/update", methods=['GET', 'POST'])
@login_required
def update_product(productid):
    product = Product.query.get_or_404(productid)
    form = UpdateProduct()
    form.category_id.choices = [(row.id, row.category_name) for row in Category.query.all()]
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            product.image_file = picture_file

            picture_file_2 = save_picture(form.picture2.data)
            product.image_file_2 = picture_file_2

            picture_file_3 = save_picture(form.picture3.data)
            product.image_file_3 = picture_file_3

        product.product_name = form.productName.data
        product.description = form.productDescription.data
        product.price = form.productPrice.data


        db.session.commit()

        flash('Su Producto fue Actualizado!', 'success')
        return redirect(url_for('admins.index', productid=productid))

    elif request.method == 'GET':
            form.productName.data = product.product_name
            form.productDescription.data = product.description
            form.productPrice.data = product.price


    image_file = url_for('static', filename='photos/' + current_user.image_file)
    return render_template('product/update_product.html', legend="Update Product", form=form,
                           image_file=image_file, product=product)


@projects.route("/home_project/<int:id>", methods=['GET', 'POST'])
@login_required
def project_detail(id):
    home = Home.query.get_or_404(id)
    home_item = Home.query.filter_by(id=id).first()
    # get existing Home project items
    project_items = Project.query.filter_by(home_item_id=id).all()
    total_cost_estimate = db.session.query(func.sum(Project.cost_estimate)).\
        filter_by(home_item_id=id).scalar() or 0
    actual_cost = db.session.query(func.sum(Project.actual_cost)). \
                              filter_by(home_item_id=id).scalar() or 0

    cost_by_category = db.session.query(Project.category, func.sum(Project.cost_estimate)). \
        filter_by(home_item_id=id).group_by(Project.category).all()

    return render_template('project/project.html',
                           home_item=home_item,
                           home=home,
                           project_items=project_items,
                           total_cost_estimate=total_cost_estimate,
                           actual_cost=actual_cost,
                           cost_by_category=cost_by_category)

#################### Actions ####################


@projects.route("/update_project/update/<int:id>", methods=['GET', 'POST'])
@login_required
def update_project_item(id):
    project_item = Project.query.get_or_404(id)
    current_home_id = project_item.home_item_id
    form = UpdateHome_Project_Form(request.form)

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            product.image_file = picture_file


        project_item.category = form.category.data
        project_item.action = form.action.data
        project_item.description = form.description.data
        project_item.provider = form.provider.data
        project_item.target_date = form.target_date.data
        project_item.cost_estimate = form.cost_estimate.data
        project_item.actual_cost = form.actual_cost.data
        db.session.commit()

        flash('Your home project has been updated!', 'success')
        return redirect(url_for('projects.project_detail', id=current_home_id))

    elif request.method == 'GET':
        form.category.data = project_item.category
        form.action.data = project_item.action
        form.description.data = project_item.description
        form.provider.data = project_item.provider
        form.target_date.data = project_item.target_date
        form.cost_estimate.data = project_item.cost_estimate
        form.actual_cost.data = project_item.actual_cost

    return render_template('project/update_project_item.html', title='Update Home Project',
                           form=form, current_home_id=current_home_id, id=id)



@projects.route("/project_item_delete/<int:id>", methods=['GET','POST'])
@login_required
def delete_project_item(id):
    delete_project_item = Project.query.get_or_404(id)
    current_home_id = delete_project_item.home_item_id  # assuming home_item is a relationship
    db.session.delete(delete_project_item)
    db.session.commit()
    flash('The Project Item was deleted', 'danger')
    return redirect(url_for('projects.project_detail', id=current_home_id))


