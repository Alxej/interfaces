from flask_restx import Resource, Namespace, reqparse
from flask import url_for
from flask_jwt_extended import (jwt_required,
                                current_user,
                                create_access_token)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

import werkzeug
import os

from .extensions import (db,
                         allowed_file,
                         images,
                         admin_required,
                         manager_required)
from .api_models import (
    category_model, 
    category_input_model, 
    brand_model, 
    brand_input_model, 
    image_model, 
    product_model, 
    product_input_model,
    role_model,
    register_model,
    user_model,
    login_model)
from .models import Category, Brand, Product, Image, User, Role


pagination_parser = reqparse.RequestParser()
pagination_parser.add_argument(
    "page",
    type=int,
    required=False,
    default=1,
    help="Page number"
)
pagination_parser.add_argument(
    "per_page",
    type=int,
    required=False,
    choices=[1, 2, 3, 5, 10, 15, 20],
    default=3,
    help="Page size"
)

image_parser = reqparse.RequestParser()
image_parser.add_argument('file',
                          type=werkzeug.datastructures.FileStorage,
                          location='files',
                          required=True,
                          help='provide a file')
image_parser.add_argument('product_id',
                          type=int,
                          location='form',
                          required=True,
                          help='select product id')

authorizations = {
    "jsonWebToken": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization"
    }
}

ns = Namespace("ProductApi", authorizations=authorizations)
ca = Namespace("CategoriesApi")
im = Namespace("ImagesApi")
br = Namespace("BrandsApi")
us = Namespace("UserApi")


@ns.route("/products")
class ProductListAPI(Resource):
    method_decorators = [jwt_required()]

    @ns.errorhandler(Exception)
    def handle_value_error_exception(exception):
        return {"error": str(exception)}, 400

    @ns.doc(security="jsonWebToken")
    @admin_required
    @ns.expect(pagination_parser)
    @ns.marshal_list_with(product_model)
    def get(self):
        p_args = pagination_parser.parse_args()
        page = p_args.get("page")
        per_page = p_args.get("per_page")
        products = Product.query.paginate(page=page, per_page=per_page)
        return products.items, 201

    @ns.doc(security="jsonWebToken")
    @manager_required
    @ns.expect(product_input_model)
    @ns.marshal_with(product_model)
    def post(self):
        product = Product(name=ns.payload["name"],
                          product_description=ns.payload["description"],
                          price=ns.payload["price"],
                          brand_id=ns.payload["brand_id"],
                          category_id=ns.payload["category_id"])
        if not Brand.query.get(ns.payload["brand_id"]):
            raise ValueError("brand with that id is not exist")
        if not Category.query.get(ns.payload["category_id"]):
            raise ValueError("category with that id is not exist")
        db.session.add(product)
        db.session.flush()
        db.session.commit()
        return product, 201


@ns.route("/products/<int:id>")
class ProductAPI(Resource):
    @ns.errorhandler(Exception)
    def handle_value_error_exception(exception):
        return {"error": str(exception)}, 400

    @ns.doc(security="jsonWebToken")
    @admin_required
    @ns.marshal_with(product_model)
    def get(self, id):
        if current_user.name != "admin":
            return {"error": "you don`t have permission for that action"}, 403
        product = Product.query.get(id)
        if not product:
            raise ValueError("no product with that id")
        return product

    @ns.doc(security="jsonWebToken")
    @ns.expect(product_input_model)
    @manager_required
    @ns.marshal_with(product_model)
    def put(self, id):
        product = Product.query.get(id)
        if not product:
            raise ValueError("no product with that id")
        if not Brand.query.get(ns.payload["brand_id"]):
            raise ValueError("brand with that id is not exist")
        if not Category.query.get(ns.payload["category_id"]):
            raise ValueError("category with that id is not exist")
        product.name = ns.payload["name"]
        product.product_description = ns.payload["description"]
        product.price = ns.payload["price"]
        product.brand_id = ns.payload["brand_id"]
        product.category_id = ns.payload["category_id"]
        db.session.commit()
        return product, 201

    @ns.doc(security="jsonWebToken")
    @manager_required
    def delete(self, id):
        product = Product.query.get(id)
        if not product:
            raise ValueError("no product with that id")
        product_images = product.images
        for image in product_images:
            try:
                os.remove(os.getcwd().replace('\\', '/') + "/app" +
                          url_for('static', filename=f'uploads/{image.image_name}')) # noqa E501
            except Exception:
                print("file is already deleted")
            db.session.delete(image)
            db.session.flush()
        db.session.delete(product)
        db.session.commit()
        return {"message": "product deleted"}, 204


