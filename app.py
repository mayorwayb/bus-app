from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import firebase_admin
from firebase_admin import credentials, firestore
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to something secure

# Firebase initialization
cred = credentials.Certificate('busapp.json')  # Replace with your actual file
firebase_admin.initialize_app(cred)
db = firestore.client()
users_ref = db.collection('users')


# Role-based access decorator
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'email' not in session and 'user_id' not in session:
                return redirect(url_for('login'))
            if role and session.get('role').lower() != role:
                return "Unauthorized", 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@app.route('/')
def home():
    return redirect(url_for('login'))


# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        role = request.form['role']

        # Check if user exists
        if any(users_ref.where('email', '==', email).stream()):
            return "User already exists", 409

        hashed_password = generate_password_hash(password)

        users_ref.add({
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'password': hashed_password,
            'role': role
        })

        return redirect(url_for('login'))

    return render_template('signup.html')


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        users = users_ref.where('email', '==', email).stream()
        user = next(users, None)
        if not user:
            return "User not found", 404

        user_data = user.to_dict()

        if not check_password_hash(user_data['password'], password):
            return "Incorrect password", 401

        if user_data['role'].lower() != role.lower():
            return "Role mismatch", 403

        session['user_id'] = user.id
        session['email'] = email
        session['role'] = user_data['role']
        session['name'] = user_data['full_name']

        return redirect(url_for(f"{role.lower()}_dashboard"))

    return render_template('login.html')


# Dashboards
@app.route('/passenger_dashboard')
@login_required(role='passenger')
def passenger_dashboard():
    return render_template('passenger_dashboard.html', name=session['name'])

@app.route('/driver_dashboard')
@login_required(role='driver')
def driver_dashboard():
    return render_template('driver_dashboard.html', name=session['name'])

@app.route('/admin_dashboard')
@login_required(role='admin')
def admin_dashboard():
    return render_template('admin_dashboard.html', name=session['name'])


# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
