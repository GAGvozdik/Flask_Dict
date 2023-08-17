from flask import Flask, render_template, request, g, url_for, abort, flash, session, redirect, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import sqlite3
import os
import numpy as np

from FDataBase import FDataBase
from UserLogin import UserLogin
from forms import LoginForm, RegisterForm, starsForm

app = Flask(__name__)

# конфигурация
DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'
USERNAME = 'admin'
PASSWORD = '123'
MAX_CONTENT_LENGTH = 1024 * 1024

app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success"

menu = [
    {"title": "МФК", "url": "/"},
    {"title": "Авторизация", "url": "/login"},
    {"title": "Подобрать МФК", "url": "/question"},
    {"title": "Обратная связь", "url": "/contacts"},
    {"title": "О нас", "url": "/about"}]


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


dbase = None


@app.before_request
def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    '''Закрываем соединение с БД, если оно было установлено'''
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route("/")
@app.route("/dict")
def dict():
    return render_template('dict.html', my_text='МФК', menu=menu, mfk_table=dbase.getMfkAnonce())


@app.route("/about")
def about():
    return render_template('about.html', my_text='About', menu=menu)





@app.route("/mfk/<alias>", methods=['GET', 'POST'])
def showMfk(alias):
    mfk = dbase.getMfk(alias)
    if not mfk:
        abort(404)
        abort(404)

    my_comments = dbase.getComment(alias)
    for my in my_comments:
        print("comments = ", my)
    print("altype = ", type(alias))
    print("comments = ", mfk)
    stars_numb = 3
    return render_template('mfk.html', menu=menu, mfk=mfk, alias=alias, my_comments=dbase.getComment(alias), stars_numb=stars_numb)

@app.route("/question", methods=['GET', 'POST'])
@login_required
def question():

    return render_template('question.html', menu=menu)


@app.route("/addComment/<alias>", methods=['GET', 'POST'])
@login_required
def addComment(alias):

    mfk = dbase.getMfk(alias)
    if not mfk:
        abort(404)

    form = starsForm()
    if form.validate_on_submit():
        comments_numb = len(dbase.getUserCommentsNumb(current_user.getName()))
        print('comments_numb')
        print(comments_numb)
        if comments_numb < 10:
            res = dbase.addComment(current_user.getName(), form.text.data, str(alias), form.score.data[-1], mfk[0])
            if not res:
                flash('Ошибка. Оценка не добавлена, попробуйте перезагрузить страницу', category='error')
            else:
                flash('Оценка добавлена успешно', category='success')

                dbase.updateUserCommentsNumb(comments_numb, current_user.getEmail())

                # ----------------------------------------------
                score_list = dbase.getMfkScore(alias)
                mfk_score = 0
                len_score_list = 0
                for i in score_list:
                    for j in i:
                        print('j = ', j)
                        mfk_score += int(j)
                        len_score_list += 1

                mfk_score = round(mfk_score /len_score_list)
                print('mfk_score, len_score_list = ', mfk_score, len_score_list)
                dbase.updateMfkScore(alias, mfk_score)

                print(comments_numb)
        else:
            flash('Вы достигли лимита коментариев. Удалите комментарий, чтобы добавить новый', category='error')

            # return redirect(url_for("showMfk(alias)"))
    form = starsForm()

    return render_template('comments.html', menu=menu, mfk=mfk, alias=alias, my_comments=dbase.getComment(alias), form=form)



@app.errorhandler(404)
def pageNotFount(error):
    return render_template('page404.html', my_text="Страница не найдена", menu=menu), 404


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    form = LoginForm()
    if form.validate_on_submit():
        user = dbase.getUserByEmail(form.email.data)
        if user and check_password_hash(user['psw'], form.psw.data):
            userlogin = UserLogin().create(user)
            rm = form.remember.data
            login_user(userlogin, remember=rm)
            return redirect(request.args.get("next") or url_for("profile"))

        flash("Неверная пара логин/пароль", "error")
    return render_template("login.html", menu=menu, my_text="Авторизация", form=form)


@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hash = generate_password_hash(request.form['psw'])
        res = dbase.addUser(form.name.data, form.email.data, hash)
        if res:
            flash("Вы успешно зарегистрированы", "success")
            return redirect(url_for('login'))
        else:
            flash("Ошибка при добавлении в БД", "error")

    return render_template("register.html", menu=menu, my_text="Регистрация", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    for i in dbase.getUserCommentsNumb(current_user.getName()):
        print("i.score = ", i)

    your_comments = dbase.getUserCommentsNumb(current_user.getName())
    if your_comments == (False, False):
        class Person:
            def __init__(self, name):
                self.name = name

        your_comments = [Person("Tom")]
        your_comments[0].score = 0
        your_comments[0].mfkname = 0
        your_comments[0].mfktitle = 0

    return render_template('profile.html', my_text="Your Profile", menu=menu, your_comments=your_comments)


@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)


@app.route('/userava')
@login_required
def userava():
    img = current_user.getAvatar(app)
    if not img:
        return ""

    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h


@app.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash("Ошибка обновления аватара", "error")
                    return redirect(url_for('profile'))
                flash("Аватар обновлен", "success")
            except FileNotFoundError as e:
                flash("Ошибка чтения файла", "error")
        else:
            flash("Ошибка обновления аватара", "error")

    return redirect(url_for('profile'))


@app.route("/contacts", methods=["POST", "GET"])
@login_required
def contacts():
    # if request.method == 'POST':
    #     print(request.form)
    #
    #     if len(request.form['username']) > 2:
    #         flash('Сообщение отправлено', category='success')
    #     else:
    #         flash('Ошибка отправки', category='error')

    return render_template('contacts.html', my_text='Contacts', menu=menu)

if __name__ == "__main__":
    app.run(debug=True)
