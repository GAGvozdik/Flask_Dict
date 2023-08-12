from flask import Flask, render_template, request, url_for, abort, flash, session, redirect
import sqlite3
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = 'fdgdfgdfggfthfjgyfjy7f7i7jtfjyf7677786hfg6hfg6h7f'

menu = [
    {"name": "My dict", "url": "dict"},
    {"name": "Login", "url": "login"},
    {"name": "About", "url": "about"},
    {"name": "Contacts", "url": "contacts"}]


@app.route("/")
def index():
    return render_template('index.html', my_text='text', menu=menu)


@app.route("/dict")
def dict():
    return render_template('index.html', my_text='my dict', menu=menu)


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

    return render_template('contacts.html', my_text='CContacts', menu=menu)


@app.errorhandler(404)
def pageNotFount(error):
    return render_template('page404.html', title="Страница не найдена", menu=menu), 404


if __name__ == "__main__":
    app.run(debug=True)
