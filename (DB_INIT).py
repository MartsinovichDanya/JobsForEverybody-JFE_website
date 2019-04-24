from Models import UserModel, NoteModel, ParamModel, VacModel
from DB import DB


def init_jfe_db():
    db = DB('jfe.db')
    um = UserModel(db.get_connection())
    um.init_table()
    um.insert('test1', 'test1', '-')
    um.insert('test2', 'test2', '-')
    um.insert('admin', 'admin', '-', True)
    nm = NoteModel(db.get_connection())
    nm.init_table()
    pm = ParamModel(db.get_connection())
    pm.init_table()
    vm = VacModel(db.get_connection())
    vm.init_table()


def init_alice_jfe_db():
    pass


init_jfe_db()
init_alice_jfe_db()
