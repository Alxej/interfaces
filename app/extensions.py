from flask_sqlalchemy import SQLAlchemy
from flask import Blueprint
from flask_restx import Api
from flask_migrate import Migrate
from flask_uploads import UploadSet, IMAGES
from flask_jwt_extended import JWTManager, current_user


db = SQLAlchemy()
migrate = Migrate()

api_bp = Blueprint("api", __name__, url_prefix="/api/")
api = Api(api_bp)

jwt = JWTManager()

images = UploadSet('images', IMAGES)

allowed = ["jpeg", "gif", "jpg", "png"]


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed


def admin_required(func):
    def wrapper(*args, **kwargs):
        if current_user.role.name != "admin":
            return {"error": "you don`t have permission for that"}, 403
        return func(*args, **kwargs)
    return wrapper


def manager_required(func):
    def wrapper(*args, **kwargs):
        if current_user.role.name == "guest":
            return {"error": "you don`t have permission for that"}, 403
        return func(*args, **kwargs)
    return wrapper
