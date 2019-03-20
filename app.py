import sqlite3
from flask import Flask, render_template, redirect,\
    session, jsonify, make_response, request
import os.path
from datetime import datetime

from Forms import LoginForm, AddNoteForm
from Models import UserModel, NoteModel
from DB import DB

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
DATABASE = 'jfe.db'


@app.route('/login', methods=['POST', 'GET'])
def login():
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


@app.route('/notes', methods=['GET', 'POST'])
def notes():
    if 'username' not in session:
        return redirect('/login')
    form = AddNoteForm()
    nm = NoteModel(db.get_connection())
    notes = nm.get_all(session['user_id'])
    if form.validate_on_submit():
        content = form.content.data
        print(content)
        nm.insert(content, session['user_id'])
        return redirect("/notes")
    print(notes)
    return render_template('notes.html', username=session['username'],
                           notes=notes, title="Заметки", form=form)


if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        db = DB(DATABASE)
        um = UserModel(db.get_connection())
        um.init_table()
        um.insert('test1', 'test1')
        um.insert('test2', 'test2')
        nm = NoteModel(db.get_connection())
        nm.init_table()
    else:
        db = DB(DATABASE)
    app.run(port=8080, host='127.0.0.1')
