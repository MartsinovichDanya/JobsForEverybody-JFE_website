import hashlib


class UserModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             user_name VARCHAR(50),
                             password_hash VARCHAR(128),
                             admin BOOL,
                             email VARCHAR(100)
                             )''')
        cursor.close()
        self.connection.commit()

    def make_admin(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''UPDATE users SET 
                            admin = ?
                            WHERE id = ?''', (True, str(user_id)))
        cursor.close()
        self.connection.commit()

    def insert(self, user_name, password, email, admin=False):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users 
                          (user_name, password_hash, admin, email) 
                          VALUES (?,?,?,?)''',
                       (user_name, hashlib.md5(bytes(password, encoding='utf8')).hexdigest(), admin, email))
        cursor.close()
        self.connection.commit()

    def get(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (str(user_id)))
        row = cursor.fetchone()
        return row

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return rows

    def delete(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM users WHERE id = ?''', (str(user_id)))
        cursor.close()
        self.connection.commit()

    def exists(self, user_name, password):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = ? AND password_hash = ?",
                       (user_name, hashlib.md5(bytes(password, encoding='utf8')).hexdigest()))
        row = cursor.fetchone()
        return (True, row[0], row[3]) if row else (False,)


class AliceUserModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             name VARCHAR(50),
                             device_id VARCHAR(128),
                             email VARCHAR(100)
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, name, device_id, email):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users 
                          (name, device_id, email) 
                          VALUES (?,?,?)''',
                       (name, device_id, email))
        cursor.close()
        self.connection.commit()

    def get(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (str(user_id)))
        row = cursor.fetchone()
        return row

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return rows

    def delete(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM users WHERE id = ?''', (str(user_id)))
        cursor.close()
        self.connection.commit()

    def exists(self, device_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE device_id = ?",
                       (device_id,))
        row = cursor.fetchone()
        return (True, row[0], row[2]) if row else (False,)


class NoteModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS notes 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             content VARCHAR(1000),
                             user_id INTEGER
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, content, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO notes 
                          (content, user_id) 
                          VALUES (?,?)''', (content, str(user_id)))
        cursor.close()
        self.connection.commit()

    def get(self, note_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM notes WHERE id = ?", (str(note_id)))
        row = cursor.fetchone()
        return row

    def get_all(self, user_id=None):
        cursor = self.connection.cursor()
        if user_id:
            cursor.execute("SELECT * FROM notes WHERE user_id = ?",
                           (str(user_id)))
        else:
            cursor.execute("SELECT * FROM notes")
        rows = cursor.fetchall()
        return rows

    def delete(self, note_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM notes WHERE id = ?''', (str(note_id),))
        cursor.close()
        self.connection.commit()

    def delete_for_user(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM notes WHERE user_id = ?''', (str(user_id)))
        cursor.close()
        self.connection.commit()

    def get_count(self, user_id=None):
        cursor = self.connection.cursor()
        if user_id:
            cursor.execute("SELECT COUNT(*) FROM notes WHERE user_id = ?",
                           (str(user_id)))
        else:
            cursor.execute("SELECT COUNT(*) FROM notes")
        rows = cursor.fetchone()
        return rows[0]


class ParamModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS params 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             search_words VARCHAR(1000),
                             area VARCHAR(1000),
                             user_id INTEGER
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, search_words, area, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO params 
                          (search_words, area, user_id) 
                          VALUES (?,?,?)''', (search_words, area, str(user_id)))
        cursor.close()
        self.connection.commit()

    def get(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM params WHERE user_id = ?", (str(user_id)))
        row = cursor.fetchone()
        return row

    def update(self, search_words, area, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''UPDATE params SET 
                            search_words = ?,
                            area = ?
                            WHERE user_id = ?''', (search_words, area, str(user_id)))
        cursor.close()
        self.connection.commit()

    def delete_for_user(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM params WHERE user_id = ?''', (str(user_id)))
        cursor.close()
        self.connection.commit()


class VacModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS vacancies 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             vac_id INTEGER, 
                             name VARCHAR(100),
                             emp_name VARCHAR(100),
                             date VARCHAR(20),
                             link VARCHAR(1000),
                             salary VARCHAR(50),
                             user_id INTEGER
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, vac_id, name, emp_name, date, link, salary, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO vacancies 
                          (vac_id, name, emp_name, date, link, salary, user_id) 
                          VALUES (?,?,?,?,?,?,?)''', (vac_id, name, emp_name, date, link, salary, str(user_id)))
        cursor.close()
        self.connection.commit()

    def get_all(self, user_id=None):
        cursor = self.connection.cursor()
        if user_id:
            cursor.execute("SELECT * FROM vacancies WHERE user_id = ?",
                           (str(user_id)))
        else:
            cursor.execute("SELECT * FROM vacancies")
        rows = cursor.fetchall()
        return rows

    def delete(self, vac_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM vacancies WHERE id = ?''', (str(vac_id),))
        cursor.close()
        self.connection.commit()

    def delete_for_user(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM vacancies WHERE user_id = ?''', (str(user_id)))
        cursor.close()
        self.connection.commit()

    def get_count(self, user_id=None):
        cursor = self.connection.cursor()
        if user_id:
            cursor.execute("SELECT COUNT(*) FROM vacancies WHERE user_id = ?",
                           (str(user_id)))
        else:
            cursor.execute("SELECT COUNT(*) FROM vacancies")
        rows = cursor.fetchone()
        return rows[0]
