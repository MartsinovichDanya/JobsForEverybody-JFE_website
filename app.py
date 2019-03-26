import sqlite3
from flask import Flask, render_template, redirect,\
    session, jsonify, make_response, request
import os.path
from datetime import datetime

from Forms import add_user, LoginForm, AddNoteForm, RegistrationForm
from Models import UserModel, NoteModel
from DB import DB

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
DATABASE = 'jfe.db'


@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'username' in session:
        return redirect('/index')
    form = LoginForm()
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        user_model = UserModel(db.get_connection())
        exists = user_model.exists(user_name, password)
        if exists[0]:
            session['username'] = user_name
            session['user_id'] = exists[1]
            session['admin_privilege'] = exists[2]
            return redirect("/index")
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/login')


@app.route('/registration', methods=['POST', 'GET'])
def registration():
    if 'username' in session:
        return redirect('/index')
    form = RegistrationForm()
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        user_model = UserModel(db.get_connection())
        user_model.insert(user_name, password)
        add_user([el[1] for el in user_model.get_all()])
        return redirect('/login')
    return render_template('registration.html', title='Регистрация', form=form)


@app.route('/notes', methods=['GET', 'POST'])
def notes():
    if 'username' not in session:
        return redirect('/login')
    form = AddNoteForm()
    nm = NoteModel(db.get_connection())
    notes_list = list(reversed(nm.get_all(session['user_id'])))
    if form.validate_on_submit():
        content = form.content.data
        nm.insert(content, session['user_id'])
        return redirect("/notes")
    return render_template('notes.html', username=session['username'],
                           notes=notes_list, title="Заметки", form=form)


@app.route('/delete_note/<int:news_id>', methods=['GET'])
def delete_note(news_id):
    if 'username' not in session:
        return redirect('/login')
    nm = NoteModel(db.get_connection())
    nm.delete(news_id)
    return redirect("/notes")


if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        db = DB(DATABASE)
        um = UserModel(db.get_connection())
        um.init_table()
        um.insert('test1', 'test1')
        um.insert('test2', 'test2')
        users = [el[1] for el in um.get_all()]
        nm = NoteModel(db.get_connection())
        nm.init_table()
    else:
        db = DB(DATABASE)
        um = UserModel(db.get_connection())
        users = [el[1] for el in um.get_all()]
    app.run(port=8080, host='127.0.0.1')
