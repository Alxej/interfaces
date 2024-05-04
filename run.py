from app import create_app
from app.models import db

urls = [{"name": "Список товаров", "url": "/"},
        {"name": "Бренды", "url": "/brands"},
        {"name": "Категории", "url": "/categories"},]

if __name__ == '__main__':
    db.init_app(app = create_app())
