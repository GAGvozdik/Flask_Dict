import sqlite3
from flask import Blueprint, render_template, url_for, redirect, session, request, flash, g, abort
from admin.adminForms import AdminLoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from UserLogin import UserLogin
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import current_app


#TODO статьи не отображаются, если их брать из моделей блюпринта
# from postview.postViewModels import Comments, Mfk
from Models import Comments, Mfk
from postview.postViewForms import PollForm1, ContactForm, searchForm, commentDelForm, new_psw_form

#TODO clear forms models css

postView = Blueprint('postView', __name__, template_folder='templates', static_folder='.static')


@postView.route("/", methods=['GET', 'POST'])
def dict():

    form = searchForm()
    form.search.render_kw = {'placeholder': 'Введите текст'}
    
    if form.validate_on_submit():

        #TODO use SQLAlchemy
        mfk_table = Mfk.getSearchMfk(form.search.data)

        if mfk_table == (False, False):
            flash('МФК с таким описанием не найдено. Поменяйте формулировку', category='error')
            return redirect(url_for('postView.dict'))
        else:

            return render_template('postview/posts.html', my_text='МФК', mfk_table=mfk_table, form=form)

    

    return render_template('postview/posts.html', my_text='МФК', mfk_table=Mfk.getMfkAnonce(), form=form, clearLink=url_for('.dict'))


@postView.route("/mfk/<alias>", methods=['GET', 'POST'])
def showMfk(alias):
    
    #TODO use SQLAlchemy
    mfk = Mfk.getMfk(alias)
    if not mfk:
        abort(404)

    return render_template('postview/mfk.html', mfk=mfk, alias=alias, my_comments=Comments.getComment(alias))