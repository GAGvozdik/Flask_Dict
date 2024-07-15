from flask_wtf import FlaskForm, RecaptchaField
import flask
from wtforms import StringField, SubmitField, BooleanField, PasswordField, SelectField, RadioField, Label, HiddenField
from wtforms.widgets import TextArea, Input
from wtforms.validators import DataRequired, Email, Length, EqualTo, InputRequired, Optional
import email_validator
#TODO re comment captcha

class LoginForm(FlaskForm):
    email = StringField("Email: ", validators=[Email("Некорректный email")])
    psw = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=8, max=100,
                                                                       message="Пароль должен быть от 8 до 100 символов")])
    remember = BooleanField("Запомнить", default=False)
    # recaptcha = RecaptchaField()
    submit = SubmitField("Войти")


class RegisterForm(FlaskForm):
    name = StringField("Имя: ", validators=[Length(min=4, max=100, message="Имя должно быть от 4 до 100 символов")])
    email = StringField("Email: ", validators=[Email("Некорректный email")])
    psw = PasswordField("Пароль: ", validators=[DataRequired(),
                                                Length(min=4, max=100,
                                                       message="Пароль должен быть от 4 до 100 символов")])

    psw2 = PasswordField("Повтор пароля: ", validators=[DataRequired(), EqualTo('psw', message="Пароли не совпадают")])

    submit = SubmitField("Регистрация")

class ValidateForm(FlaskForm):
    email_code = StringField("Введите код подтверждения: ")
    # recaptcha = RecaptchaField()
    submit = SubmitField("Подтвердить")

class recoveryForm(FlaskForm):
    email = StringField("Email: ", validators=[Email("Некорректный email")])

    submit = SubmitField("Подтвердить")


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

class ContactForm(FlaskForm):
    text = StringField(u'Text', widget=TextArea())
    # recaptcha = RecaptchaField()
    submit = SubmitField("Войти")


class searchForm(FlaskForm):
    search = StringField(u'Text')
    submit = SubmitField("Найти")

class commentDelForm(FlaskForm):
    submit = SubmitField("Удалить комментарий")

class PollForm1(FlaskForm):


    other1 = StringField("other1", validators=[Optional()])
    other2 = StringField("other2", validators=[Optional()])

    problems1 = remember = BooleanField("Да, сложно было выбрать среди большого количества вариантов", default=False)
    problems2 = remember = BooleanField("Да, сложно было успеть записаться на подходящий курс", default=False)
    problems3 = remember = BooleanField("Да, не нашел вовремя информацию, как и когда это сделать", default=False)
    problems4 = remember = BooleanField("Нет, никаких проблем не было", default=False)
    problems5 = remember = BooleanField('Other:', default=False)

    interested = RadioField('Stars', validators=[InputRequired()], choices=[
        ('st5', 'Да, это было бы удобнее'),
        ('st4', 'Возможно, попробовал бы'),
        ('st3', 'Нет, меня всё устраивает'),
        ('st2', 'Нет, никаких проблем не было'),
        ('st1', 'Other:')
    ])
    submit = SubmitField("Отправить")



