from flask import Flask  # render_template, flash, redirect, url_for, request
from flask_uploads import configure_uploads
# from app.forms import ProductCreationForm, CategoryCreationForm, BrandCreationForm # noqaE501

from .extensions import api, db, migrate, jwt, images
from .models import User
from .resources import ns, br, ca, im, us, o


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config["SECRET_KEY"] = 'jasd1khsjdk335ksfgsdvcbek54'
    app.config["JWT_SECRET_KEY"] = "234jii1ndbc132ubddscasd"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    app.config["UPLOADED_FILES_ALLOW"] = ["jpeg", "gif", "jpg", "png"]
    app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///site.db'
    app.config['UPLOADED_IMAGES_DEST'] = 'app/static/uploads/'
    configure_uploads(app, images)

    api.init_app(app)
    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        if db.engine.url.drivername == 'sqlite':
            migrate.init_app(app, db, render_as_batch=True)
        else:
            migrate.init_app(app, db)

    api.add_namespace(ns)
    api.add_namespace(ca)
    api.add_namespace(br)
    api.add_namespace(im)
    api.add_namespace(us)
    api.add_namespace(o)

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user.id

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.filter(User.id == identity).first()

    return app
