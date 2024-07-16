import sqlite3
from flask import Blueprint, render_template, url_for, redirect, session, request, flash, g, abort
from admin.adminForms import AdminLoginForm
from werkzeug.security import generate_password_hash, check_password_hash
# from MFKStars.backend_dict.auth.UserLogin import UserLogin
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import current_app


#TODO статьи не отображаются, если их брать из моделей блюпринта
# from postview.postViewModels import Comments, Mfk
from Models import Comments, Mfk
from postview.postViewForms import PollForm1, ContactForm, searchForm, commentDelForm, new_psw_form, starsForm

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



#################################################################################
# comments/marks --
#################################################################################


# TODO комментарии добавляются на страницу мфк но не добавляются к пользователю на страницу пользователя
@postView.route('/addComment/<alias>', methods=['GET', 'POST'])
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

    return render_template('postview/comments.html', mfk=mfk, alias=alias, my_comments=Comments.getComment(alias), form=form)
