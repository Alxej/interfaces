from flask import Flask, render_template, flash, redirect, url_for, request, session
from flask_uploads import configure_uploads
from flask_cors import CORS
from app.forms import (ProductCreationForm,
                       CategoryCreationForm,
                       BrandCreationForm,
                       LoginForm,
                       RegistrationForm,
                       EditUserForm)
from werkzeug.security import generate_password_hash, check_password_hash

import os

from .extensions import api, db, migrate, jwt, images, api_bp
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
    app.config['CORS_HEADERS'] = 'Content-Type'
    configure_uploads(app, images)

    # api.init_app(app)
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

    app.register_blueprint(api_bp)

    CORS(app=app, resources={r"/api/*": {"origins": "*"}})

    @app.route('/', methods=['POST', 'GET'])
    def start():
        return redirect(url_for('login'))

    @app.route('/login', methods=['POST', 'GET'])
    def login():
        from app.models import User
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter(User.username == form.username.data).first()
            if user and check_password_hash(user.password_hash, form.password.data):
                session['user_role'] = user.role.name
                session['username'] = user.username
                return redirect(url_for('index'))
            else:
                flash('Попробуйте ещё')
        return render_template('login.html', form=form)

    @app.route('/logout', methods=['POST', 'GET'])
    def logout():
        session.clear()
        return redirect(url_for('login'))

    @app.route('/register', methods=['POST', 'GET'])
    def register():
        if 'user_role' not in session.keys():
            return {"error": "you don`t have permission for that"}, 403
        else:
            if session['user_role'] != "admin":
                return {"error": "you don`t have permission for that"}, 403
        from app.models import User, Role
        form = RegistrationForm()
        choices = []
        for role in Role.query.all():
            choices.append((role.id, role.name))
        form.role.choices = choices
        if form.validate_on_submit():
            user = User(username=form.username.data,
                        password_hash=generate_password_hash(form.password.data),
                        role_id=form.role.data[0])
            try:
                db.session.add(user)
                db.session.commit()
                return redirect('users')
            except Exception:
                flash("Попробуйте ещё раз")
        return render_template('register.html', form=form, role=session['user_role'], username=session['username'])

    @app.route("/products")
    def index():
        from app.models import Product
        page = request.args.get('page', 1, type=int)
        products = Product.query.paginate(page=page, per_page=6)
        return render_template('index.html',
                               title="Товары",
                               products=products,
                               page=page,
                               role=session['user_role'],
                               username=session['username'])

    @app.route("/products/<int:product_id>/delete")
    def product_delete(product_id):
        if 'user_role' not in session.keys():
            return {"error": "you don`t have permission for that"}, 403
        else:
            if session['user_role'] == "guest":
                return {"error": "you don`t have permission for that"}, 403
        from app.models import Product
        try:
            products = Product.query.filter(Product.id == product_id).all()
            for image in products[0].images:
                print(os.getcwd())
                os.remove(os.getcwd().replace('\\', '/') + "/app" + url_for('static', filename=f'uploads/{image.image_name}'))
                db.session.delete(image)
            db.session.delete(products[0])
            db.session.flush()
            db.session.commit()
            return redirect(url_for("index"))
        except Exception as e:
            db.session.rollback()
            print("не получается")
            print(e)
        return redirect(url_for("index"))

    @app.route("/products/<int:product_id>/edit", methods=["POST", "GET"])
    def product_edit(product_id):
        if 'user_role' not in session.keys():
            return {"error": "you don`t have permission for that"}, 403
        else:
            if session['user_role'] == "guest":
                return {"error": "you don`t have permission for that"}, 403
        from app.forms import ProductEditingForm
        from app.models import Product, Image
        product = Product.query.filter(Product.id == product_id).first()
        form = ProductEditingForm()
        form.product_description.default = product.product_description
        choices = []
        for image in product.images:
            choices.append((image.id, image.image_name))
        form.deleted_images.choices = choices
        uploaded = ""
        for image in product.images:
            uploaded += image.image_name
            uploaded += " "
        
        if form.validate_on_submit():
            try:
                product.name = form.name.data
                # print(form.product_description.data)
                # print(form.images.data)
                product.product_description = form.product_description.data
                product.price = "{:.2f}".format(form.price.data)
                product.brand_id = form.brand.data[0]
                product.category_id = form.category.data[0]
                db.session.flush()

                images_list = []
                if form.images.data: 
                    for image in form.images.data:
                        try:
                            filename = images.save(image)
                            images_list.append(Image(product_id=product.id,
                                                     image_name=filename))
                        except Exception:
                            flash("Некоторые файлы не сохранены")
                            continue
                    if len(images_list) > 0:
                        db.session.add_all(images_list)
                        db.session.flush()

                for image in product.images:
                    if str(image.id) in form.deleted_images.data:
                        os.remove(os.getcwd().replace('\\', '/') + "/app" + url_for('static', filename=f'uploads/{image.image_name}'))
                        db.session.delete(image)

                db.session.flush()
                db.session.commit()
                flash("Информация о продукте обновлена")

                choices = []
                for image in product.images:
                    choices.append((image.id, image.image_name))
                    form.deleted_images.choices = choices
            except Exception as e:
                db.session.rollback()
                print(e)
                flash("Ошибка сохранения")
        uploaded = ""
        for image in product.images:
            uploaded += image.image_name
            uploaded += " "
        return render_template('editproduct.html', form=form,
                               product_name=product.name,
                               product_description=product.product_description,
                               price=product.price,
                               brand=product.brand.brand_name,
                               category=product.category.category_name, 
                               images_label=uploaded, role = session['user_role'], username=session['username'])

    # @app.route("/products/<int:product_id>/edit", methods=['POST'])
    # def product_edit_in_db(product_id):
    #     if 'user_role' not in session.keys():
    #         return {"error": "you don`t have permission for that"}, 403
    #     else:
    #         if session['user_role'] == "guest":
    #             return {"error": "you don`t have permission for that"}, 403
    #     from app.forms import ProductEditingForm
    #     from app.models import Product, Image
    #     product = Product.query.filter(Product.id == product_id).all()[0]
    #     form = ProductEditingForm(request.form)
    #     if form.validate_on_submit():
    #         try:
    #             product.name = form.name.data
    #             # print(form.product_description.data)
    #             # print(form.images.data)
    #             product.product_description = form.product_description.data
    #             product.price = "{:.2f}".format(form.price.data)
    #             product.brand_id = form.brand.data[0]
    #             product.category_id = form.category.data[0]
    #             db.session.flush()

    #             images_list = []
    #             if form.images.data: 
    #                 for image in form.images.data:
    #                     try:
    #                         filename = images.save(image)
    #                         images_list.append(Image(product_id=product.id,
    #                                                  image_name=filename))
    #                     except Exception:
    #                         flash("Некоторые файлы не сохранены")
    #                         continue
    #                 if len(images_list) > 0:
    #                     db.session.add_all(images_list)
    #                     db.session.flush()

    #             for image in product.images:
    #                 if str(image.id) in form.deleted_images.data:
    #                     os.remove(os.getcwd().replace('\\', '/') + "/app" + url_for('static', filename=f'uploads/{image.image_name}'))
    #                     db.session.delete(image)

    #             db.session.flush()
    #             db.session.commit()
    #             flash("Информация о продукте обновлена")

    #             choices = []
    #             for image in product.images:
    #                 choices.append((image.id, image.image_name))
    #                 form.deleted_images.choices = choices
    #         except Exception as e:
    #             db.session.rollback()
    #             print(e)
    #             flash("Ошибка сохранения бренда")
    #     uploaded = ""
    #     for image in product.images:
    #         uploaded += image.image_name
    #         uploaded += " "
    #     return render_template('editproduct.html', form=form,
    #                            product_name=product.name,
    #                            product_description=product.product_description,
    #                            price=product.price,
    #                            brand=product.brand.brand_name,
    #                            category=product.category.category_name, 
    #                            images_label=uploaded, role = session['user_role'], username=session['username'])

    @app.route("/createproduct", methods=["POST", "GET"])
    def createproduct():
        if 'user_role' not in session.keys():
            return {"error": "you don`t have permission for that"}, 403
        else:
            if session['user_role'] == "guest":
                return {"error": "you don`t have permission for that"}, 403
        form = ProductCreationForm()
        if form.validate_on_submit():
            from app.models import Product, Image
            product = Product(name=form.name.data,
                              product_description=form.product_description.data,
                              price="{:.2f}".format(form.price.data),
                              brand_id=form.brand.data[0],
                              category_id=form.category.data[0])
            try:
                db.session.add(product)
                db.session.flush()
                images_list = []
                if form.images.data: 
                    for image in form.images.data:
                        try:
                            filename = images.save(image)
                            images_list.append(Image(product_id=product.id,
                                                     image_name=filename))
                        except Exception:
                            continue
                    if len(images_list) > 0:
                        db.session.add_all(images_list)
                        db.session.flush()
                db.session.commit()
                flash("Продукт добавлен")
            except Exception as e:
                db.session.rollback()
                print(e)
                flash("Ошибка сохранения бренда")
        return render_template('createproduct.html',
                               title="Создание",
                               form=form, role = session['user_role'], username=session['username'])

    @app.route("/brands")
    def brands():
        if 'user_role' not in session.keys():
            return {"error": "you don`t have permission for that"}, 403
        else:
            if session['user_role'] == "guest":
                return {"error": "you don`t have permission for that"}, 403
        from app.models import Brand
        brands = Brand.query.order_by(Brand.brand_name.desc())
        return render_template('brands.html', title="Бренды", brands=brands, role = session['user_role'], username=session['username'])

    @app.route("/createbrand", methods=["POST", "GET"])
    def createbrand():
        if 'user_role' not in session.keys():
            return {"error": "you don`t have permission for that"}, 403
        else:
            if session['user_role'] == "guest":
                return {"error": "you don`t have permission for that"}, 403
        form = BrandCreationForm()
        print(form.validate())
        print(form.errors)
        if form.validate_on_submit():
            print("sadasdsada")
            from app.models import Brand
            brand = Brand(brand_name=form.brand_name.data)
            try:
                db.session.add(brand)
                db.session.flush()
                db.session.commit()
                flash("Бренд добавлен")
            except Exception:
                db.session.rollback()
                flash("Ошибка сохранения бренда")
        return render_template('createbrand.html', title="Создание", form=form, role = session['user_role'], username=session['username'])

    @app.route("/brands/<int:brand_id>/delete")
    def brand_delete(brand_id):
        if 'user_role' not in session.keys():
            return {"error": "you don`t have permission for that"}, 403
        else:
            if session['user_role'] == "guest":
                return {"error": "you don`t have permission for that"}, 403
        from app.models import Brand
        try:
            brands = Brand.query.filter(Brand.id == brand_id).all()
            db.session.delete(brands[0])
            db.session.flush()
            db.session.commit()
            return redirect(url_for("brands"))
        except Exception:
            print("не получается")
        return redirect(url_for("brands"))

    @app.route("/brands/<int:brand_id>/edit", methods=["POST", "GET"])
    def brand_edit(brand_id):
        if 'user_role' not in session.keys():
            return {"error": "you don`t have permission for that"}, 403
        else:
            if session['user_role'] == "guest":
                return {"error": "you don`t have permission for that"}, 403
        from app.forms import BrandCreationForm
        from app.models import Brand
        brand = Brand.query.filter(Brand.id == brand_id).all()[0]
        form = BrandCreationForm()
        if form.validate_on_submit():
            new_name = form.brand_name.data
            try:
                brand.brand_name = new_name
                db.session.flush()
                db.session.commit()
                return render_template('brandedit.html',
                                       title="Создание",
                                       form=form,
                                       brand_name=brand.brand_name,
                                       role=session['user_role'],
                                       username=session['username'])
            except Exception:
                print("не получается")
        return render_template('brandedit.html',
                               title="Создание",
                               form=form,
                               brand_name=brand.brand_name, role = session['user_role'], username=session['username'])

    @app.route("/categories")
    def categories():
        if 'user_role' not in session.keys():
            return {"error": "you don`t have permission for that"}, 403
        else:
            if session['user_role'] == "guest":
                return {"error": "you don`t have permission for that"}, 403
        from app.models import Category
        categories = Category.query.order_by(Category.category_name.desc())
        return render_template('categories.html',
                               title="Категории",
                               categories=categories, role = session['user_role'], username=session['username'])

    @app.route("/createcategory", methods=["POST", "GET"])
    def createcategory():
        if 'user_role' not in session.keys():
            return {"error": "you don`t have permission for that"}, 403
        else:
            if session['user_role'] == "guest":
                return {"error": "you don`t have permission for that"}, 403
        form = CategoryCreationForm()
        print(form.validate())
        print(form.errors)
        if form.validate_on_submit():
            print("sadasdsada")
            from app.models import Category
            category = Category(category_name=form.category_name.data)
            try:
                db.session.add(category)
                db.session.flush()
                db.session.commit()
                flash("Категория добавлена")
            except Exception:
                db.session.rollback()
                flash("Ошибка сохранения категории")
        return render_template('createcategory.html',
                               title="Создание",
                               form=form, role = session['user_role'], username=session['username'])

    @app.route("/categories/<int:category_id>/delete")
    def category_delete(category_id):
        if 'user_role' not in session.keys():
            return {"error": "you don`t have permission for that"}, 403
        else:
            if session['user_role'] == "guest":
                return {"error": "you don`t have permission for that"}, 403
        from app.models import Category
        try:
            categories = Category.query.filter(Category.id == category_id).all()
            db.session.delete(categories[0])
            db.session.flush()
            db.session.commit()
            return redirect(url_for("categories"))
        except Exception:
            print("не получается")
        return redirect(url_for("categories"))

    @app.route("/categories/<int:category_id>/edit", methods=["GET"])
    def category_edit(category_id):
        if 'user_role' not in session.keys():
            return {"error": "you don`t have permission for that"}, 403
        else:
            if session['user_role'] == "guest":
                return {"error": "you don`t have permission for that"}, 403
        from app.forms import CategoryCreationForm
        from app.models import Category
        category = Category.query.filter(Category.id == category_id).first()
        form = CategoryCreationForm()
        return render_template('categoryedit.html',
                               title="Создание",
                               form=form,
                               category_name=category.category_name, role = session['user_role'], username=session['username'])

    @app.route("/categories/<int:category_id>/edit", methods=["POST", "GET"])
    def category_edit_db(category_id):
        if 'user_role' not in session.keys():
            return {"error": "you don`t have permission for that"}, 403
        else:
            if session['user_role'] == "guest":
                return {"error": "you don`t have permission for that"}, 403
        from app.forms import CategoryCreationForm
        from app.models import Category
        category = Category.query.filter(Category.id == category_id).first()
        form = CategoryCreationForm(request.form)
        if form.validate_on_submit():
            new_name = form.category_name.data
            try:
                category.category_name = new_name
                db.session.flush()
                db.session.commit()
                return render_template('categoryedit.html',
                                       title="Создание",
                                       form=form,
                                       category_name=category.category_name,
                                       role=session['user_role'],
                                       username=session['username'])
            except Exception:
                flash("не получается")
        return render_template('categoryedit.html',
                               title="Создание",
                               form=form,
                               category_name=category.category_name,
                               role=session['user_role'],
                               username=session['username'])

    @app.route("/users", methods=["POST", "GET"])
    def users():
        if 'user_role' not in session.keys():
            return {"error": "you don`t have permission for that"}, 403
        else:
            if session['user_role'] != "admin":
                return {"error": "you don`t have permission for that"}, 403
        from app.models import User
        users = User.query.filter(User.username != session['username']).order_by(User.username.desc())
        return render_template('users.html',
                               title="Пользователи",
                               users=users, role=session['user_role'], username=session['username'])

    @app.route("/users/<int:id>/edit", methods=["POST", "GET"])
    def user_edit(id):
        if 'user_role' not in session.keys():
            return {"error": "you don`t have permission for that"}, 403
        else:
            if session['user_role'] != "admin":
                return {"error": "you don`t have permission for that"}, 403
        from app.models import User, Role
        form = EditUserForm()
        choices = []
        for role in Role.query.all():
            choices.append((role.id, role.name))
        form.role.choices = choices
        user = User.query.get(id)
        if form.validate_on_submit():
            user.username = form.username.data
            user.role_id = form.role.data[0]
            try:
                db.session.commit()
            except Exception:
                flash("Попробуйте ещё раз")
        return render_template('editUser.html',
                               form=form,
                               cur_role=user.role.name,
                               cur_username=user.username,
                               role=session['user_role'],
                               username=session['username'])

    @app.route("/users/<int:id>/delete", methods=["POST", "GET"])
    def user_delete(id):
        if 'user_role' not in session.keys():
            return {"error": "you don`t have permission for that"}, 403
        else:
            if session['user_role'] != "admin":
                return {"error": "you don`t have permission for that"}, 403
        from app.models import User
        users = User.query.get(id)
        try:
            db.session.delete(users)
            db.session.commit()
            return redirect(url_for('users'))
        except Exception:
            flash("Попробуйте ещё")
            return redirect(url_for('users'))

    @app.route("/products/<int:id>/order", methods=["POST", "GET"])
    def order(id):
        from app.models import User, Order, Product
        user = User.query.filter(User.username == session['username']).first()
        product = Product.query.get(id)
        order = Order(user_id=user.id,
                      product_id=product.id,
                      total_price=product.price)
        try:
            db.session.add(order)
            db.session.commit()
            return redirect(url_for('index'))
        except Exception:
            return redirect(url_for('index'))
        
    @app.route("/basket", methods=["POST", "GET"])
    def basket():
        from app.models import User, Order, Product
        user = User.query.filter(User.username == session['username']).first()
        page = request.args.get('page', 1, type=int)
        orders = Order.query.filter(Order.user_id == user.id).filter(Order.status == False).paginate(page=page, per_page=6)
        products = []
        for order in orders:
            product = Product.query.get(order.product_id)
            if not product:
                continue
            products.append(product)
        return render_template('backet.html',
                               title="Корзина",
                               products=products,
                               orders=orders,
                               page=page,
                               role=session['user_role'],
                               username=session['username'])

    @app.route("/basket/<int:id>/buy", methods=["POST", "GET"])
    def basket_buy(id):
        from app.models import Order
        order = Order.query.get(id)
        order.status = True
        db.session.commit()
        return redirect(url_for('basket'))

    @app.route("/basket/<int:id>/remove", methods=["POST", "GET"])
    def basket_remove(id):
        from app.models import Order
        order = Order.query.get(id)
        db.session.delete(order)
        db.session.commit()
        return redirect(url_for('basket'))


    @app.route("/history", methods=["POST", "GET"])
    def history():
        from app.models import User, Order, Product
        user = User.query.filter(User.username == session['username']).first()
        page = request.args.get('page', 1, type=int)
        orders = Order.query.filter(Order.user_id == user.id).filter(Order.status == True).paginate(page=page, per_page=6)
        products = []
        for order in orders:
            product = Product.query.get(order.product_id)
            if not product:
                continue
            products.append(product)
        return render_template('history.html',
                               title="Корзина",
                               products=products,
                               orders=orders,
                               page=page,
                               role=session['user_role'],
                               username=session['username'])

    return app
