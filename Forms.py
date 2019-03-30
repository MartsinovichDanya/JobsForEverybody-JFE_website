from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, ValidationError
from wtforms.validators import DataRequired, InputRequired, EqualTo, AnyOf

import json

with open("regioni.json", "r") as f:
    VALID_AREAS = json.load(f).keys()


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(message='Это обязательное поле')])
    password = PasswordField('Пароль', validators=[DataRequired(message='Это обязательное поле')])
    submit = SubmitField('Войти')


class AddNoteForm(FlaskForm):
    content = TextAreaField('Текст', validators=[DataRequired(message='Это обязательное поле')])
    submit = SubmitField('Добавить')


def login_unique_check(form, field):
    with open("all_users.json", "r") as f:
        all_users = json.load(f)
    if field.data in all_users:
        raise ValidationError('Пользователь с таким логином уже существует')


def area_check(form, field):
    if field.data.lower() not in VALID_AREAS:
        raise ValidationError('Такого населенного пункта не существует')


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
    search_area = StringField('Населенный пункт', validators=[DataRequired(message='Это обязательное поле'),
                                                              area_check])
    submit = SubmitField('Сохранить настройки')


class MoreButton(FlaskForm):
    submit = SubmitField('Найти еще')