@im.route("/images")
class ImageListAPI(Resource):
    @im.doc(security="jsonWebToken")
    @admin_required
    @im.marshal_list_with(image_model)
    def get(self):
        return Image.query.all()

    @im.doc(security="jsonWebToken")
    @manager_required
    @im.expect(image_parser)
    @im.marshal_with(image_model)
    def post(self):
        args = image_parser.parse_args()
        product = Product.query.get(args['product_id'])
        if not product:
            raise ValueError("no product with that id")

        image = args['file']
        if image and allowed_file(image.filename):
            filename = images.save(image)
            image_to_add = Image(product_id=product.id,
                                 image_name=filename)
            db.session.add(image_to_add)
            db.session.commit()
            return image_to_add, 201
        else:
            raise ValueError("image is not allowed")


@im.route("/images/<int:id>")
class ImageAPI(Resource):
    @im.doc(security="jsonWebToken")
    @admin_required
    @im.marshal_with(image_model)
    def get(self, id):
        image = Image.query.get(id)
        if not image:
            raise ValueError("there is no image with that id")
        return Image.query.get(id), 201

    @im.doc(security="jsonWebToken")
    @manager_required
    @im.expect(image_parser)
    @im.marshal_with(image_model)
    def put(self, id):
        image = Image.query.get(id)
        if not image:
            raise ValueError("there is no image with that id")
        image_to_delete = image.image_name
        args = image_parser.parse_args()
        product = Product.query.get(args['product_id'])
        if not product:
            raise ValueError("no product with that id")

        image_to_upload = args['file']
        if image_to_upload and allowed_file(image_to_upload.filename):
            filename = secure_filename(image_to_upload.filename)
            image_to_upload.save(os.path.join('app/static/uploads/',
                                              filename))
            image.image_name = filename
            image.product_id = args['product_id']
            db.session.commit()
            os.remove(os.getcwd().replace('\\', '/') + "/app" +
                      url_for('static', filename=f'uploads/{image_to_delete}'))
            return image, 201
        else:
            raise ValueError("image is not allowed")

    @im.doc(security="jsonWebToken")
    @manager_required
    def delete(self, id):
        image = Image.query.get(id)
        if not image:
            raise ValueError("there is no image with that id")
        os.remove(os.getcwd().replace('\\', '/') + "/app" +
                  url_for('static', filename=f'uploads/{image.image_name}'))
        db.session.delete(image)
        db.session.commit()
        return {"message": f"image {id} deleted"}, 204


@br.route("/brands")
class BrandListAPI(Resource):
    @br.errorhandler(Exception)
    def handle_value_error_exception(exception):
        return {"error": str(exception)}, 400

    @br.doc(security="jsonWebToken")
    @admin_required
    @br.marshal_list_with(brand_model)
    def get(self):
        return Brand.query.all()

    @br.doc(security="jsonWebToken")
    @manager_required
    @br.expect(brand_input_model)
    @br.marshal_list_with(brand_model)
    def post(self):
        brand = Brand(brand_name=br.payload["brand_name"])
        try:
            db.session.add(brand)
            db.session.flush()
            db.session.commit()
            return brand, 201
        except Exception:
            return {}, 408


