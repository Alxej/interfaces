from flask_restx import Resource, Namespace, reqparse
from flask import url_for
from werkzeug.utils import secure_filename

import werkzeug
import os

from .extensions import db, allowed_file
from .api_models import category_model, category_input_model, brand_model, brand_input_model, image_model, product_model, product_input_model  # noqa: E501
from .models import Category, Brand, Product, Image

ns = Namespace("api")

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


@ns.route("/products")
class ProductListAPI(Resource):
    @ns.errorhandler(Exception)
    def handle_value_error_exception(exception):
        return {"error": str(exception)}, 400

    @ns.expect(pagination_parser)
    @ns.marshal_list_with(product_model)
    def get(self):
        p_args = pagination_parser.parse_args()
        page = p_args.get("page")
        per_page = p_args.get("per_page")
        products = Product.query.paginate(page=page, per_page=per_page)
        return products.items, 201

    @ns.expect(product_input_model)
    @ns.marshal_list_with(product_model)
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

    @ns.marshal_with(product_model)
    def get(self, id):
        product = Product.query.get(id)
        if not product:
            raise ValueError("no product with that id")
        return product

    @ns.expect(product_input_model)
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

    def delete(self, id):
        product = Product.query.get(id)
        if not product:
            raise ValueError("no product with that id")
        images = product.images
        for image in images:
            os.remove(os.getcwd().replace('\\', '/') + "/app" +
                      url_for('static', filename=f'uploads/{image.image_name}')) # noqa E501
            db.session.delete(image)
            db.session.flush()
        db.session.delete(product)
        db.session.commit()
        return {"message": "product deleted"}, 204


@ns.route("/images")
class ImageListAPI(Resource):
    @ns.marshal_list_with(image_model)
    def get(self):
        return Image.query.all()

    @ns.expect(image_parser)
    @ns.marshal_with(image_model)
    def post(self):
        args = image_parser.parse_args()
        product = Product.query.get(args['product_id'])
        if not product:
            raise ValueError("no product with that id")

        image = args['file']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join('app/static/uploads/',
                                    filename))
            image_to_add = Image(product_id=product.id,
                                 image_name=filename)
            db.session.add(image_to_add)
            db.session.commit()
            return image_to_add, 201
        else:
            raise ValueError("image is not allowed")


@ns.route("/images/<int:id>")
class ImageAPI(Resource):
    @ns.marshal_with(image_model)
    def get(self, id):
        image = Image.query.get(id)
        if not image:
            raise ValueError("there is no image with that id")
        return Image.query.get(id), 201

    @ns.expect(image_parser)
    @ns.marshal_with(image_model)
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

    def delete(self, id):
        image = Image.query.get(id)
        if not image:
            raise ValueError("there is no image with that id")
        os.remove(os.getcwd().replace('\\', '/') + "/app" +
                  url_for('static', filename=f'uploads/{image.image_name}'))
        db.session.delete(image)
        db.session.commit()
        return {"message": f"image {id} deleted"}, 204


@ns.route("/brands")
class BrandListAPI(Resource):
    @ns.errorhandler(Exception)
    def handle_value_error_exception(exception):
        return {"error": str(exception)}, 400

    @ns.marshal_list_with(brand_model)
    def get(self):
        return Brand.query.all()

    @ns.expect(brand_input_model)
    @ns.marshal_list_with(brand_model)
    def post(self):
        brand = Brand(brand_name=ns.payload["brand_name"])
        try:
            db.session.add(brand)
            db.session.flush()
            db.session.commit()
            return brand, 201
        except Exception:
            return {}, 408


@ns.route("/brands/<int:id>")
class BrandApi(Resource):
    @ns.errorhandler(Exception)
    def handle_value_error_exception(exception):
        return {"error": str(exception)}, 400

    @ns.marshal_with(brand_model)
    def get(self, id):
        brand = Brand.query.get(id)
        if not brand:
            raise ValueError("brand with that id is not exist")
        return brand, 201

    @ns.expect(brand_input_model)
    @ns.marshal_with(brand_model)
    def put(self, id):
        brand = Brand.query.get(id)
        if not brand:
            raise ValueError("brand with that id is not exist")
        brand.brand_name = ns.payload["brand_name"]
        db.session.commit()
        return brand, 201

    def delete(self, id):
        brand = Brand.query.get(id)
        if not brand:
            raise ValueError("brand with that id is not exist")
        db.session.delete(brand)
        db.session.commit()
        return {}, 204


@ns.route("/categories")
class CategoryListAPI(Resource):
    @ns.errorhandler(Exception)
    def handle_value_error_exception(exception):
        return {"error": str(exception)}, 400

    @ns.marshal_list_with(category_model)
    def get(self):
        return Category.query.all()

    @ns.expect(category_input_model)
    @ns.marshal_list_with(category_model)
    def post(self):
        category = Category(category_name=ns.payload["category_name"])
        try:
            db.session.add(category)
            db.session.flush()
            db.session.commit()
            return category, 201
        except Exception:
            return {}, 408


@ns.route("/categories/<int:id>")
class CategoryApi(Resource):
    @ns.errorhandler(Exception)
    def handle_value_error_exception(exception):
        return {"error": str(exception)}, 400

    @ns.marshal_with(category_model)
    def get(self, id):
        category = Category.query.get(id)
        if not category:
            raise ValueError("category with that id is not exist")
        return category, 201

    @ns.expect(category_input_model)
    @ns.marshal_with(category_model)
    def put(self, id):
        category = Category.query.get(id)
        if not category:
            raise ValueError("category with that id is not exist")
        category.category_name = ns.payload["category_name"]
        db.session.commit()
        return category, 201

    def delete(self, id):
        category = Category.query.get(id)
        if not category:
            raise ValueError("category with that id is not exist")
        db.session.delete(category)
        db.session.commit()
        return {}, 204
