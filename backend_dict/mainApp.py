from flask import Flask, render_template, request, g, url_for, abort, flash, session, redirect, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import sqlite3
import os
import numpy as np
from flask_mail import Mail, Message
from flask_bootstrap import Bootstrap
from random import randint

from FDataBase import FDataBase
from UserLogin import UserLogin
from forms import LoginForm, RegisterForm, starsForm, ValidateForm, recoveryForm, new_psw_form, ContactForm, searchForm, commentDelForm
from forms import PollForm1
from test import add_mfk_to_db
from flask_wtf.csrf import CSRFProtect
import os
from admin.admin import admin

#TODO вкладка авторизация ведет на пустую страницу 


app = Flask(__name__)
bootstrap = Bootstrap(app)
# Bootstrap(app)
# config
DATABASE = '/tmp/flsite.db'
DEBUG = True

USERNAME = 'admin'
PASSWORD = os.urandom(50).hex()


# mail config

mail = Mail(app)

app.config["MAIL_SERVER"] = 'smtp.gmail.com'
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = 'gvozdikgeorge@gmail.com'
app.config['MAIL_PASSWORD'] = 'mkdwvebgqqrmxkgt'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['SECRET_KEY'] = os.urandom(50).hex()
app.config['RECAPTCHA_PUBLIC_KEY'] = "6LeRRc0nAAAAAHncCrhRoeYqSqlBBl5b0kODY_qQ"
app.config['RECAPTCHA_PRIVATE_KEY'] = "6LeRRc0nAAAAAK6u6lMesUFuM-rnzQLWKFKI9xEV"


mail = Mail(app)

csrf = CSRFProtect(app)
csrf.init_app(app)
# app.config.update(
#     SESSION_COOKIE_SECURE=True,
#     SESSION_COOKIE_HTTPONLY=True,
#     SESSION_COOKIE_SAMESITE='Lax',
# )


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
    {"title": "Опрос", "url": "/poll"},
    {"title": "О нас", "url": "/about"},
    {"title": "admin", "url": "/admin"}]

max_commetns_numb = 7


app.register_blueprint(admin, url_prefix='/admin')



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

    add_mfk_to_db()

def rewrite_db():
    conn = sqlite3.connect('flsite.db')
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS comments')
    conn.commit()
    cursor.execute('DROP TABLE IF EXISTS users')
    conn.commit()
    cursor.execute('DROP TABLE IF EXISTS mfk')

    conn.commit()
    conn.close()
    create_db()
    add_mfk_to_db()


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


##############################################################################
# Main pages
##############################################################################

@app.route("/poll", methods=['GET', 'POST'])
def poll():
    form = PollForm1()
    form.interested.render_kw = {'style': '', 'class': ''}

    if form.validate_on_submit():
        if form.interested.data == 'st1' and not form.other2.data:
            flash('Пожалуйста, укажите причину для выбора "Другое"', category='error')

    return render_template('poll.html', my_text='Опросговна', menu=menu, form=form)

@app.route("/")
@app.route("/dict", methods=['GET', 'POST'])
def dict():
    form = searchForm()
    form.search.render_kw = {'placeholder': 'Введите текст'}
    print(0)
    if form.validate_on_submit():

        mfk_table = dbase.getSearchMfk(form.search.data)

        if mfk_table == (False, False):
            flash('МФК с таким описанием не найдено. Поменяйте формулировку', category='error')
            return redirect('dict')
        else:
            return render_template('dict.html', my_text='МФК', menu=menu, mfk_table=mfk_table, form=form)

    return render_template('dict.html', my_text='МФК', menu=menu, mfk_table=dbase.getMfkAnonce(), dbase=dbase, form=form, bootstrap=bootstrap)


@app.route("/about")
def about():
    return render_template('about.html', my_text='О нас', menu=menu)


