from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api
from flask_migrate import Migrate
from flask_uploads import UploadSet, IMAGES

db = SQLAlchemy()
migrate = Migrate()
api = Api()

images = UploadSet('images', IMAGES)

allowed = ["jpeg", "gif", "jpg", "png"]


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed
