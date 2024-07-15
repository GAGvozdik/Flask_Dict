import sqlite3
from flask import Blueprint, render_template, url_for, redirect, session, request, flash, g
from admin.adminForms import AdminLoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from UserLogin import UserLogin
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import current_app

admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')

#TODO logout redirect to empty page

menu = [
    # вылетало при входе в админку
    # {'url': '/dict', 'title': 'На главную'},
        {'url': '.index', 'title': 'Панель'},
        {'url': '.listusers', 'title': 'Список пользователей'},
        {'url': '.listpubs', 'title': 'Список статей'},
        {'url': '.logout', 'title': 'Выйти'}]

def isLogged():
    return True if session.get('admin_logged') else False

def login_admin():
    session['admin_logged'] = True

def logout_admin():
    session.pop('admin_logged', None)


db = None
@admin.before_request
def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    global db
    db = g.get('link_db')

@admin.teardown_request
def teardown_request(request):
    global db
    db = None
    return request

@admin.route('/')
@admin.route('/base_admin')
@admin.route('/index')
def index():
    if not isLogged():
        return redirect(url_for('.login'))

    return render_template('admin/index.html', menu=menu, title='Админ-панель')

@admin.route('/login', methods=["POST", "GET"])
def login():
    if isLogged():
        return redirect(url_for('.index'))


    form = AdminLoginForm()
    form.psw.render_kw = {'class': 'search-input'}
    form.email.render_kw = {'class': 'search-input'}

    if form.validate_on_submit():
        if form.email.data == 'admin' and form.psw.data == '12345':

            login_admin()
            
            return redirect(url_for('.index'))

        flash("Неверная пара логин/пароль", "error")
    return render_template("login.html", menu=menu, my_text="Авторизация", form=form)


@admin.route('/logout', methods=["POST", "GET"])
def logout():
    if not isLogged():
        return redirect(url_for('.login'))

    logout_admin()

    return redirect(url_for('.logout'))

@admin.route('/list-pubs')
def listpubs():
    if not isLogged():
        return redirect(url_for('.login'))

    list = []
    if db:
        try:
            cur = db.cursor()
            cur.execute(f"SELECT title, text, url FROM posts")
            list = cur.fetchall()
        except sqlite3.Error as e:
            print("Ошибка получения статей из БД " + str(e))

    return render_template('admin/listpubs.html', title='Список статей', menu=menu, list=list)

@admin.route('/list-users')
def listusers():
    if not isLogged():
        return redirect(url_for('.login'))

    list = []
    if db:
        try:
            cur = db.cursor()
            cur.execute(f"SELECT name, email FROM users ORDER BY time DESC")
            list = cur.fetchall()
        except sqlite3.Error as e:
            print("Ошибка получения статей из БД " + str(e))

    return render_template('admin/listusers.html', title='Список пользователей', menu=menu, list=list)