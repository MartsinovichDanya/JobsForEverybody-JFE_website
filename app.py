from flask import Flask, render_template, redirect,\
    session
import os.path
import json

from Forms import LoginForm, AddNoteForm, RegistrationForm, ParamForm, MoreButton
from Models import UserModel, NoteModel, ParamModel, VacModel
from DB import DB
from API_kicker import get_vac

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
    user_model = UserModel(db.get_connection())
    all_users = [el[1] for el in user_model.get_all()]
    with open("all_users.json", "w", encoding='utf8') as f:
        json.dump(all_users, f)
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        user_model.insert(user_name, password)
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


@app.route('/delete_note/<int:note_id>', methods=['GET'])
def delete_note(note_id):
    if 'username' not in session:
        return redirect('/login')
    nm = NoteModel(db.get_connection())
    nm.delete(note_id)
    return redirect("/notes")


@app.route('/settings', methods=['POST', 'GET'])
def settings():
    if 'username' not in session:
        return redirect('/login')
    form = ParamForm()
    if form.validate_on_submit():
        search_words = form.search_words.data
        search_area = form.search_area.data
        pm = ParamModel(db.get_connection())
        if not pm.get(session['user_id']):
            pm.insert(search_words, search_area, session['user_id'])
        else:
            pm.update(search_words, search_area, session['user_id'])
        vm = VacModel(db.get_connection())
        vac_list = get_vac(search_words, search_area)
        for el in vac_list:
            vm.insert(*el, user_id=session['user_id'])
        return redirect('/index')
    return render_template('settings.html', title='Настройки поиска', form=form)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'username' not in session:
        return redirect('/login')
    form = MoreButton()
    pm = ParamModel(db.get_connection())
    if not pm.get(session['user_id']):
        return redirect('/settings')
    vm = VacModel(db.get_connection())
    vacancies_list = vm.get_all(session['user_id'])
    vacancies_list = sorted(vacancies_list, key=lambda n: -int(n[4].replace('-', '')))
    if form.validate_on_submit():
        params = pm.get(session['user_id'])
        vac_list = get_vac(params[1], params[2])
        exist_vac = [el[0] for el in vm.get_all(session['user_id'])]
        for el in vac_list:
            if int(el[0]) not in exist_vac:
                vm.insert(*el, user_id=session['user_id'])
        return redirect('/index')
    return render_template('index.html', username=session['username'],
                           vacancies=vacancies_list, title="Главная", form=form)


@app.route('/delete_vacancie/<int:vac_id>', methods=['GET'])
def delete_vacancie(vac_id):
    if 'username' not in session:
        return redirect('/login')
    vm = VacModel(db.get_connection())
    vm.delete(vac_id)
    return redirect("/index")


if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        db = DB(DATABASE)
        um = UserModel(db.get_connection())
        um.init_table()
        um.insert('test1', 'test1')
        um.insert('test2', 'test2')
        um.insert('admin', 'admin', True)
        nm = NoteModel(db.get_connection())
        nm.init_table()
        pm = ParamModel(db.get_connection())
        pm.init_table()
        vm = VacModel(db.get_connection())
        vm.init_table()
    else:
        db = DB(DATABASE)
    app.run(port=8080, host='127.0.0.1')
