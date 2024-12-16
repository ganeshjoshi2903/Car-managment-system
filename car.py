from flask import Flask, request, render_template_string, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)

app.secret_key = 'your_secret_key'  # Required for session management and flash messages

# Create the SQLite database and tables
def create_db():
    conn = sqlite3.connect('data.db', timeout=10)  # Wait for up to 10 seconds
    c = conn.cursor()
    # Create cracker entries table
    c.execute(''' 
        CREATE TABLE IF NOT EXISTS cracker_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            make TEXT,
            model TEXT,
            year INTEGER,
            vin TEXT,
            color TEXT,
            owner_name TEXT,
            license_plate TEXT,
            registration_date TEXT,
            mileage INTEGER,
            comments TEXT
        )
    ''')
    # Create user table for authentication (set default username as 'root' and password as 'root')
    c.execute(''' 
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    # Insert a default user (username=root, password=root) if not already present
    c.execute(''' 
        INSERT OR IGNORE INTO users (username, password) VALUES ('root', 'root')
    ''')
    conn.commit()
    conn.close()

create_db()

# Insert data into the cracker_entries table
def insert_data(cracker_data):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute(''' 
        INSERT INTO cracker_entries (make, model, year, vin, color, owner_name, license_plate, registration_date, mileage, comments)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', cracker_data)
    conn.commit()
    conn.close()

# Fetch all data from cracker_entries
def fetch_all_data():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM cracker_entries')
    rows = c.fetchall()
    conn.close()
    return rows

# Fetch a single record by ID
def fetch_data_by_id(id):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM cracker_entries WHERE id = ?', (id,))
    row = c.fetchone()
    conn.close()
    return row

# Update data in the cracker_entries table
def update_data(id, cracker_data):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute(''' 
        UPDATE cracker_entries
        SET make = ?, model = ?, year = ?, vin = ?, color = ?, owner_name = ?, license_plate = ?, registration_date = ?, mileage = ?, comments = ?
        WHERE id = ?
    ''', (*cracker_data, id))
    conn.commit()
    conn.close()

# Delete data from the cracker_entries table
def delete_data(id):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('DELETE FROM cracker_entries WHERE id = ?', (id,))
    conn.commit()
    conn.close()

# Insert a new user into the users table
def insert_user(username, password):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute(''' 
        INSERT INTO users (username, password) VALUES (?, ?)
    ''', (username, password))
    conn.commit()
    conn.close()

# Check user credentials
def check_user_credentials(username, password):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = c.fetchone()
    conn.close()
    return user

# Route for logging in
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = check_user_credentials(username, password)

        if user:
            session['user_id'] = user[0]  # Store user ID in session
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid username or password", "danger")
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Login</title>
            <style>
                body { font-family: Arial, sans-serif; background-color: #f7f7f7; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
                .login-container { background: #fff; padding: 40px; border-radius: 8px; box-shadow: 0 0 15px rgba(0, 0, 0, 0.1); width: 350px; animation: fadeIn 0.5s ease-in; }
                .login-container h1 { text-align: center; margin-bottom: 20px; color: #007bff; }
                input[type="text"], input[type="password"] { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 4px; }
                button { width: 100%; padding: 12px; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
                button:hover { background-color: #0056b3; }
                .alert { padding: 10px; margin-bottom: 20px; border-radius: 5px; }
                .alert-success { background-color: #28a745; color: white; }
                .alert-danger { background-color: #dc3545; color: white; }
                @keyframes fadeIn {
                    0% { opacity: 0; }
                    100% { opacity: 1; }
                }
            </style>
        </head>
        <body>
            <div class="login-container">
                <h1>Login</h1>
                <form method="POST">
                    <input type="text" name="username" placeholder="Username" required><br>
                    <input type="password" name="password" placeholder="Password" required><br>
                    <button type="submit">Login</button>
                </form>
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        <div class="alert alert-{{ category }}">{{ message }}</div>
                    {% endif %}
                {% endwith %}
                
                
                {% with messages = get_flashed_messages(with_categories=true) %}
    {% for category, message in messages %}
        {% if category == 'danger' %}
            <script>
                document.addEventListener('DOMContentLoaded', function() {
                    alert("{{ message }}");
                });
            </script>
        {% endif %}
    {% endfor %}
{% endwith %}



                
            </div>
        </body>
        </html>
    ''')

# Route for logging out
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user_id from session
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

# Home route to display cracker management page
@app.route('/', methods=['GET', 'POST'])
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login page if not logged in

    if request.method == 'POST':
        cracker_data = (
            request.form['make'],
            request.form['model'],
            request.form['year'],
            request.form['vin'],
            request.form['color'],
            request.form['owner_name'],
            request.form['license_plate'],
            request.form['registration_date'],
            request.form['mileage'],
            request.form['comments']
        )
        entry_id = request.form.get('entry_id')

        if entry_id:
            update_data(entry_id, cracker_data)
            flash("Cracker entry updated successfully!", "success")
        else:
            insert_data(cracker_data)
            flash("Cracker entry added successfully!", "success")

        return redirect(url_for('home'))

    entry_id = request.args.get('edit')
    entry = None
    if entry_id:
        entry = fetch_data_by_id(entry_id)

    entries = fetch_all_data()
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Cracker Management System</title>
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
            <style>
                body { font-family: Arial, sans-serif; background-color: #f0f0f0; }
                .container { background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 15px rgba(0, 0, 0, 0.1); }
                .table { background-color: #fff; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); }
                h1 { color: #007bff; }
                .btn-primary { background-color: #007bff; }
                .btn-danger { background-color: #dc3545; }
                .btn-warning { background-color: #ffc107; }
                .form-control { border-radius: 4px; }
                .alert { margin-bottom: 20px; }
            </style>
            
             <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
        </head>
        <body>
        
        <nav class="navbar navbar-expand-lg navbar-light bg-light">
  <a class="navbar-brand" href="#" style="width:90%" >Car Management System</a>
  

     
      <a href="{{ url_for('logout') }}" class="btn btn-outline-danger my-2 my-sm-0">Logout</a>

</nav>
        <center>
        
            <div class="" style=" width:90%; ">
                <br/>
                <h1>Car Entry Management</h1>
                <br/>
                <br/>
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        <div class="alert alert-{{ category }}">{{ message }}</div>
                    {% endif %}
                {% endwith %}
                <form method="POST">
                    <div class="form-row">
                        <div class="col"><input type="text" name="make" class="form-control" placeholder="Make" value="{{ entry[1] if entry else '' }}" required></div>
                        <div class="col"><input type="text" name="model" class="form-control" placeholder="Model" value="{{ entry[2] if entry else '' }}" required></div>
                    </div>
                    <div class="form-row mt-2">
                        <div class="col"><input type="number" name="year" class="form-control" placeholder="Year" value="{{ entry[3] if entry else '' }}" required></div>
                        <div class="col"><input type="text" name="vin" class="form-control" placeholder="VIN" value="{{ entry[4] if entry else '' }}" required></div>
                    </div>
                    <div class="form-row mt-2">
                        <div class="col"><input type="text" name="color" class="form-control" placeholder="Color" value="{{ entry[5] if entry else '' }}" required></div>
                        <div class="col"><input type="text" name="owner_name" class="form-control" placeholder="Owner Name" value="{{ entry[6] if entry else '' }}" required></div>
                    </div>
                    <div class="form-row mt-2">
                        <div class="col"><input type="text" name="license_plate" class="form-control" placeholder="License Plate" value="{{ entry[7] if entry else '' }}" required></div>
                        <div class="col"><input type="date" name="registration_date" class="form-control" value="{{ entry[8] if entry else '' }}" required></div>
                    </div>
                    <div class="form-row mt-2">
                        <div class="col"><input type="number" name="mileage" class="form-control" placeholder="Mileage" value="{{ entry[9] if entry else '' }}" required></div>
                    </div>
                    <div class="form-row mt-2">
                        <div class="col"><textarea name="comments" class="form-control" placeholder="Comments">{{ entry[10] if entry else '' }}</textarea></div>
                    </div>
                    {% if entry %}
                        <input type="hidden" name="entry_id" value="{{ entry[0] }}">
                    {% endif %}
                    <button type="submit" class="btn btn-primary mt-3">{{ 'Update Cracker Entry' if entry else 'Add Car Entry' }}</button>
                </form>

                <h2 class="mt-5">Existing Entries</h2>
                <table class="table table-bordered">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Make</th>
                            <th>Model</th>
                            <th>Year</th>
                            <th>VIN</th>
                            <th>Color</th>
                            <th>Owner Name</th>
                            <th>License Plate</th>
                            <th>Registration Date</th>
                            <th>Milage</th>
                            <th>Comment</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for entry in entries %}
                            <tr>
                                <td>{{ entry[0] }}</td>
                                <td>{{ entry[1] }}</td>
                                <td>{{ entry[2] }}</td>
                                <td>{{ entry[3] }}</td>
                                <td>{{ entry[4] }}</td>
                                <td>{{ entry[5] }}</td>
                                <td>{{ entry[6] }}</td>
                                <td>{{ entry[7] }}</td>
                                <td>{{ entry[8] }}</td>
                                <td>{{ entry[9] }}</td>
                                <td>{{ entry[10] }}</td>
                                <td>
                                    <a href="{{ url_for('home', edit=entry[0]) }}" class="btn btn-warning">Edit</a>
                                    <form action="{{ url_for('delete', id=entry[0]) }}" method="POST" style="display:inline;">
                                        <button type="submit" class="btn btn-danger">Delete</button>
                                    </form>
                                </td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </center>
            
             <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.14.7/dist/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
 
        </body>
        </html>
    ''', entries=entries, entry=entry)

# Route to delete an entry
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    delete_data(id)
    flash("Entry deleted successfully!", "success")
    return redirect(url_for('home'))

if __name__ == '__main__':

    app.run(debug=True)