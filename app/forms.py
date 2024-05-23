from wtforms import StringField, SubmitField, DecimalField, MultipleFileField, TextAreaField, SelectField, validators, widgets, SelectMultipleField, PasswordField
from wtforms.validators import DataRequired, Length, ValidationError
from flask_wtf import FlaskForm
from flask import url_for
from markupsafe import Markup
import os

class ImageSelectionField(widgets.ListWidget):
    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        html = [f"<{self.html_tag} {widgets.html_params(**kwargs)}>"]
        path = os.getcwd().replace('\\', '/')
        for subfield in field:
            html.append(f"<div class='row justify-content-center'><div class='col-4'>")
            html.append(f"<li class='list-group-item'>{subfield(class_='form-check-input me-1')} {subfield.label}</li>")
            html.append(f"<img class='img-thumbnail rounded float-end' src='{url_for('static', filename=f'uploads/{subfield.label.text}')}' alt='{subfield.label.text}'></img></div></div>")
        html.append("</%s>" % self.html_tag)
        return Markup("".join(html))
    
class MultiCheckboxField(SelectMultipleField):
    widget = ImageSelectionField(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class ProductCreationForm(FlaskForm):
    name = StringField("Название товара: ", validators=[DataRequired(), Length(max=128)])
    product_description = TextAreaField('Описание: ', validators=[Length(max=256)])
    price = DecimalField(label="Цена: ", places=2)
    brand = SelectField("Бренд: ")
    category = SelectField("Категория: ")
    images = MultipleFileField("Выберите картинки: ")
    submit = SubmitField("Сохранить товар")

    def __init__(self, *args, **kwargs):
        super(ProductCreationForm, self).__init__(*args, **kwargs)
        from app.models import Brand, Category
        self.brand.choices = [(obj.id, obj.brand_name) for obj in Brand.query.order_by('brand_name')]
        self.category.choices = [(obj.id, obj.category_name) for obj in Category.query.order_by('category_name')]

class ProductEditingForm(ProductCreationForm):
    deleted_images = MultiCheckboxField('Выберите картинки для удаления')

    def __init__(self, *args, **kwargs):
        super(ProductEditingForm, self).__init__(*args, **kwargs)
    


class BrandCreationForm(FlaskForm):
    brand_name = StringField("Название бренда: ", validators=[DataRequired(), Length(max=128)])
    submit = SubmitField("Сохранить бренд")


class LoginForm(FlaskForm):
    username = StringField("Имя пользователя: ", validators=[DataRequired(), Length(max=128)])
    password = PasswordField("Пароль: ", validators=[DataRequired(), Length(max=128)])
    submit = SubmitField("Войти")


class RegistrationForm(FlaskForm):
    username = StringField("Имя пользователя: ", validators=[DataRequired(), Length(max=128)])
    password = PasswordField("Пароль: ", validators=[DataRequired(), Length(max=128)])
    role = SelectField("Роль: ")
    submit = SubmitField("Зарегистрировать")

class EditUserForm(FlaskForm):
    username = StringField("Имя пользователя: ", validators=[DataRequired(), Length(max=128)])
    role = SelectField("Роль: ")
    submit = SubmitField("Сохранить")


class CategoryCreationForm(FlaskForm):
    category_name = StringField("Название категории: ", validators=[DataRequired(), Length(max=128)])
    submit = SubmitField("Сохранить категорию")