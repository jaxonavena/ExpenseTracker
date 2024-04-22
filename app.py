from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)


@app.route('/')
@app.route('/home')
def index():
  return render_template('index.html')


connect = sqlite3.connect('database.db')
connect.execute('CREATE TABLE IF NOT EXISTS USERS (ID INTEGER PRIMARY KEY, name TEXT, email TEXT)')
connect.execute('CREATE TABLE IF NOT EXISTS EXPENSES (ID INTEGER PRIMARY KEY, user_id INTEGER, description TEXT, date TEXT, amount REAL, category TEXT, FOREIGN KEY(user_id) REFERENCES USERS(ID))')
connect.execute('CREATE TABLE IF NOT EXISTS GOALS (ID INTEGER PRIMARY KEY, user_id INTEGER, title TEXT, description TEXT, target_amount REAL, start_time TEXT, end_time TEXT, progress_level TEXT, priority_level TEXT, frequency TEXT, FOREIGN KEY(user_id) REFERENCES USERS(ID))')

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
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
    return render_template('add_user.html')

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
  if request.method == 'POST':
    with sqlite3.connect("database.db") as connect:
      expense_id = request.form['expense_id'] # TODO: MAKE IT COUNT ON IT'S OWN
      user_id = request.form['user_id'] # TODO: MAKE IT SOURCE THE USER ID, AND ONLY ALLOW USERS TO MAKE EXPENSES AND GOALS
      description = request.form['description'] #TODO: ALLOW NULL
      date = request.form['date']
      amount = request.form['amount']
      category = request.form['category']

      cursor = connect.cursor()
      cursor.execute("INSERT INTO EXPENSES (id, user_id, description, date, amount, category) VALUES (?,?,?,?,?,?)", (expense_id, user_id, description, date, amount, category))
      connect.commit()
    return render_template("index.html")
  else:
    return render_template('add_expense.html')


@app.route('/add_goal', methods=['GET', 'POST'])
def add_goal():
  if request.method == 'POST':
    with sqlite3.connect("database.db") as connect:
      goal_id = request.form['goal_id'] # TODO: MAKE IT COUNT ON IT'S OWN
      user_id = request.form['user_id'] # TODO: MAKE IT SOURCE THE USER ID, AND ONLY ALLOW USERS TO MAKE EXPENSES AND GOALS
      title = request.form['title']
      description = request.form['description'] #TODO: ALLOW NULL?
      target_amount = request.form['target_amount']
      start_time = request.form['start_time'] # TODO: HAVE DEFAULT?
      end_time = request.form['end_time'] # TODO: HAVE DEFAULT?
      progress_level = request.form['progress_level'] # TODO: HAVE DEFAULT
      priority_level = request.form['priority_level'] # TODO: HAVE DEFAULT
      frequency = request.form['frequency'] # What was this again? If we want it to repeat? TODO: ALLOW NULL


      cursor = connect.cursor()
      cursor.execute("INSERT INTO GOALS (id, user_id, title, description, target_amount, start_time, end_time, progress_level, priority_level, frequency) VALUES (?,?,?,?,?,?,?,?,?,?)", (goal_id, user_id, title, description, target_amount, start_time, end_time, progress_level, priority_level, frequency))
      connect.commit()
    return render_template("index.html")
  else:
    return render_template('add_goal.html')


@app.route('/tables')
def tables():
  connect = sqlite3.connect('database.db')
  cursor = connect.cursor()

  cursor.execute('SELECT * FROM USERS')
  users_data = cursor.fetchall()

  cursor.execute('SELECT * FROM EXPENSES')
  expenses_data = cursor.fetchall()

  cursor.execute('SELECT * FROM GOALS')
  goals_data = cursor.fetchall()

  return render_template("tables.html", users_data=users_data, expenses_data=expenses_data, goals_data=goals_data)



if __name__ == '__main__':
  app.run(debug=False)
