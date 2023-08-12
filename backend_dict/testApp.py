from flask import Flask, \
    render_template, \
    request, \
    g, \
    url_for, \
    abort, \
    flash, \
    session, \
    redirect

from FDataBase import FDataBase
import sqlite3
import os

app = Flask(__name__)
# конфигурация
DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'
USERNAME = 'admin'
PASSWORD = '123'
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))

menu = [
    {"title": "My dict", "url": "dict"},
    {"title": "Add post", "url": "add_post"},
    {"title": "Login", "url": "login"},
    {"title": "About", "url": "about"},
    {"title": "Contacts", "url": "contacts"}]


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    """Вспомогательная функция для создания таблиц БД"""
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    '''Соединение с БД, если оно еще не установлено'''
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.teardown_appcontext
def close_db(error):
    '''Закрываем соединение с БД, если оно было установлено'''
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route("/")
def index():
    return render_template('index.html', my_text='Main Page', menu=menu)


@app.route("/dict")
def dict():
    db = get_db()
    dbase = FDataBase(db)
    return render_template('dict.html', my_text='Dict', menu=menu, posts=dbase.getPostsAnonce())


@app.route("/login", methods=["POST", "GET"])
def login():
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == 'POST' and request.form['username'] == "selfedu" and request.form['psw'] == "123":
        session['userLogged'] = request.form['username']
        return redirect(url_for('profile', username=session['userLogged']))
    return render_template('login.html', my_text='Autorize', menu=menu)


@app.route("/profile/<username>")
def profile(username):
    # if 'userLogged' not in session or session['userLogged'] != username:
    #     abort(401)
    # return f"Пользователь: {username}"
    return render_template('profile.html', my_text=username, menu=menu)


@app.route("/about")
def about():
    return render_template('index.html', my_text='About', menu=menu)


@app.route("/contacts", methods=["POST", "GET"])
def contacts():
    if request.method == 'POST':
        print(request.form)

        if len(request.form['username']) > 2:
            flash('Сообщение отправлено', category='success')
        else:
            flash('Ошибка отправки', category='error')

    return render_template('contacts.html', my_text='Contacts', menu=menu)


@app.errorhandler(404)
def pageNotFount(error):
    return render_template('page404.html', title="Страница не найдена", menu=menu), 404


@app.route("/add_post", methods=["POST", "GET"])
def addPost():
    db = get_db()
    dbase = FDataBase(db)

    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.addPost(request.form['name'], request.form['post'])
            if not res:
                flash('Ошибка добавления статьи', category='error')
            else:
                flash('Статья добавлена успешно', category='success')
        else:
            flash('Ошибка добавления статьи', category='error')

    return render_template('add_post.html', menu=menu, title="Добавление статьи")

if __name__ == "__main__":
    app.run(debug=True)