@app.route("/mfk/<alias>", methods=['GET', 'POST'])
def showMfk(alias):
    mfk = dbase.getMfk(alias)
    if not mfk:
        abort(404)

    return render_template('mfk.html', menu=menu, mfk=mfk, alias=alias, my_comments=dbase.getComment(alias))


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

        if comments_numb < max_commetns_numb:

            is_comment_already_added = 0
            if dbase.getUserCommentsNumb(current_user.getName()) != (False, False):
                for i in dbase.getUserCommentsNumb(current_user.getName()):
                    for j in i:
                        if j == mfk[0]:
                            is_comment_already_added = 1

            if is_comment_already_added == 0:
                res = dbase.addComment(current_user.getName(), str(alias), form.score.data[-1], mfk[0], form.reason.data)
                if not res:
                    flash('Ошибка. Оценка не добавлена, попробуйте перезагрузить страницу', category='error')
                else:
                    flash('Оценка добавлена успешно', category='success')

                    if dbase.getUserCommentsNumb(current_user.getName()) != (False, False):
                        comments_numb = len(dbase.getUserCommentsNumb(current_user.getName()))
                    else:
                        comments_numb = 0
                    dbase.updateUserCommentsNumb(comments_numb, current_user.getEmail())

                    # ----------------------------------------------
                    score_list = dbase.getMfkScore(alias)
                    mfk_score = 0
                    len_score_list = 0
                    for i in score_list:
                        for j in i:
                            mfk_score += int(j)
                            len_score_list += 1

                    mfk_score = round(mfk_score / len_score_list)
                    dbase.updateMfkScore(alias, mfk_score)

                    score_numb = dbase.getMfkScoreNumb(alias)
                    for i in score_numb:
                        for j in i:
                            score_numb = j

                    if score_numb == None:
                        score_numb = 1
                    else:
                        score_numb += 1
                    print('score_numb', score_numb)
                    dbase.updateMfkScoreNumb(alias, score_numb)

            else:
                flash('Вы уже оставляли оценку этому мфк', category='error')
        else:
            flash('Вы достигли лимита коментариев. Удалите комментарий, чтобы добавить новый', category='error')
        return redirect(url_for('showMfk', alias=alias))

    return render_template('comments.html', menu=menu, mfk=mfk, alias=alias, my_comments=dbase.getComment(alias),
                           form=form)


@app.errorhandler(404)
def pageNotFount(error):
    return render_template('page404.html', my_text="Страница не найдена", menu=menu), 404


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    form = LoginForm()
    form.psw.render_kw = {'class': 'search-input'}
    form.email.render_kw = {'class': 'search-input'}

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
    form.name.render_kw = {'class': 'search-input'}
    form.psw.render_kw = {'class': 'search-input'}
    form.psw2.render_kw = {'class': 'search-input'}
    form.email.render_kw = {'class': 'search-input'}

    if form.validate_on_submit():
        if dbase.getUsersE(form.email.data) == (False, False):
            if dbase.getUsersN(form.name.data) == (False, False):
                msg = Message(subject='Verification code MFK Stars', sender='MFKStars@gmail.com',
                              recipients=[form.email.data])
                otp = randint(000000, 999999)
                msg.body = 'MFK Stars. Код подтверждения: ' + str(otp)
                mail.send(msg)
                print(otp)
                session['name'] = form.name.data
                session['email'] = form.email.data
                session['password'] = generate_password_hash(form.psw.data)
                session['otp'] = otp
                return redirect(url_for('verify'))
            else:
                flash("Пользователь с таким именем уже зарегистрирован", "error")
        else:
            flash("Пользователь с такой почтой уже зарегистрирован", "error")
    return render_template("register.html", menu=menu, my_text="Регистрация", form=form)


@app.route('/password_recovery', methods=["POST", "GET"])
def password_recovery():
    form = recoveryForm()
    form.email.render_kw = {'class': 'search-input'}

    if form.validate_on_submit():
        if dbase.getUsersE(form.email.data) != (False, False):

            msg = Message(subject='Verification code MFK Stars', sender='MFKStars@gmail.com',
                          recipients=[form.email.data])
            otp = randint(000000, 999999)
            print(otp)
            msg.body = 'MFK Stars. Код подтверждения: ' + str(otp)
            mail.send(msg)

            session['recovery_email'] = form.email.data
            session['recovery_email_code'] = otp

            flash("На вашу почту был выслан код подтверждения", "success")
            return redirect(url_for('verify_recovery'))
        else:
            flash("Пользователь с такой почтой не найден", "error")
            return redirect(url_for('login'))
    return render_template('password_recovery.html', form=form)


@app.route('/verify', methods=["POST", "GET"])
def verify():
    form_code = ValidateForm()
    form_code.email_code.render_kw = {'class': 'search-input'}

    email = session.get('email')
    my_mail = email[:3] + "@" * len(email[3:])

    otp = session.get("otp")

    if form_code.validate_on_submit():
        user_otp = form_code.email_code.data
        if str(otp) == user_otp:
            flash("Email подтвержден", "success")

            hash = session.get('password')
            res = dbase.addUser(session.get('name'), session.get('email'), hash)
            if res:
                flash("Вы успешно зарегистрированы", "success")
                return redirect(url_for('login'))
            else:
                flash("Ошибка при добавлении в БД", "error")
        else:
            flash("Неверный код подтверждения", "error")
            print(otp)
            print(user_otp)

    return render_template('verify.html', form_code=form_code, my_mail=my_mail)


