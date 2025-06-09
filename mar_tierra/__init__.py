import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from mar_tierra.config import Config
from flask_bcrypt import Bcrypt
from flask_cors import CORS

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions with the app instance
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Import blueprints and register them with the app
    from mar_tierra.views.main.routes_main import main
    from mar_tierra.views.users.routes_users import users
    from mar_tierra.views.admins.routes_admins import admins
    from mar_tierra.views.projects.routes_projects import projects
    from mar_tierra.views.homes.routes_homes import homes
    from mar_tierra.views.products.routes_products import products

    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(admins)
    app.register_blueprint(projects)
    app.register_blueprint(homes)
    app.register_blueprint(products)

    CORS(app)

    return app
