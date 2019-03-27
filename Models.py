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
                             admin BOOL
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, user_name, password):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users 
                          (user_name, password_hash, admin) 
                          VALUES (?,?,?)''',
                       (user_name, hashlib.md5(bytes(password, encoding='utf8')).hexdigest(), False))
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

    def exists(self, user_name, password):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = ? AND password_hash = ?",
                       (user_name, hashlib.md5(bytes(password, encoding='utf8')).hexdigest()))
        row = cursor.fetchone()
        return (True, row[0], row[-1]) if row else (False,)


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

    def get(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM notes WHERE id = ?", (str(news_id)))
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
        cursor.execute('''DELETE FROM notes WHERE id = ?''', (str(note_id)))
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
                          VALUES (?,?)''', (search_words, area, str(user_id)))
        cursor.close()
        self.connection.commit()

    def get(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM params WHERE user_id = ?", (str(user_id)))
        row = cursor.fetchone()
        return row


class VacModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS vacancies 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             name VARCHAR(100),
                             date VARCHAR(20),
                             link VARCHAR(1000),
                             user_id INTEGER
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, name, date, link, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO vacancies 
                          (name, date, link, user_id) 
                          VALUES (?,?,?,?)''', (name, date, link, str(user_id)))
        cursor.close()
        self.connection.commit()

    def get_all(self, user_id=None):
        cursor = self.connection.cursor()
        if user_id:
            cursor.execute("SELECT * FROM notes WHERE user_id = ?",
                           (str(user_id)))
        else:
            cursor.execute("SELECT * FROM notes")
        rows = cursor.fetchall()
        return rows

    def delete(self, vac_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM notes WHERE id = ?''', (str(vac_id)))
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
