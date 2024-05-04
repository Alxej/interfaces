@app.route("/products")
    @app.route("/")
    def index():
        from app.models import Product
        page = request.args.get('page', 1, type=int)
        products = Product.query.paginate(page=page, per_page=6)
        return render_template('index.html',
                               title="Товары",
                               products=products,
                               page=page)
    
    @app.route("/pr")
    def pr():
        return render_template("Competence.html")
    
    @app.route("/products/<int:product_id>/delete")
    def product_delete(product_id):
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
    
    @app.route("/products/<int:product_id>/edit")
    def product_edit(product_id):
        from app.forms import ProductEditingForm
        from app.models import Product
        product = Product.query.filter(Product.id == product_id).all()[0]
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
        return render_template('editproduct.html', form=form,
                               product_name=product.name,
                               product_description=product.product_description,
                               price=product.price,
                               brand=product.brand.brand_name,
                               category=product.category.category_name, 
                               images_label=uploaded)
    
    @app.route("/products/<int:product_id>/edit", methods=['POST', 'GET'])
    def product_edit_in_db(product_id):
        from app.forms import ProductEditingForm
        from app.models import Product, Image
        product = Product.query.filter(Product.id == product_id).all()[0]
        form = ProductEditingForm(request.form)
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
                flash("Ошибка сохранения бренда")
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
                               images_label=uploaded)

    @app.route("/createproduct", methods=["POST", "GET"])
    def createproduct():
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
                               form=form)

    @app.route("/brands")
    def brands():
        from app.models import Brand
        brands = Brand.query.order_by(Brand.brand_name.desc())
        return render_template('brands.html', title="Бренды", brands=brands)
    
    @app.route("/createbrand", methods=["POST", "GET"])
    def createbrand():
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
        return render_template('createbrand.html', title="Создание", form=form)

    @app.route("/brands/<int:brand_id>/delete")
    def brand_delete(brand_id):
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
                                       brand_name=brand.brand_name)
            except Exception:
                print("не получается")
        return render_template('brandedit.html',
                               title="Создание",
                               form=form,
                               brand_name=brand.brand_name)
    
    @app.route("/categories")
    def categories():
        from app.models import Category
        categories = Category.query.order_by(Category.category_name.desc())
        return render_template('categories.html',
                               title="Категории",
                               categories=categories)
    
    @app.route("/createcategory", methods=["POST", "GET"])
    def createcategory():
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
                               form=form)

    @app.route("/categories/<int:category_id>/delete")
    def category_delete(category_id):
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

    @app.route("/categories/<int:category_id>/edit", methods=["POST", "GET"])
    def category_edit(category_id):
        from app.forms import CategoryCreationForm
        from app.models import Category
        category = Category.query.filter(Category.id == category_id).all()[0]
        form = CategoryCreationForm()
        return render_template('categoryedit.html',
                               title="Создание",
                               form=form,
                               category_name=category.category_name)

    @app.route("/categories/<int:category_id>/edit", methods=["POST", "GET"])
    def category_edit_db(category_id):
        from app.forms import CategoryCreationForm
        from app.models import Category
        category = Category.query.filter(Category.id == category_id).all()[0]
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
                                       category_name=category.category_name)
            except Exception:
                print("не получается")
        return render_template('categoryedit.html',
                               title="Создание",
                               form=form,
                               category_name=category.category_name)