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

# from MFKStars.backend_dict.auth.UserLogin import UserLogin
from forms import LoginForm, RegisterForm, starsForm, ValidateForm, recoveryForm, DEVLoginForm
from forms import PollForm1, ContactForm, searchForm, commentDelForm, new_psw_form, CommentForm
from Models import db, Comments, Mfk, Users

from admin.admin import admin
from postview.postview import postView
from auth.auth import auth

#TODO вкладка авторизация ведет на пустую страницу 
#TODO importы почисть
#TODO use SQLAlchemy
#TODO move or del dev login to admin
#TODO Userlogin fix
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
    {"title": "Авторизация", "url": "/auth/login"},
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
    #TODO Userlogin fix
    # userlogin = UserLogin().create(user)
    # login_user(userlogin, remember=0)
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



##############################################################################
# Mfk pages
##############################################################################

app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(postView, url_prefix='/postView')
app.register_blueprint(auth, url_prefix='/auth')

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


#TODO add different causes of mark
@app.route("/poll", methods=['GET', 'POST'])
@login_required
def poll():
    form = PollForm1()
    form.interested.render_kw = {'style': '', 'class': ''}

    if form.validate_on_submit():
        if form.interested.data == 'st1' and not form.other2.data:
            flash('Пожалуйста, укажите причину для выбора "Другое"', category='error')

    return render_template('poll.html', my_text='Опросговна', form=form)


@app.route("/contacts", methods=["POST", "GET"])
@login_required
def contacts():
    form = ContactForm()
    form.text.render_kw = {'style': 'height: 200px; width: 350px; ', 'class': 'search-input'}
    # TODO re comment recaptcha
    # form.recaptcha.render_kw = {'style': 'box-sizing: border-box; display: block; max-width: 100%;'}
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
