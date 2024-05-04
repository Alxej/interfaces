from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
api = Api()

allowed = ["jpeg", "gif", "jpg", "png"]


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed
