from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, SelectField, ValidationError
from wtforms.validators import DataRequired, InputRequired, EqualTo

users = ['test1', 'test2', 'admin']


def add_user(user_list):
    for user in user_list:
        if user not in users:
            users.append(user)


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(message='Это обязательное поле')])
    password = PasswordField('Пароль', validators=[DataRequired(message='Это обязательное поле')])
    submit = SubmitField('Войти')


class AddNoteForm(FlaskForm):
    content = TextAreaField('Текст', validators=[DataRequired(message='Это обязательное поле')])
    submit = SubmitField('Добавить')


def login_unique_check(form, field):
    if field.data in users:
        raise ValidationError('Пользователь с таким логином уже существует')


class RegistrationForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(message='Это обязательное поле'),
                                                login_unique_check])
    password = PasswordField('Пароль', validators=[InputRequired(message='Это обязательное поле'),
                                                   EqualTo('confirm',
                                                           message='Пароли должны совпадать')])
    confirm = PasswordField('Повторите пароль', validators=[DataRequired(message='Это обязательное поле')])
    submit = SubmitField('Зарегистрироваться')


class ParamForm(FlaskForm):
    search_words = StringField('Ключевые слова для поиска', validators=[DataRequired(message='Это обязательное поле')])
    search_area = StringField('Населенный пункт', validators=[DataRequired(message='Это обязательное поле')])
    submit = SubmitField('Сохранить настройки')


class MoreButton(FlaskForm):
    submit = SubmitField('Найти еще')
