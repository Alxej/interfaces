from flask_restx import fields

from .extensions import api

category_model = api.model("Category", {
    "id": fields.Integer,
    "category_name": fields.String
})

category_input_model = api.model("CategoryInput", {
    "category_name": fields.String
})

brand_model = api.model("Brand", {
    "id": fields.Integer,
    "brand_name": fields.String
})

brand_input_model = api.model("BrandInput", {
    "brand_name": fields.String
})

image_model = api.model("Image", {
    "id": fields.Integer,
    "product_id": fields.Integer,
    "image_name": fields.String
})

image_input_model = api.model("ImageInput", {
    "product_id": fields.Integer,
})

product_model = api.model("Product", {
    "id": fields.Integer,
    "name": fields.String,
    "product_description": fields.String,
    "price": fields.Float,
    "images": fields.Nested(image_model),
    "category": fields.Nested(category_model),
    "brand": fields.Nested(brand_model)
})

product_input_model = api.model("ProductAdding", {
    "name": fields.String,
    "description": fields.String,
    "price": fields.Float,
    "category_id": fields.Integer,
    "brand_id": fields.Integer
})
