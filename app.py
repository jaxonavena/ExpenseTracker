from flask import Flask, render_template, request, session, flash, redirect, url_for, jsonify
from flask_bcrypt import Bcrypt
import sqlite3
import secrets
from datetime import datetime


app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = secrets.token_urlsafe(16)

@app.route('/')
@app.route('/home')
def index():
  return render_template('login_signup.html')


connect = sqlite3.connect('database.db')
connect.execute('CREATE TABLE IF NOT EXISTS USERSS (ID INTEGER PRIMARY KEY, name TEXT, email TEXT, balance REAL, income REAL, password TEXT)')
connect.execute('CREATE TABLE IF NOT EXISTS EXPENSES (ID INTEGER PRIMARY KEY, user_id INTEGER, description TEXT, date TEXT, amount REAL, category TEXT, FOREIGN KEY(user_id) REFERENCES USERSS(ID))')
connect.execute('CREATE TABLE IF NOT EXISTS GOALS (ID INTEGER PRIMARY KEY, user_id INTEGER, title TEXT, description TEXT, target_amount REAL, start_time TEXT, end_time TEXT, progress_level TEXT, priority_level TEXT, frequency TEXT, FOREIGN KEY(user_id) REFERENCES USERSS(ID))')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        with sqlite3.connect("database.db") as connect:
            user_id_tuple = connect.execute("SELECT CASE WHEN MAX(ID) IS NULL THEN 1 ELSE MAX(ID) + 1 END AS next_id FROM USERSS")
            user_id = user_id_tuple.fetchone()[0]
            print("SIGNUP USER ID", user_id)
            # session['user_id'] = user_id

            name = request.form['name_signup']
            email = request.form['email_signup']
            balance = float(request.form['balance_signup'])
            income = float(request.form['income_signup'])
            password_plain = request.form['password_signup']
            hashed_password = bcrypt.generate_password_hash(password_plain).decode('utf-8')
            cursor = connect.cursor()
            cursor.execute("INSERT INTO USERSS (id,name,email,balance,income,password) VALUES (?,?,?,?,?,?)", (user_id, name, email, balance, income, hashed_password))
            connect.commit()
        return render_template("login_signup.html")
    return render_template('login_signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        with sqlite3.connect("database.db") as connect:
          email = request.form['email_login']
          password = request.form['password_login']
          cursor = connect.cursor()
          cursor.execute("SELECT password FROM USERSS WHERE email = ?", (email,))
          user = cursor.fetchone()
          print("this is the cursor fetchone user", user)

          cursor.execute("SELECT ID FROM USERSS WHERE email = ?", (email,))
          user_id_row = cursor.fetchone()
          user_id = user_id_row[0] if user_id_row else None

          session['user_id'] = user_id
          print("THIS IS setting user_id", user_id)

          if user and bcrypt.check_password_hash(user[0], password):
              # session['user_id'] = user[0]
              # print("setting user_id", user[0])


              user_id = session.get('user_id')
              cursor.execute("SELECT balance, income FROM USERSS WHERE ID=?", (user_id,))
              user_data = cursor.fetchone()
              cursor.execute("SELECT SUM(amount) FROM EXPENSES WHERE user_id=?", (user_id,))
              expenses_data = cursor.fetchone()
              flash('You were successfully logged in', 'success')
              print("cuurent_balance is ", user_data[0])
              print("User data", user_data)
              print("The total income of this userr isss:", user_data[1])
              return render_template(
              'home.html',
              current_balance=user_data[0] if user_data else 0,
              total_income=user_data[1] if user_data else 0,
              total_expenses=expenses_data[0] if expenses_data else 0
              )
          else:
              return 'Login Failed'
    return render_template('login_signup.html')


# DB TABLE MAPPINGS ----------------------------------------------------------------------------------------------------------

def get_category_name(category_id):
    category_mapping = {
        "expense-category-option1": "Bills",
        "expense-category-option2": "Food",
        "expense-category-option3": "Entertainment",
        "expense-category-option4": "Shopping",
        "expense-category-option5": "Travel",
        "expense-category-option6": "Education",
        "expense-category-option7": "Subscriptions",
        "expense-category-option8": "Miscellaneous",
    }
    return category_mapping.get(category_id, "Unknown")

def get_progress_level(progress_id):
    progress_mapping = {
        "fresh-start-prog": "Fresh Start",
        "gaining-ground-prog": "Gaining Ground",
        "halfway-there-prog": "Halfway There",
        "almost-done-prog": "Almost Done",
        "completedd-prog": "Completed",
    }
    return progress_mapping.get(progress_id, "Unknown")

def get_priority_level(priority_id):
    priority_mapping = {
        "high-priority": "High",
        "medium-priority": "Medium",
        "low-priority": "Low",
    }
    return priority_mapping.get(priority_id, "Unknown")

def get_frequency(frequency_id):
    frequency_mapping = {
        "daily-freq": "Daily",
        "weekly-freq": "Weekly",
        "biweekly-freq": "Biweekly",
        "monthly-freq": "Monthly",
        "quarterly-freq": "Quarterly",
        "yearly-freq": "Yearly",
    }
    return frequency_mapping.get(frequency_id, "Unknown")

# END DB TABLE MAPPINGS -----------------------------------------------------------------------------------------------


@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
  if request.method == 'POST':
        user_id = session.get('user_id')
        flash(user_id)
        if not user_id:
            flash('You must be logged in to add expenses.', 'error')
            return render_template('login_signup.html')

        description = request.form['description']
        date = request.form['date']
        amount = request.form['amount']
        category = request.form['category']
        category_name = get_category_name(category)

        with sqlite3.connect("database.db") as connect:
            cursor = connect.cursor()

            cursor.execute("SELECT MAX(id) FROM EXPENSES")
            max_id = cursor.fetchone()[0]
            expense_id = max_id + 1 if max_id is not None else 1

            # Retrieve current balance
            cursor.execute("SELECT balance FROM USERSS WHERE ID=?", (user_id,))
            current_balance = cursor.fetchone()[0]
            new_balance = current_balance - float(amount)
            # Update the balance in the database
            cursor.execute("UPDATE USERSS SET balance = ? WHERE ID = ?", (new_balance, user_id))

            cursor.execute("INSERT INTO EXPENSES (id, user_id, description, date, amount, category) VALUES (?,?,?,?,?,?)",
                           (expense_id, user_id, description, date, float(amount), category_name))
            connect.commit()

        flash('Expense added successfully!', 'success')
        return redirect(url_for('dashboard'))
  else:
      return render_template('login_signup.html')

@app.route('/get_transactions')
def get_transactions():
    user_id = session.get('user_id')
    if not user_id:
        return {'error': 'User not logged in'}, 401

    with sqlite3.connect("database.db") as connect:
        connect.row_factory = sqlite3.Row
        cursor = connect.cursor()
        cursor.execute("SELECT * FROM EXPENSES WHERE user_id = ?", (user_id,))
        expenses = cursor.fetchall()
        # Convert each row into a dictionary
        expenses_list = [dict(expense) for expense in expenses]

    return {'expenses': expenses_list}

@app.route('/get_goals')
def get_goals():
    user_id = session.get('user_id')
    if not user_id:
        return {'error': 'User not logged in'}, 401

    with sqlite3.connect("database.db") as connect:
        connect.row_factory = sqlite3.Row
        cursor = connect.cursor()
        cursor.execute("SELECT * FROM GOALS WHERE user_id = ?", (user_id,))
        goals = cursor.fetchall()
        # Convert each row into a dictionary
        goals_list = [dict(goal) for goal in goals]
        print("GOALS LIST FROM GET GOALS: ", goals_list)

    return {'goals': goals_list}

@app.route('/update_settings', methods=['POST'])
def update_settings():
    data = request.get_json()
    print(data)

    user_id = session.get('user_id')
    print("USER ID", user_id)


    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401

    new_balance = data.get('new_balance')
    new_income = data.get('new_income')

    print("new balance after json", new_balance)
    print("new income after json", new_income)


    with sqlite3.connect("database.db") as connect:
        cursor = connect.cursor()

        # cursor.execute("SELECT email FROM USERSS WHERE ID = ?", (user_id,))
        # email = cursor.fetchone()
        # print("EMAIL", email)
        cursor.execute("UPDATE USERSS SET balance = ?, income = ? WHERE ID = ?", (new_balance, new_income, user_id))
        connect.commit()

    return jsonify({'success': True})


@app.route('/add_goal', methods=['GET', 'POST'])
def add_goal():
  if request.method == 'POST':
    user_id = session.get('user_id')
    if not user_id:
      return jsonify({'error': 'User not logged in'}), 401

    with sqlite3.connect("database.db") as connect:
      cursor = connect.cursor()

      cursor.execute("SELECT MAX(id) FROM GOALS")
      current_highest_goal_id = cursor.fetchone()[0]
      goal_id = current_highest_goal_id + 1 if current_highest_goal_id is not None else 1

      title = request.form['title']
      description = request.form['description'] #TODO: ALLOW NULL?
      target_amount = float(request.form['target_amount'])
      start_time = request.form['start_time'] # TODO: HAVE DEFAULT?
      end_time = request.form['end_time'] # TODO: HAVE DEFAULT?

      progress_level = request.form['progress_level'] # TODO: HAVE DEFAULT
      progress_level_name = get_progress_level(progress_level)

      priority_level = request.form['priority_level'] # TODO: HAVE DEFAULT
      priority_level_name = get_priority_level(priority_level)

      frequency = request.form['frequency'] # What was this again? If we want it to repeat? TODO: ALLOW NULL
      frequency_name = get_frequency(frequency)



      cursor = connect.cursor()
      cursor.execute("INSERT INTO GOALS (id, user_id, title, description, target_amount, start_time, end_time, progress_level, priority_level, frequency) VALUES (?,?,?,?,?,?,?,?,?,?)", (goal_id, user_id, title, description, target_amount, start_time, end_time, progress_level_name, priority_level_name, frequency_name))
      connect.commit()
    return render_template("home.html")
  else:
    return render_template('add_goal.html')

@app.route('/dashboard')
def dashboard():
    return render_template('home.html')

@app.route('/monthly_expenses')
def get_monthly_expenses():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401

    monthly_expenses = [0] * 12
    with sqlite3.connect("database.db") as connect:
        connect.row_factory = sqlite3.Row
        cursor = connect.cursor()

        for i in range(1, 13):
            cursor.execute("""
                SELECT SUM(amount) as total FROM EXPENSES
                WHERE user_id = ? AND strftime('%m', date) = ?
            """, (user_id, f"{i:02}"))
            result = cursor.fetchone()
            monthly_expenses[i - 1] = result['total'] if result['total'] is not None else 0

    return jsonify(monthly_expenses=monthly_expenses)

@app.route('/delete_expenses', methods=['POST'])
def delete_expenses():
    data = request.get_json()
    ids = data.get('ids', [])
    if not ids:
        return jsonify({'error': 'No expenses selected'}), 400

    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM EXPENSES WHERE id IN ({})".format(','.join('?'*len(ids))), tuple(ids))
        conn.commit()

    return jsonify({'success': True})

@app.route('/delete_goals', methods=['POST'])
def delete_goals():
    data = request.get_json()
    ids = data.get('ids', [])
    if not ids:
        return jsonify({'error': 'No goals selected'}), 400

    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM GOALS WHERE id IN ({})".format(','.join('?'*len(ids))), tuple(ids))
        conn.commit()

    return jsonify({'success': True})

@app.route('/tables')
def tables():
  connect = sqlite3.connect('database.db')
  cursor = connect.cursor()

  cursor.execute('SELECT * FROM USERSS')
  users_data = cursor.fetchall()

  cursor.execute('SELECT * FROM EXPENSES')
  expenses_data = cursor.fetchall()

  cursor.execute('SELECT * FROM GOALS')
  goals_data = cursor.fetchall()

  return render_template("tables.html", users_data=users_data, expenses_data=expenses_data, goals_data=goals_data)


if __name__ == '__main__':
  app.run(debug=True)