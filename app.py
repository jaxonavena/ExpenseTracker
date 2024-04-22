from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)


@app.route('/')
@app.route('/home')
def index():
  return render_template('index.html')


connect = sqlite3.connect('database.db')
connect.execute('CREATE TABLE IF NOT EXISTS USERS (ID INTEGER PRIMARY KEY, name TEXT, email TEXT)')
connect.execute('CREATE TABLE IF NOT EXISTS EXPENSE (ID INTEGER PRIMARY KEY, user_id INTEGER, description TEXT, date TEXT, amount REAL, category TEXT, FOREIGN KEY(user_id) REFERENCES USERS(ID))')
connect.execute('CREATE TABLE IF NOT EXISTS GOAL (ID INTEGER PRIMARY KEY, user_id INTEGER, title TEXT, description TEXT, target_amount REAL, start_time TEXT, end_time TEXT, progress_level TEXT, priority_level TEXT, frequency TEXT, FOREIGN KEY(user_id) REFERENCES USERS(ID))')

@app.route('/join', methods=['GET', 'POST'])
def join():
  if request.method == 'POST':
    with sqlite3.connect("database.db") as connect:

      user_id_tuple = connect.execute("SELECT CASE WHEN MAX(ID) IS NULL THEN 1 ELSE MAX(ID) + 1 END AS next_id FROM USERS")
      user_id = user_id_tuple.fetchone()[0]

      name = request.form['name']
      email = request.form['email']

      cursor = connect.cursor()
      cursor.execute("INSERT INTO USERS (id,name,email) VALUES (?,?,?)", (user_id, name, email))
      connect.commit()
    return render_template("index.html")
  else:
    return render_template('join.html')


@app.route('/users')
def users():
  connect = sqlite3.connect('database.db')
  cursor = connect.cursor()
  cursor.execute('SELECT * FROM USERS')

  data = cursor.fetchall()
  return render_template("users.html", data=data)


if __name__ == '__main__':
  app.run(debug=False)
