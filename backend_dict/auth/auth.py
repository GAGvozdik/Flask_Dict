import sqlite3
from flask import Blueprint, render_template, url_for, redirect, session, request, flash, g, abort
from admin.adminForms import AdminLoginForm
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import current_app
from flask_mail import Mail, Message
from random import randint

#TODO статьи не отображаются, если их брать из моделей блюпринта
# from postview.postViewModels import Comments, Mfk
from Models import Comments, Mfk, Users
from auth.authForms import ValidateForm, recoveryForm, RegisterForm, LoginForm, new_psw_form

from auth.UserLogin import UserLogin

# from mainApp import login_manager, mail



userAuth = Blueprint('userAuth', __name__, template_folder='templates', static_folder='.static')

# mail config
mail = Mail(userAuth)

userAuth.config["MAIL_SERVER"] = 'smtp.gmail.com'
userAuth.config["MAIL_PORT"] = 465
userAuth.config["MAIL_USERNAME"] = 'gvozdikgeorge@gmail.com'
userAuth.config['MAIL_PASSWORD'] = 'mkdwvebgqqrmxkgt'
userAuth.config['MAIL_USE_TLS'] = False
userAuth.config['MAIL_USE_SSL'] = True
userAuth.config['SECRET_KEY'] = os.urandom(50).hex()
userAuth.config['RECAPTCHA_PUBLIC_KEY'] = "6LeRRc0nAAAAAHncCrhRoeYqSqlBBl5b0kODY_qQ"
userAuth.config['RECAPTCHA_PRIVATE_KEY'] = "6LeRRc0nAAAAAK6u6lMesUFuM-rnzQLWKFKI9xEV"

mail = Mail(userAuth)

login_manager = LoginManager(userAuth)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success"


# @postView.route("/", methods=['GET', 'POST'])
# def dict():

#     form = searchForm()
#     form.search.render_kw = {'placeholder': 'Введите текст'}
    
#     if form.validate_on_submit():

#         #TODO use SQLAlchemy
#         mfk_table = Mfk.getSearchMfk(form.search.data)

#         if mfk_table == (False, False):
#             flash('МФК с таким описанием не найдено. Поменяйте формулировку', category='error')
#             return redirect(url_for('postView.dict'))
#         else:

#             return render_template('postview/posts.html', my_text='МФК', mfk_table=mfk_table, form=form)



#################################################################################
# login ++
#################################################################################


@userAuth.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_userAuthenticated:
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
    return render_template("userAuth/login.html", my_text="Авторизация", form=form)


@login_manager.user_loader
def load_user(user_id):

    #TODO use SQLAlchemy
    return Users.getUser(user_id)


@userAuth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('.login'))


#################################################################################
# registr ++
#################################################################################


@userAuth.route("/register", methods=["POST", "GET"])
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
                return redirect(url_for('.verify'))
            else:
                flash("Пользователь с таким именем уже зарегистрирован", "error")
        else:
            flash("Пользователь с такой почтой уже зарегистрирован", "error")
        pass

    return render_template("userAuth/register.html", my_text="Регистрация", form=form)


#################################################################################
# psw recovery + veryfy ++
#################################################################################

@userAuth.route('/password_recovery', methods=["POST", "GET"])
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
            return redirect(url_for('.verify_recovery'))
        else:
            flash("Пользователь с такой почтой не найден", "error")
            return redirect(url_for('.login'))


    return render_template('userAuth/password_recovery.html', form=form)


@userAuth.route('/verify', methods=["POST", "GET"])
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
                return redirect(url_for('.login'))
            else:
                flash("Ошибка при добавлении в БД", "error")

        else:
            flash("Неверный код подтверждения", "error")

    return render_template('userAuth/verify.html', form_code=form_code, my_mail=my_mail)


@userAuth.route('/verify_recovery', methods=["POST", "GET"])
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
            return redirect(url_for('.new_psw'))
        else:
            flash("Неверный код подтверждения", "error")

    return render_template('userAuth/verify_recovery.html', form=form, my_mail=my_mail)


@userAuth.route('/new_psw', methods=["POST", "GET"])
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
            return redirect(url_for('.login'))
        else:
            flash("Ошибка при добавлении в БД", "error")

    return render_template('userAuth/new_psw.html', form=form)

