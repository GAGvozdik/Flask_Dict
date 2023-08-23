from flask_wtf import FlaskForm, RecaptchaField
import flask
from wtforms import StringField, SubmitField, BooleanField, PasswordField, SelectField, RadioField, Label
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Email, Length, EqualTo, InputRequired
import email_validator


class LoginForm(FlaskForm):
    email = StringField("Email: ", validators=[Email("Некорректный email")])
    psw = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=4, max=100,
                                                                       message="Пароль должен быть от 4 до 100 символов")])
    remember = BooleanField("Запомнить", default=False)
    recaptcha = RecaptchaField()
    submit = SubmitField("Войти")


class RegisterForm(FlaskForm):
    name = StringField("Имя: ", validators=[Length(min=4, max=100, message="Имя должно быть от 4 до 100 символов")])
    email = StringField("Email: ", validators=[Email("Некорректный email")])
    psw = PasswordField("Пароль: ", validators=[DataRequired(),
                                                Length(min=4, max=100,
                                                       message="Пароль должен быть от 4 до 100 символов")])

    psw2 = PasswordField("Повтор пароля: ", validators=[DataRequired(), EqualTo('psw', message="Пароли не совпадают")])
    recaptcha = RecaptchaField()
    submit = SubmitField("Регистрация")

class ValidateForm(FlaskForm):
    email_code = StringField("Введите код подтверждения: ")
    recaptcha = RecaptchaField()
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
    # text = StringField(u'Text', widget=TextArea())
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
    recaptcha = RecaptchaField()
    submit = SubmitField("Войти")



