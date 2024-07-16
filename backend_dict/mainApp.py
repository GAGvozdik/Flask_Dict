from random import randint
import sqlite3
import os
import numpy as np
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from flask import Flask, render_template, request, g, url_for, abort, flash, session, redirect, make_response
from flask_mail import Mail, Message
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from UserLogin import UserLogin
from forms import LoginForm, RegisterForm, starsForm, ValidateForm, recoveryForm, DEVLoginForm
from forms import PollForm1, ContactForm, searchForm, commentDelForm, new_psw_form, CommentForm
from Models import db, Comments, Mfk, Users

from admin.admin import admin
from postview.postview import postView

#TODO вкладка авторизация ведет на пустую страницу 
#TODO importы почисть
#TODO use SQLAlchemy
#TODO move or del dev login to admin
#TODO 

app = Flask(__name__)
bootstrap = Bootstrap(app)
# Bootstrap(app)
# config

#TODO use SQLAlchemy
# DATABASE = '/tmp/flsite.db'
DEBUG = True

USERNAME = 'admin'
PASSWORD = "6LeRRc0vdht&%4^46yhhfqlBBl5b0kODY_qQ"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///MainDB.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)  

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

app.config.from_object(__name__)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success"

menu = [
    {"title": "МФК", "url": "/postView"},
    # del dev 
    {"title": "DEV", "url": "/"},
    {"title": "Авторизация", "url": "/login"},
    {"title": "Подобрать МФК", "url": "/question"},
    {"title": "Обратная связь", "url": "/contacts"},
    {"title": "Опрос", "url": "/poll"},
    {"title": "О нас", "url": "/about"},
    {"title": "admin", "url": "/admin"}]

max_commetns_numb = 7



def create_db():
    db.create_all()

@app.route('/loginDEV', methods=["POST", "GET"])
def loginDEV():
    user = Users.getUserByEmail('qwer@gmail.com')
    userlogin = UserLogin().create(user)
    login_user(userlogin, remember=0)
    print('lodev')
    return redirect(url_for('profile'))

# def rewrite_db():
#     add_mfk_to_db()

@app.context_processor
def inject_menu():
    return {'menu': menu}

#TODO clear methods=["POST", "GET"]
@app.route('/', methods=["POST", "GET"])
def index():

    loginform = DEVLoginForm()

    if loginform.validate_on_submit():
        return redirect(url_for('loginDEV'))

    return render_template('index.html', my_text='МФК', menu=menu, loginform=loginform)

app.register_blueprint(admin, url_prefix='/admin')

##############################################################################
# Mfk pages
##############################################################################

app.register_blueprint(postView, url_prefix='/postView')

#################################################################################
# profile --
#################################################################################

@app.route('/profile', methods=["POST", "GET"])
@login_required
def profile():
    form = commentDelForm()
    if form.validate_on_submit():

        mfk_title = request.form.get('mfk_title')
        mfk_name = request.form.get('mfk_name')

        #TODO use SQLAlchemy
        if mfk_title != "Вы еще не ставили оценки":

            Comments.delComment(mfk_title, current_user.getName())

            score_list = Comments.getMfkScore(mfk_name)
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

            #TODO сделать id по name 
            Mfk.updateMfkScore(mfk_name, mfk_score)



            if Mfk.getMfkScoreNumb(mfk_name) > 0:
                Mfk.updateMfkScoreNumb(mfk_name, Mfk.getMfkScoreNumb(mfk_name) - 1)

    #TODO use SQLAlchemy
    your_comments = Comments.getUserCommentsNumb(current_user.getName())
    if your_comments == (False, False):
        class Person:
            def __init__(self, name):
                self.name = name

        your_comments = [Person("")]
        your_comments[0].score = ""
        your_comments[0].mfkname = "Вы еще не ставили оценки"
        your_comments[0].mfktitle = "Вы еще не ставили оценки"

    if Comments.getUserCommentsNumb(current_user.getName()) != (False, False):
        comments_numb = len(Comments.getUserCommentsNumb(current_user.getName()))
    else:
        comments_numb = 0
    Users.updateUserCommentsNumb(comments_numb, current_user.getEmail())

    return render_template('profile.html', menu=menu, your_comments=your_comments, comments_numb=comments_numb, form=form)



#################################################################################
# comments/marks --
#################################################################################

#TODO add different causes of mark
@app.route("/poll", methods=['GET', 'POST'])
def poll():
    form = PollForm1()
    form.interested.render_kw = {'style': '', 'class': ''}

    if form.validate_on_submit():
        if form.interested.data == 'st1' and not form.other2.data:
            flash('Пожалуйста, укажите причину для выбора "Другое"', category='error')

    return render_template('poll.html', my_text='Опросговна', menu=menu, form=form)


