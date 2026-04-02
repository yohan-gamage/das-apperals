from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from datetime import datetime

import random, time
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = 'das_apparels_maintenance_secret_2024'
app.config['SESSION_PERMANENT'] = False

from functools import wraps

def manager_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Allow if user is 'Management' OR 'Admin'
        role = session.get('speciality')
        if role not in ['Management', 'Admin']:
            flash('Access denied. Admin or Management required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def maintenance_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Allow if user is 'Maintenance' OR 'Admin'
        role = session.get('speciality')
        if role not in ['Maintenance', 'Admin']:
            flash('Access Denied. Admin or Maintenance Specialist required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Mail config — add these lines before app.secret_key
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'dasapparealsmaintenance@gmail.com'   # ← change
app.config['MAIL_PASSWORD'] = 'jbco quxl nzln rzok'       # ← Gmail app password
app.config['MAIL_DEFAULT_SENDER'] = 'dasapparealsmaintenance@gmail.com'
mail = Mail(app)

def get_db():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",                # WAMP default empty password
        database="das_apparels"  # your database name in phpMyAdmin
    )
    return conn

# ─── AUTH ────────────────────────────────────────────────────────────────────

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'employee_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Employee WHERE username=%s", (username,))
        emp = cursor.fetchone()
        cursor.close()
        conn.close()
        if emp and password == emp['passwordHash']:
            session.permanent = False
            session['employee_id'] = emp['employeeID']
            session['employee_name'] = emp['name']
            session['username'] = emp['username']
            session['speciality'] = emp['speciality']
            return redirect(url_for('dashboard'))
        flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/send_otp', methods=['POST'])
def send_otp():
    email = request.form.get('email', '').strip()
    if not email:
        flash('Email is required to send OTP', 'error')
        return redirect(url_for('register'))

    otp = str(random.randint(100000, 999999))
    session['otp'] = otp
    session['otp_email'] = email
    session['otp_expiry'] = time.time() + 300  # 5 minutes

    msg = Message('Your DAS Apparels OTP', recipients=[email])
    msg.body = f'Your one-time password is: {otp}\n\nThis code expires in 5 minutes.'
    try:
        mail.send(msg)
        flash('OTP sent to your email. Check your inbox.', 'success')
    except Exception as e:
        flash('Failed to send OTP. Check email configuration.', 'error')

    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        employee_id = request.form['employee_id'].strip()
        name        = request.form['name'].strip()
        speciality  = request.form['speciality']
        username    = request.form['username'].strip()
        email       = request.form['email'].strip()
        password    = request.form['password']
        confirm     = request.form['confirm']
        otp_entered = request.form.get('otp', '').strip()

        # ── Two-step password check ──────────────────────────
        if password != confirm:
            flash('Passwords do not match', 'error')
            return render_template('register.html')

        # ── OTP verification ─────────────────────────────────
        stored_otp    = session.get('otp')
        stored_email  = session.get('otp_email')
        otp_expiry    = session.get('otp_expiry', 0)

        if not stored_otp:
            flash('Please request an OTP first', 'error')
            return render_template('register.html')
        if time.time() > otp_expiry:
            flash('OTP has expired. Please request a new one.', 'error')
            session.pop('otp', None)
            return render_template('register.html')
        if otp_entered != stored_otp or email != stored_email:
            flash('Invalid OTP or email mismatch', 'error')
            return render_template('register.html')

        # ── Clear OTP from session ───────────────────────────
        session.pop('otp', None)
        session.pop('otp_email', None)
        session.pop('otp_expiry', None)

        # ── DB checks ────────────────────────────────────────
        conn   = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM Employee WHERE employeeID=%s", (employee_id,))
        if cursor.fetchone():
            flash('Employee ID already registered', 'error')
            cursor.close(); conn.close()
            return render_template('register.html')

        cursor.execute("SELECT * FROM Employee WHERE username=%s", (username,))
        if cursor.fetchone():
            flash('Username already taken, choose another', 'error')
            cursor.close(); conn.close()
            return render_template('register.html')

        # ── Insert ───────────────────────────────────────────
        cursor.execute(
            "INSERT INTO Employee (employeeID, name, speciality, username, passwordHash, salt) "
            "VALUES (%s,%s,%s,%s,%s,%s)",
            (employee_id, name, speciality, username, password, '')
        )
        conn.commit()
        cursor.close(); conn.close()
        flash('Account created! You can now login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'employee_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ─── DASHBOARD ───────────────────────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as cnt FROM MaintenanceJob WHERE status='Pending'")
    pending = cursor.fetchone()['cnt']
    cursor.execute("SELECT COUNT(*) as cnt FROM MaintenanceJob WHERE status='Ongoing'")
    ongoing = cursor.fetchone()['cnt']
    cursor.execute("SELECT COUNT(*) as cnt FROM MaintenanceJob WHERE status='Done'")
    done = cursor.fetchone()['cnt']
    cursor.execute("SELECT COUNT(*) as cnt FROM MaintenanceJob")
    total = cursor.fetchone()['cnt']
    cursor.close()
    conn.close()
    stats = {'pending': pending, 'ongoing': ongoing, 'done': done, 'total': total}
    return render_template('dashboard.html', stats=stats)

# ─── ANONYMOUS REPORTING (NEW) ──────────────────────────────────────────────

@app.route('/report_issue', methods=['GET', 'POST'])
def report_issue():
    # Note: No @login_required here so anyone can access it
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        asset_id = request.form['asset_id']
        description = request.form['description']
        mobile = request.form['mobile']
        today = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute(
            "INSERT INTO report (AssetID, description, mobileNumber, status, reportDate) VALUES (%s, %s, %s, %s, %s)",
            (asset_id, description, mobile, 'Pending', today)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash('Issue reported successfully! Maintenance will check it soon.', 'success')
        return redirect(url_for('login'))

    # Fetch assets for the dropdown menu
    cursor.execute("SELECT assetID, name FROM Asset")
    assets = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('report_issue.html', assets=assets)


# ─── JOBS ────────────────────────────────────────────────────────────────────

@app.route('/jobs/new', methods=['GET', 'POST'])
@login_required
@maintenance_only
def new_job():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        desc = request.form['description']
        asset_id = request.form['asset_id']
        report_date = datetime.now().strftime('%Y-%m-%d')
        cursor.execute(
            "INSERT INTO MaintenanceJob (description, report_date, status, assetID) VALUES (%s,%s,%s,%s)",
            (desc, report_date, 'Pending', asset_id)
        )
    
        cursor.execute(
            "UPDATE report SET status = 'Request Reviewed' WHERE assetID = %s AND status = 'Pending'",
            (asset_id,)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash('Maintenance job created successfully!', 'success')
        return redirect(url_for('view_jobs', filter='all'))
    cursor.execute("""
        SELECT DISTINCT a.assetID, a.name, l.locationName AS location_name 
        FROM Asset a
        JOIN report r ON a.assetID = r.assetID
        JOIN Location l ON a.locationID = l.locationID
        WHERE r.status = 'Pending'
        """)
    assets = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('new_job.html', assets=assets)

@app.route('/jobs')
@login_required
def view_jobs():
    filter_type = request.args.get('filter', 'all')
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    base_query = """
        SELECT j.*, a.name as asset_name, a.category, l.locationName
        FROM MaintenanceJob j
        LEFT JOIN Asset a ON j.assetID = a.assetID
        LEFT JOIN Location l ON a.locationID = l.locationID
    """
    if filter_type == 'pending':
        cursor.execute(base_query + " WHERE j.status='Pending' ORDER BY j.report_date DESC")
    elif filter_type == 'ongoing':
        cursor.execute(base_query + " WHERE j.status='Ongoing' ORDER BY j.report_date DESC")
    elif filter_type == 'done':
        cursor.execute(base_query + " WHERE j.status='Done' ORDER BY j.report_date DESC")
    else:
        cursor.execute(base_query + " ORDER BY j.report_date DESC")
    jobs = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('view_jobs.html', jobs=jobs, filter_type=filter_type)

@app.route('/jobs/<int:job_id>')
@login_required
def job_detail(job_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT j.*, a.name as asset_name, a.category, l.locationName
        FROM MaintenanceJob j
        LEFT JOIN Asset a ON j.assetID = a.assetID
        LEFT JOIN Location l ON a.locationID = l.locationID
        WHERE j.jobID=%s
    """, (job_id,))
    job = cursor.fetchone()
    if not job:
        cursor.close()
        conn.close()
        flash('Job not found', 'error')
        return redirect(url_for('view_jobs'))
    cursor.execute("""
        SELECT e.employeeID, e.name, e.speciality, ja.assignedDate
        FROM JobAssignment ja JOIN Employee e ON ja.employeeID = e.employeeID
        WHERE ja.jobID=%s
    """, (job_id,))
    assigned = cursor.fetchall()
    cursor.execute("""
        SELECT tu.*, t.tool_name
        FROM ToolUsage tu JOIN Tool t ON tu.toolID = t.toolID
        WHERE tu.jobID=%s
    """, (job_id,))
    tools = cursor.fetchall()
    cursor.execute("SELECT * FROM Employee ORDER BY name")
    all_employees = cursor.fetchall()
    cursor.execute("SELECT * FROM Tool WHERE AvailableQuantity > 0 ORDER BY tool_name")
    all_tools = cursor.fetchall()
    assigned_ids = [e['employeeID'] for e in assigned]
    cursor.close()
    conn.close()
    return render_template('job_detail.html', job=job, assigned=assigned,
                           tools=tools, all_employees=all_employees,
                           all_tools=all_tools, assigned_ids=assigned_ids)

@app.route('/jobs/<int:job_id>/update_status', methods=['POST'])
@login_required
def update_status(job_id):
    new_status = request.form['status']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE MaintenanceJob SET status=%s WHERE jobID=%s", (new_status, job_id))
    conn.commit()
    cursor.close()
    conn.close()
    flash(f'Job status updated to {new_status}', 'success')
    return redirect(url_for('job_detail', job_id=job_id))

@app.route('/jobs/<int:job_id>/assign_employee', methods=['POST'])
@login_required
@maintenance_only
def assign_employee(job_id):
    emp_id = request.form['employee_id']
    assigned_date = datetime.now().strftime('%Y-%m-%d')
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM JobAssignment WHERE jobID=%s AND employeeID=%s", (job_id, emp_id))
    existing = cursor.fetchone()
    if existing:
        flash('Employee already assigned to this job', 'warning')
    else:
        cursor.execute(
            "INSERT INTO JobAssignment (jobID, employeeID, assignedDate) VALUES (%s,%s,%s)",
            (job_id, emp_id, assigned_date)
        )
        cursor.execute(
            "UPDATE MaintenanceJob SET status='Ongoing' WHERE jobID=%s AND status='Pending'",
            (job_id,)
        )
        conn.commit()
        flash('Employee assigned successfully!', 'success')
    cursor.close()
    conn.close()
    return redirect(url_for('job_detail', job_id=job_id))

@app.route('/jobs/<int:job_id>/remove_employee/<int:emp_id>', methods=['POST'])
@login_required
@maintenance_only
def remove_employee(job_id, emp_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM JobAssignment WHERE jobID=%s AND employeeID=%s", (job_id, emp_id))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Employee removed from job', 'info')
    return redirect(url_for('job_detail', job_id=job_id))

@app.route('/jobs/<int:job_id>/assign_tool', methods=['POST'])
@login_required
def assign_tool(job_id):
    tool_id = request.form['tool_id']
    quantity = int(request.form['quantity'])
    borrow_date = datetime.now().strftime('%Y-%m-%d')
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Tool WHERE toolID=%s", (tool_id,))
    tool = cursor.fetchone()
    if not tool or tool['AvailableQuantity'] < quantity:
        flash('Not enough quantity available for this tool', 'error')
    else:
        cursor.execute(
            "INSERT INTO ToolUsage (jobID, toolID, borrowDate, quantity) VALUES (%s,%s,%s,%s)",
            (job_id, tool_id, borrow_date, quantity)
        )
        cursor.execute(
            "UPDATE Tool SET AvailableQuantity = AvailableQuantity - %s WHERE toolID=%s",
            (quantity, tool_id)
        )
        conn.commit()
        flash('Tool assigned to job!', 'success')
    cursor.close()
    conn.close()
    return redirect(url_for('job_detail', job_id=job_id))

@app.route('/jobs/<int:job_id>/return_tool/<int:usage_id>', methods=['POST'])
@login_required
def return_tool(job_id, usage_id):
    return_date = datetime.now().strftime('%Y-%m-%d')
    comment = request.form.get('damage_comment', '').strip()
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ToolUsage WHERE usageID=%s", (usage_id,))
    usage = cursor.fetchone()
    if usage and not usage['returnDate']:
        cursor.execute("UPDATE ToolUsage SET returnDate=%s, damage_comment=%s WHERE usageID=%s", (return_date, comment, usage_id))
        cursor.execute(
            "UPDATE Tool SET AvailableQuantity = AvailableQuantity + %s WHERE toolID=%s",
            (usage['quantity'], usage['toolID'])
        )
        conn.commit()

        if comment:
            flash(f'Tool returned with damage report: "{comment}"', 'warning')
        else:
            flash('Tool returned to store!', 'success')
    cursor.close()
    conn.close()
    return redirect(url_for('job_detail', job_id=job_id))

@app.route('/jobs/<int:job_id>/delete', methods=['POST'])
@login_required
@maintenance_only
def delete_job(job_id):
    conn = get_db()
    cursor = conn.cursor()
    try:
        # 1. First, delete child records due to Foreign Key constraints
        cursor.execute("DELETE FROM ToolUsage WHERE jobID=%s", (job_id,))
        cursor.execute("DELETE FROM JobAssignment WHERE jobID=%s", (job_id,))
        
        # 2. Now delete the actual job
        cursor.execute("DELETE FROM MaintenanceJob WHERE jobID=%s", (job_id,))
        
        conn.commit()
        flash(f'Job #{job_id:04d} has been permanently deleted.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting job: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('view_jobs'))

@app.route('/requests')
@login_required
def view_requests():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    # We join with Asset and Location to get the names, not just IDs
    cursor.execute("""
        SELECT r.reportID, a.name AS asset_name, l.locationName AS location_name, r.status, r.reportDate
        FROM report r
        JOIN Asset a ON r.assetID = a.assetID
        JOIN Location l ON a.locationID = l.locationID
        ORDER BY r.reportDate DESC
    """)
    all_requests = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('requests.html', requests=all_requests)

# ─── REPORTS ─────────────────────────────────────────────────────────────────

@app.route('/reports')
@login_required
def reports():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT status, COUNT(*) as count FROM MaintenanceJob GROUP BY status")
    by_status = cursor.fetchall()
    cursor.execute("""
        SELECT e.name, e.speciality,
               COUNT(ja.jobID) as total_jobs,
               SUM(CASE WHEN j.status='Ongoing' THEN 1 ELSE 0 END) as ongoing,
               SUM(CASE WHEN j.status='Done' THEN 1 ELSE 0 END) as done
        FROM Employee e
        LEFT JOIN JobAssignment ja ON e.employeeID = ja.employeeID
        LEFT JOIN MaintenanceJob j ON ja.jobID = j.jobID
        GROUP BY e.employeeID ORDER BY total_jobs DESC
    """)
    emp_workload = cursor.fetchall()
    cursor.execute("""
        SELECT t.tool_name, t.AvailableQuantity,
               COUNT(tu.usageID) as times_used,
               SUM(CASE WHEN tu.returnDate IS NULL THEN tu.quantity ELSE 0 END) as currently_out
        FROM Tool t
        LEFT JOIN ToolUsage tu ON t.toolID = tu.toolID
        GROUP BY t.toolID ORDER BY times_used DESC
    """)
    tool_report = cursor.fetchall()
    cursor.execute("""
        SELECT a.category, COUNT(j.jobID) as job_count
        FROM MaintenanceJob j JOIN Asset a ON j.assetID = a.assetID
        GROUP BY a.category ORDER BY job_count DESC
    """)
    by_category = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('reports.html',
                           by_status=by_status,
                           emp_workload=emp_workload,
                           tool_report=tool_report,
                           by_category=by_category)

# ... (existing reports code) ...

# ─── INVENTORY MANAGEMENT (NEW) ─────────────────────────────────────────────

@app.route('/inventory')
@login_required
@manager_only # This is the restriction you asked for
def inventory():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Location")
    locations = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('inventory.html', locations=locations)

@app.route('/inventory/add_asset', methods=['POST'])
@login_required
@manager_only
def add_asset():
    name = request.form['name']
    category = request.form['category']
    loc_id = request.form['location_id']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Asset (name, category, locationID) VALUES (%s, %s, %s)", 
                   (name, category, loc_id))
    conn.commit()
    cursor.close()
    conn.close()
    flash('New Asset added successfully!', 'success')
    return redirect(url_for('inventory'))

@app.route('/inventory/add_tool', methods=['POST'])
@login_required
@manager_only
def add_tool():
    tool_name = request.form['tool_name']
    qty = request.form['quantity']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Tool (tool_name, AvailableQuantity) VALUES (%s, %s)", 
                   (tool_name, qty))
    conn.commit()
    cursor.close()
    conn.close()
    flash('New Tool added to store!', 'success')
    return redirect(url_for('inventory'))



if __name__ == '__main__':
    app.run(debug=True, port=5000)