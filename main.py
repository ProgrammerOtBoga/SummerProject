import sqlite3
from flask import Flask, request, render_template, session, redirect
import datetime
from dop import LoginForm
import os
from PIL import Image

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'


class DB:
    def __init__(self):
        conn = sqlite3.connect('news.db', check_same_thread=False)
        self.conn = conn

    def get_connection(self):
        return self.conn

    def __del__(self):
        self.conn.close()


class UsersModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             user_name VARCHAR(50),
                             password_hash VARCHAR(128)
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users 
                          (user_name, password_hash) 
                          VALUES (?,?)''', (user_name, password_hash))
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

    def exists(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = ? AND password_hash = ?",
                       (user_name, password_hash))
        row = cursor.fetchone()
        return (True, row[0]) if row else (False,)


class NewsModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS news 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             name VARCHAR(100),
                             content VARCHAR(1000),
                             ingrid VARCHAR(100),
                             photo VARCHAR(100),
                             hard INTEGER,
                             date,
                             user_id INTEGER
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, name, content, ingrid, photo, hard, user_id):
        cursor = self.connection.cursor()
        date = int(str(datetime.date.today()).split('-')[0]) * 364 + int(
            str(datetime.date.today()).split('-')[1]) * 30 + int(
            str(datetime.date.today()).split('-')[2])
        cursor.execute('''INSERT INTO news 
                          (name, content, ingrid, photo,hard,date, user_id) 
                          VALUES (?,?,?,?,?,?,?)''', (name, content, ingrid, photo, hard, date, str(user_id)))
        cursor.close()
        self.connection.commit()

    def get(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM news WHERE id = ?", (str(news_id)))
        row = cursor.fetchone()
        return row

    def get_all(self, user_id=None, sort=None):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM news ORDER BY name ASC")
        rows = cursor.fetchall()
        return rows

    def delete(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM news WHERE id = ?''', (str(news_id)))

        cursor.close()
        self.connection.commit()


db = DB()
news = NewsModel(db.get_connection())
news.init_table()
user_model = UsersModel(db.get_connection())
user_model.init_table()


def editor_files(name):
    img = Image.open(name)
    width = 120
    height = 120
    resized_img = img.resize((width, height), Image.ANTIALIAS)
    resized_img.save(name)


@app.route('/')
@app.route('/index')
def index():
    news = NewsModel(db.get_connection()).get_all()
    admin = 'fatahoff.georgy@yandex.ru'
    if len(news) != 0:
        news = sorted(news, key=lambda tup: tup[6], reverse=True)
    return render_template('index.html',
                           news=news, admin=admin)


@app.route('/index_false')
def index_false():
    news = NewsModel(db.get_connection()).get_all()
    admin = 'fatahoff.georgy@yandex.ru'
    if len(news) != 0:
        news = sorted(news, key=lambda tup: tup[6], reverse=False)
    return render_template('index.html',
                           news=news, admin=admin)


@app.route('/index_name_true')
def index_name_true():
    admin = 'fatahoff.georgy@yandex.ru'
    news = NewsModel(db.get_connection()).get_all()
    if len(news) != 0:
        news = sorted(news, key=lambda tup: tup[1], reverse=True)
    return render_template('index.html', news=news, admin=admin)


@app.route('/index_name_false')
def index_name_false():
    admin = 'fatahoff.georgy@yandex.ru'
    news = NewsModel(db.get_connection()).get_all()
    if len(news) != 0:
        news = sorted(news, key=lambda tup: tup[1], reverse=False)
    return render_template('index.html', news=news, admin=admin)


@app.route('/index_hard_true')
def index_hard_true():
    admin = 'fatahoff.georgy@yandex.ru'
    news = NewsModel(db.get_connection()).get_all()
    if len(news) != 0:
        news = sorted(news, key=lambda tup: tup[5], reverse=True)
    return render_template('index.html', news=news, admin=admin)


@app.route('/index_hard_false')
def index_hard_false():
    admin = 'fatahoff.georgy@yandex.ru'
    news = NewsModel(db.get_connection()).get_all()
    if len(news) != 0:
        news = sorted(news, key=lambda tup: tup[5], reverse=False)
    return render_template('index.html', news=news, admin=admin)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        user_model = UsersModel(db.get_connection())
        exists = user_model.exists(user_name, password)
        if exists[0]:
            session['username'] = user_name
            session['user_id'] = exists[1]
            return redirect("/index")
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/index')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'GET':
        return render_template('add_news.html')
    elif request.method == 'POST':
        if 'username' not in session:
            return redirect('/login')
        title = request.form['name']
        content = request.form['recipe']
        ingrid = request.form['ingrid']
        hard = request.form['hard']
        if title != '' and content != '' and ingrid != '':
            if 'file' not in request.form:
                where = 'static/for_recipes/' + request.files['file'].filename
                request.files['file'].save(where)
                editor_files(where)
            else:
                print('не все поля заполнены')
                return redirect('/add_book')
            nm = NewsModel(db.get_connection())
            nm.insert(title, content, ingrid, hard, where, session['user_id'])
            return redirect("/index")
        return redirect('/add_book')
        # return render_template('add_news.html')


# @app.route('/red_book/<int:news_id>', methods=['GET', 'POST'])
# def red_book(news_id):
#    print(0)
#    if 'username' not in session:
#        return redirect('/login')
#    nm = NewsModel(db.get_connection())
#    a = nm.get(news_id)
#    title = a[1]
#    content = a[2]
#    brifly = a[3]
#    photo = a[4]
#    id = a[0]


@app.route('/delete_book/<int:news_id>', methods=['GET'])
def delete_book(news_id):
    if 'username' not in session:
        return redirect('/login')
    nm = NewsModel(db.get_connection())
    print(session)
    a = nm.get(news_id)
    filename = a[5]
    os.remove(filename)
    nm.delete(news_id)
    return redirect("/index")


@app.route('/registration', methods=['POST', 'GET'])
def form_sample():
    if request.method == 'GET':
        return render_template('registration.html')
    elif request.method == 'POST':
        user_name = request.form['email']
        password = request.form['password']
        if len(user_name) != 0 and len(password) != 0:
            user_model = UsersModel(db.get_connection())
            vse = user_model.get_all()
            for i in vse:
                if user_name in i:
                    print('Такой логин уже занят')
                    return redirect('/registration')
            #if 'file' not in request.form:
            #    where = 'static/for_logins/' + request.files['file'].filename
            #    request.files['file'].save(where)
            #    editor_files(where)
            #    print(0)
            user_model.insert(user_name, password)
            return redirect("/login")
        return redirect('/registration')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
