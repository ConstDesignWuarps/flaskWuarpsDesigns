from datetime import datetime
from typing import Union
from flask import current_app
#from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin
from mar_tierra import db, login_manager


@login_manager.user_loader
def load_user(user_id: int) -> 'User':
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String, default='user')
    home_items = db.relationship('Home', backref='author', lazy=True)


    def __repr__(self) -> str:
        return f"{self.email}"


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phase = db.Column(db.String(100))
    description = db.Column(db.String(200))
    provider = db.Column(db.String(200))
    price = db.Column(db.Float)
    home_item_id = db.Column(db.Integer, db.ForeignKey('home_items.id'))

    # Renamed to avoid conflict
    related_home = db.relationship('Home', lazy=True)

    def __repr__(self):
        return f"ProductModel(id={self.id}, name='{self.name}', price={self.price})"





class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(100))
    category = db.Column(db.String(100))
    action = db.Column(db.String(100))
    description = db.Column(db.String(200))
    provider = db.Column(db.String(200))
    target_date = db.Column(db.Date, nullable=True)
    cost_estimate = db.Column(db.Float)
    actual_cost = db.Column(db.Float)

    home_item_id = db.Column(db.Integer, db.ForeignKey('home_items.id'))
    home_item = db.relationship('Home', backref='related_projects', lazy=True)  # Changed backref to 'related_projects'

    pictures = db.relationship('Picture', backref='project', lazy=True)

    def __repr__(self):
        return f"Home_Project(id={self.id}, status='{self.status}', category='{self.category}')"



class Picture(db.Model):
    __tablename__ = 'picture'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    image_path = db.Column(db.String(200))

    def __repr__(self):
        return f"Picture(id={self.id}, image_path='{self.image_path}')"


class Home(db.Model):
    """This class defines the homes table"""
    __tablename__ = 'home_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    creator_email = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(120), nullable=True, default='Draft Request')
    name = db.Column(db.String(120), nullable=True)
    desired_budget = db.Column(db.Float)
    target_date = db.Column(db.Date, nullable=True)
    type = db.Column(db.String(120), nullable=True)
    description = db.Column(db.String(120), nullable=True)

    estimated_Cost = db.Column(db.Float)
    consumption_rate = db.Column(db.Float)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_closed = db.Column(db.Date, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', foreign_keys=[user_id])
    products = db.relationship('Product', backref='home', lazy=True)  # No conflict here, backref is 'home'
    projects = db.relationship('Project', backref='project_item', lazy=True)

    def __repr__(self) -> str:
        return f"Home'{self.name}'"



class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(20), nullable=False)
    visit_count = db.Column(db.Integer, nullable=False, default=1)
    consent_given = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_email = db.Column(db.String(120), db.ForeignKey('user.email'))

    def __repr__(self):
        return f"Visit('{self.ip_address}', '{self.visit_count}', '{self.consent_given}', '{self.user_id}', '{self.user_email}')"
