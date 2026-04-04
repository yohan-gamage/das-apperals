from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from datetime import datetime
import os
import random, time
from flask_mail import Mail, Message
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'das_apparels_maintenance_secret_2024')
app.config['SESSION_PERMANENT'] = False

# --- MAIL CONFIG ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USER', 'dasapparealsmaintenance@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASS', 'jbco quxl nzln rzok') 
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USER', 'dasapparealsmaintenance@gmail.com')
mail = Mail(app)

# --- DECORATORS ---
def manager_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        role = session.get('speciality')
        if role not in ['Management', 'Admin']:
            flash('Access denied. Admin or Management required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def maintenance_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        role = session.get('speciality')
        if role not in ['Maintenance', 'Admin']:
            flash('Access Denied. Admin or Maintenance Specialist required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'employee_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def get_db():
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        import urllib.parse as urlparse
        url = urlparse.urlparse(db_url)
        return mysql.connector.connect(
            host=url.hostname,
            user=url.username,
            password=url.password,
            port=url.port or 3306,
            database=url.path[1:]
        )
    else:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",                
            database="das_apparels"
        )

@app.context_processor
def inject_ongoing_count():
    if 'employee_id' in session:
        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            # Standardized to lowercase table names: jobassignment, maintenancejob
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM jobassignment ja
                JOIN maintenancejob j ON ja.jobID = j.jobID
                WHERE ja.employeeID = %s AND j.status = 'Ongoing'
            """, (session['employee_id'],))
            result = cursor.fetchone()
            cursor.close(); conn.close()
            return {'ongoing_count': result['count']}
        except:
            return {'ongoing_count': 0}
    return {'ongoing_count': 0}

# --- ROUTES ---

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'employee_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        # Standardized to lowercase table: employee
        cursor.execute("SELECT * FROM employee WHERE username=%s", (username,))
        emp = cursor.fetchone()
        cursor.close(); conn.close()
        if emp and password == emp['passwordHash']:
            session['employee_id'] = emp['employeeID']
            session['employee_name'] = emp['name']
            session['username'] = emp['username']
            session['speciality'] = emp['speciality']
            return redirect(url_for('dashboard'))
        flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    # Standardized to lowercase table: maintenancejob
    cursor.execute("SELECT status, COUNT(*) as cnt FROM maintenancejob GROUP BY status")
    results = cursor.fetchall()
    stats = {r['status'].lower(): r['cnt'] for r in results}
    for s in ['pending', 'ongoing', 'done']:
        if s not in stats: stats[s] = 0
    cursor.close(); conn.close()
    return render_template('dashboard.html', stats=stats)

@app.route('/report_issue', methods=['GET', 'POST'])
def report_issue():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        cursor.execute(
            "INSERT INTO report (AssetID, description, mobileNumber, status, reportDate) VALUES (%s, %s, %s, %s, %s)",
            (request.form['asset_id'], request.form['description'], request.form['mobile'], 'Pending', datetime.now().strftime('%Y-%m-%d'))
        )
        conn.commit()
        cursor.close(); conn.close()
        flash('Issue reported successfully!', 'success')
        return redirect(url_for('login'))

    # Standardized to lowercase table: asset
    cursor.execute("SELECT assetID, name FROM asset")
    assets = cursor.fetchall()
    cursor.close(); conn.close()
    return render_template('report_issue.html', assets=assets)

@app.route('/jobs')
@login_required
def view_jobs():
    filter_type = request.args.get('filter', 'all')
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    base_query = """
        SELECT j.*, a.name as asset_name, a.category, l.locationName
        FROM maintenancejob j
        LEFT JOIN asset a ON j.assetID = a.assetID
        LEFT JOIN location l ON a.locationID = l.locationID
    """
    if filter_type != 'all':
        cursor.execute(base_query + f" WHERE j.status='{filter_type.capitalize()}' ORDER BY j.report_date DESC")
    else:
        cursor.execute(base_query + " ORDER BY j.report_date DESC")
    jobs = cursor.fetchall()
    cursor.close(); conn.close()
    return render_template('view_jobs.html', jobs=jobs, filter_type=filter_type)

@app.route('/inventory')
@login_required
@manager_only
def inventory_management():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT locationID, locationName FROM location ORDER BY locationName ASC")
    locations = cursor.fetchall()
    cursor.execute("SELECT assetID, name FROM asset ORDER BY name ASC")
    assets = cursor.fetchall()
    cursor.execute("SELECT toolID, tool_name, AvailableQuantity FROM tool ORDER BY tool_name ASC")
    tools = cursor.fetchall()
    cursor.close(); conn.close()
    return render_template('inventory.html', locations=locations, assets=assets, tools=tools)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
