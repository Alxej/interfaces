# Лабы по интерфейсам


![N|li](https://cdn.7tv.app/emote/63ec1c6988b87ef33e5f679a/4x.webp)


Гои, ниже будет гайдец по всякой полезной фигне, которую будет не понятно как использовать.

## Структура
- Файл routes.py - просто помойка, куда я скинул прошлый функционал, который не необходим для работы
- Файл extensions.py - файл для дополнительной инициализации полезных штук
- Файл resources.py - файл со всем функционалом и API (потом оттуда вынесу все функции в отдельный файлик)

## Создание БД
Введите команды (не факт, что все нужны, но по введении всех их в cmd у вас должно всё создаться)
```sh
flask db init
flask db migrate
flask db upgrade
```

## Авторизация

- Первая проблема в том, что вам понадобятся добавленные в базу данных роли, но функционал добавления ролей я не добавил, роли я добавлял вручную через прогу (DB browser for SQLite)
- Нужно добавлять роли со следующими названиями: admin, manager, guest
- Админ - все права, манагер - все, кроме работы с пользователями, гест - заказы может делать разве что (да, я успел сделать 3 лабу вроде как, но мб не правильно)
- Чтобы авторизоваться нужно выполнить пару действий: получить зарегаться, залогиниться (получив jwt кодец) и авторизоваться (справа сверху кнопка)
- При введении кода нужно перед ним написать слово Bearer (хз с чем это связано, наверное с тем, что я использовал какой-то не совсем обычный jwt код, но у меня он принял лабу так что пофиг)

## Плагины
Всё есть в requirements.txt
``` pip install -r requirements.txt```

## Думайте

![N|li](https://cdn.7tv.app/emote/640b43116b587ac1a11be71b/4x.webp)