@app.route('/verify_recovery', methods=["POST", "GET"])
def verify_recovery():
    form = ValidateForm()
    form.email_code.render_kw = {'class': 'search-input'}

    email = session.get('recovery_email')
    my_mail = email[:3] + "@" * len(email[3:])

    otp = session.get("recovery_email_code")

    if form.validate_on_submit():

        user_otp = form.email_code.data

        if otp == user_otp:
            flash("Email подтвержден", "success")
            return redirect(url_for('new_psw'))
        else:
            flash("Неверный код подтверждения", "error")

    return render_template('verify_recovery.html', form=form, my_mail=my_mail)


@app.route('/new_psw', methods=["POST", "GET"])
def new_psw():
    form = new_psw_form()
    form.psw.render_kw = {'class': 'search-input'}
    form.psw2.render_kw = {'class': 'search-input'}

    email = session.get('recovery_email')

    if form.validate_on_submit():

        hash = generate_password_hash(form.psw.data)
        res = dbase.updatePsw(email, hash)
        if res:
            flash("Пароль успешно изменен", "success")
            return redirect(url_for('login'))
        else:
            flash("Ошибка при добавлении в БД", "error")
    return render_template('new_psw.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))


@app.route('/profile', methods=["POST", "GET"])
@login_required
def profile():
    form = commentDelForm()
    if form.validate_on_submit():

            mfk_title = request.form.get('mfk_title')
            mfk_name = request.form.get('mfk_name')
            if mfk_title != "Вы еще не ставили оценки":
                dbase.delComment(mfk_title, current_user.getName())

                if dbase.getUserCommentsNumb(current_user.getName()) != (False, False):
                    comments_numb = len(dbase.getUserCommentsNumb(current_user.getName()))
                else:
                    comments_numb = 0
                dbase.updateUserCommentsNumb(comments_numb, current_user.getEmail())

                score_list = dbase.getMfkScore(mfk_name)
                mfk_score = 0
                len_score_list = 0

                for i in score_list:
                    for j in i:
                        mfk_score += int(j)
                        len_score_list += 1

                if len_score_list == 0:
                    mfk_score = 0
                else:
                    mfk_score = round(mfk_score / len_score_list)

                dbase.updateMfkScore(mfk_name, mfk_score)

                score_numb = dbase.getMfkScoreNumb(mfk_name)
                for i in score_numb:
                    for j in i:
                        score_numb = j

                if (score_numb == None) or (score_numb == 0):
                    score_numb = 0
                else:
                    score_numb -= 1
                dbase.updateMfkScoreNumb(mfk_name, score_numb)

    your_comments = dbase.getUserCommentsNumb(current_user.getName())
    if your_comments == (False, False):
        class Person:
            def __init__(self, name):
                self.name = name

        your_comments = [Person("")]
        your_comments[0].score = ""
        your_comments[0].mfkname = "Вы еще не ставили оценки"
        your_comments[0].mfktitle = "Вы еще не ставили оценки"

    if dbase.getUserCommentsNumb(current_user.getName()) != (False, False):
        comments_numb = len(dbase.getUserCommentsNumb(current_user.getName()))
    else:
        comments_numb = 0
    dbase.updateUserCommentsNumb(comments_numb, current_user.getEmail())

    return render_template('profile.html', menu=menu, your_comments=your_comments, comments_numb=comments_numb, form=form)


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id, dbase)


@app.route("/contacts", methods=["POST", "GET"])
@login_required
def contacts():
    form = ContactForm()
    form.text.render_kw = {'style': 'height: 200px; width: 350px; ', 'class': 'search-input'}
    form.recaptcha.render_kw = {'style': 'box-sizing: border-box; display: block; max-width: 100%;'}
    if form.validate_on_submit():
        msg = Message(subject='Отзывы и пожелания', sender='MFKStars@gmail.com', recipients=['nagel20@yandex.ru'])

        m = ''
        m += str(current_user.getName())
        m += '<br>/n\\n'
        m += str(current_user.getEmail())
        m += '<br>/n\\n'
        m = str(form.text.data)

        msg.body = m

        mail.send(msg)
        flash("Cообщение отправлено", "success")
        return redirect('contacts')
    return render_template('contacts.html', my_text='Обратная связь', menu=menu, form=form)


if __name__ == "__main__":
    app.run(debug=True)
