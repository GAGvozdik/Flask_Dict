from flask_wtf import FlaskForm, RecaptchaField
import flask
from wtforms import StringField, SubmitField, BooleanField, PasswordField, SelectField, RadioField, Label, HiddenField
from wtforms.widgets import TextArea, Input
from wtforms.validators import DataRequired, Email, Length, EqualTo, InputRequired, Optional
import email_validator


class LoginForm(FlaskForm):
    email = StringField("Email: ")
    psw = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=4, max=100, message="Пароль должен быть от 8 до 100 символов")])
    remember = BooleanField("Запомнить", default=False)
    # recaptcha = RecaptchaField()
    submit = SubmitField("Войти")


class new_psw_form(FlaskForm):
    psw = PasswordField("Пароль: ", validators=[DataRequired(),
                                                Length(min=4, max=100,
                                                       message="Пароль должен быть от 4 до 100 символов")])
    psw2 = PasswordField("Повтор пароля: ", validators=[DataRequired(), EqualTo('psw', message="Пароли не совпадают")])

    submit = SubmitField("Подтвердить")


class starsForm(FlaskForm):

    score = RadioField('Stars', validators=[InputRequired()], choices=[
        ('st5', 'Excellent'),
        ('st4', 'Good'),
        ('st3', 'OK'),
        ('st2', 'Bad'),
        ('st1', 'Terrible')
    ])
    reason = SelectField('reason', choices=[
        ('not_helpful', 'Не помогло'),
        ('not_interesting', 'Не интересно'),
        ('not_relevant', 'Не соответствует')
    ])

    submit = SubmitField('Подтвердить')

class searchForm(FlaskForm):
    search = StringField(u'Text')
    submit = SubmitField("Найти")

class commentDelForm(FlaskForm):
    submit = SubmitField("Удалить комментарий")