@br.route("/brands/<int:id>")
class BrandApi(Resource):
    @br.errorhandler(Exception)
    def handle_value_error_exception(exception):
        return {"error": str(exception)}, 400

    @br.doc(security="jsonWebToken")
    @admin_required
    @br.marshal_with(brand_model)
    def get(self, id):
        brand = Brand.query.get(id)
        if not brand:
            raise ValueError("brand with that id is not exist")
        return brand, 201

    @br.doc(security="jsonWebToken")
    @manager_required
    @br.expect(brand_input_model)
    @br.marshal_with(brand_model)
    def put(self, id):
        brand = Brand.query.get(id)
        if not brand:
            raise ValueError("brand with that id is not exist")
        brand.brand_name = br.payload["brand_name"]
        db.session.commit()
        return brand, 201

    @br.doc(security="jsonWebToken")
    @manager_required
    def delete(self, id):
        brand = Brand.query.get(id)
        if not brand:
            raise ValueError("brand with that id is not exist")
        db.session.delete(brand)
        db.session.commit()
        return {}, 204


@ca.route("/categories")
class CategoryListAPI(Resource):
    @ca.errorhandler(Exception)
    def handle_value_error_exception(exception):
        return {"error": str(exception)}, 400

    @ca.doc(security="jsonWebToken")
    @admin_required
    @ca.marshal_list_with(category_model)
    def get(self):
        return Category.query.all()

    @ca.doc(security="jsonWebToken")
    @manager_required
    @ca.expect(category_input_model)
    @ca.marshal_list_with(category_model)
    def post(self):
        category = Category(category_name=ca.payload["category_name"])
        try:
            db.session.add(category)
            db.session.flush()
            db.session.commit()
            return category, 201
        except Exception:
            return {}, 408


@ca.route("/categories/<int:id>")
class CategoryApi(Resource):
    @ca.errorhandler(Exception)
    def handle_value_error_exception(exception):
        return {"error": str(exception)}, 400

    @ca.doc(security="jsonWebToken")
    @admin_required
    @ca.marshal_with(category_model)
    def get(self, id):
        category = Category.query.get(id)
        if not category:
            raise ValueError("category with that id is not exist")
        return category, 201

    @ca.doc(security="jsonWebToken")
    @manager_required
    @ca.expect(category_input_model)
    @ca.marshal_with(category_model)
    def put(self, id):
        category = Category.query.get(id)
        if not category:
            raise ValueError("category with that id is not exist")
        category.category_name = ca.payload["category_name"]
        db.session.commit()
        return category, 201

    @ca.doc(security="jsonWebToken")
    @manager_required
    def delete(self, id):
        category = Category.query.get(id)
        if not category:
            raise ValueError("category with that id is not exist")
        db.session.delete(category)
        db.session.commit()
        return {}, 204


@us.route("/users")
class UserList(Resource):
    @us.doc(security="jsonWebToken")
    @admin_required
    @us.marshal_list_with(user_model)
    def get(self):
        users = User.query.all()
        return users, 201


@us.route("/roles")
class RoleListApi(Resource):
    @us.doc(security="jsonWebToken")
    @admin_required
    @us.marshal_list_with(role_model)
    def get(self):
        roles = Role.query.all()
        return roles, 201


@us.route("/register")
class RegisterApi(Resource):
    @us.expect(register_model)
    @us.marshal_with(user_model)
    def post(self):
        role = Role.query.filter(Role.name == us.payload["role"]).first()
        if not role:
            raise ValueError("there is no such a role")
        user = User(username=us.payload["username"],
                    password_hash=generate_password_hash(us.payload["password"]), # noqa E501
                    role_id=role.id)
        db.session.add(user)
        db.session.commit()
        return user, 201


@us.route("/login")
class LoginApi(Resource):
    @us.expect(login_model)
    def post(self):
        user = User.query.filter(User.username ==
                                 us.payload["username"]).first()
        if not user:
            return {"error": "User does not exist"}, 401
        if not check_password_hash(user.password_hash,
                                   us.payload["password"]):
            return {"error": "Incorrect password"}, 401

        return {"access_token": create_access_token(user),
                "role": user.role.name}