# TODO комментарии добавляются на страницу мфк но не добавляются к пользователю на страницу пользователя
@app.route('/addComment/<alias>', methods=['GET', 'POST'])
def addComment(alias):

    #TODO use SQLAlchemy 
    mfk = Mfk.getMfk(alias)
    if not mfk:
        abort(404)

    form = starsForm()
    comments_numb = 0
    max_comments_numb = 7  # Максимальное количество комментариев
    current_user_name = current_user.getName()  # Замените на логин текущего пользователя

    # Проверяем, есть ли комментарии пользователя под этой статьей
    comments = Comments.getComment(alias)
    if comments:
        comments_numb = len(comments)
        for comment in comments:
            if comment.username == current_user_name:
                flash('Комментарий уже добавлен','error')
                return redirect(url_for('postView.showMfk', alias=alias))

    if form.validate_on_submit():
        # Проверяем, не превышено ли максимальное число комментариев
        if comments_numb < max_comments_numb:
            # Извлекаем значения из формы
            score = form.score.data
            reason = form.reason.data

            # Преобразуем score в числовое значение
            score_value = int(score[2:])  # Извлекаем число из 'st5', 'st4', etc.
            
            mark_score = Mfk.getMfkScoreNumb(alias) + 1

            res = Comments.addComment(
                current_user_name,
                alias,  # Используем alias из URL
                score_value,  # Передаем числовую оценку
                mfk.getMfkName(alias),  #TODO change 2 mfktitle  
                mark_score,
                reason
            )

            Mfk.updateMfkScoreNumb(alias, Mfk.getMfkScoreNumb(alias) + 1)


            score_list = Comments.getMfkScore(alias)
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

            #TODO сделать id по name 
            Mfk.updateMfkScore(alias, mfk_score)

            if res:
                flash('Комментарий добавлен','sucess')
            else:
                flash('Ошибка добавления комментария','error')
        else:
            flash('Вы достигли лимита коментариев. Удалите комментарий, чтобы добавить новый', category='error')

    return render_template('comments.html', menu=menu, mfk=mfk, alias=alias, my_comments=Comments.getComment(alias), form=form)

#################################################################################
# login ++
#################################################################################


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    form = LoginForm()
    form.psw.render_kw = {'class': 'search-input'}
    form.email.render_kw = {'class': 'search-input'}

    if form.validate_on_submit():
        
        #TODO use SQLAlchemyd
        user = Users.getUserByEmail(form.email.data)

        if user and check_password_hash(user.psw, form.psw.data):
            userlogin = UserLogin().create(user)
            rm = form.remember.data
            login_user(userlogin, remember=rm)
            return redirect(request.args.get("next") or url_for("profile"))

        flash("Неверная пара логин/пароль", "error")
    return render_template("login.html", menu=menu, my_text="Авторизация", form=form)


@login_manager.user_loader
def load_user(user_id):

    #TODO use SQLAlchemy
    return UserLogin().fromDB(user_id, db)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))


#################################################################################
# registr ++
#################################################################################


@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    form.name.render_kw = {'class': 'search-input'}
    form.psw.render_kw = {'class': 'search-input'}
    form.psw2.render_kw = {'class': 'search-input'}
    form.email.render_kw = {'class': 'search-input'}

    if form.validate_on_submit():
        #TODO use SQLAlchemy
        if Users.getUsersE(form.email.data) == (False, False):
            if Users.getUsersN(form.name.data) == (False, False):
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
        pass

    return render_template("register.html", menu=menu, my_text="Регистрация", form=form)


#################################################################################
# psw recovery + veryfy ++
#################################################################################

@app.route('/password_recovery', methods=["POST", "GET"])
def password_recovery():
    form = recoveryForm()
    form.email.render_kw = {'class': 'search-input'}

    if form.validate_on_submit():
        #TODO use SQLAlchemy
        if Users.getUsersE(form.email.data) != (False, False):

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
            
            #TODO use SQLAlchemy
            res = Users.addUser(session.get('name'), session.get('email'), hash)
            if res:
                flash("Вы успешно зарегистрированы", "success")
                return redirect(url_for('login'))
            else:
                flash("Ошибка при добавлении в БД", "error")

        else:
            flash("Неверный код подтверждения", "error")

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
        print(otp)

        if str(otp) == user_otp:
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
        
        #TODO use SQLAlchemy
        res = Users.updatePsw(email, hash)
        if res:
            flash("Пароль успешно изменен", "success")
            return redirect(url_for('login'))
        else:
            flash("Ошибка при добавлении в БД", "error")

    return render_template('new_psw.html', form=form)


#################################################################################
# other ++
#################################################################################



@app.route("/about")
def about():
    return render_template('about.html', my_text='О нас', menu=menu)


@app.route("/question", methods=['GET', 'POST'])
@login_required
def question():
    return render_template('question.html', menu=menu, email=current_user.getEmail())


@app.errorhandler(404)
def pageNotFount(error):
    return render_template('page404.html', my_text="Страница не найдена", menu=menu), 404


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
