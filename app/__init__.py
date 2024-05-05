from flask import Flask  # render_template, flash, redirect, url_for, request
from flask_uploads import configure_uploads
# from app.forms import ProductCreationForm, CategoryCreationForm, BrandCreationForm # noqaE501

from .extensions import api, db, migrate, images
from .resources import ns, br, ca, im


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config["SECRET_KEY"] = 'jasd1khsjdk335ksfgsdvcbek54'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    app.config["UPLOADED_FILES_ALLOW"] = ["jpeg", "gif", "jpg", "png"]
    app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///site.db'
    app.config['UPLOADED_IMAGES_DEST'] = 'app/static/uploads/'
    configure_uploads(app, images)

    api.init_app(app)
    db.init_app(app)

    with app.app_context():
        if db.engine.url.drivername == 'sqlite':
            migrate.init_app(app, db, render_as_batch=True)
        else:
            migrate.init_app(app, db)

    api.add_namespace(ns)
    api.add_namespace(ca)
    api.add_namespace(br)
    api.add_namespace(im)

    return app
