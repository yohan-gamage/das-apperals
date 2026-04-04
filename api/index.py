from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from datetime import datetime
import os
import random, time
from flask_mail import Mail, Message
from functools import wraps

app = Flask(__name__)

# --- CONFIGURATION (UPDATED FOR PRODUCTION/VERCEL) ---
# Use Environment Variables for sensitive keys
app.secret_key = os.getenv('SECRET_KEY', 'das_apparels_maintenance_secret_2024')
app.config['SESSION_PERMANENT'] = False

# Mail config — Updated to use Environment Variables
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'dasapparealsmaintenance@gmail.com')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'jbco quxl nzln rzok')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME', 'dasapparealsmaintenance@gmail.com')
mail = Mail(app)

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

def get_db():
    # Updated for Cloud Hosting (Vercel cannot connect to localhost)
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', '1234'),
        database=os.getenv('DB_NAME', 'das_apparels'),
        port=int(os.getenv('DB_PORT', 3306))
    )
    return conn

# ─── GLOBAL CONTEXT PROCESSOR ───────────────────────────────────────
@app.context_processor
def inject_ongoing_count():
    if 'employee_id' in session:
        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            # Table names changed to lowercase to match das_apparels.sql exactly
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM jobassignment ja
                JOIN maintenancejob j ON ja.jobID = j.jobID
                WHERE ja.employeeID = %s AND j.status = 'Ongoing'
            """, (session['employee_id'],))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return {'ongoing_count': result['count']}
        except:
            return {'ongoing_count': 0}
    return {'ongoing_count': 0}

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
        # Table 'employee' lowercase
        cursor.execute("SELECT * FROM employee WHERE username=%s", (username,))
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
    session['otp_expiry'] = time.time() + 300 
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
        if password != confirm:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
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
        session.pop('otp', None)
        session.pop('otp_email', None)
        session.pop('otp_expiry', None)
        conn   = get_db()
        cursor = conn.cursor(dictionary=True)
        # Table 'employee' lowercase
        cursor.execute("SELECT * FROM employee WHERE employeeID=%s", (employee_id,))
        if cursor.fetchone():
            flash('Employee ID already registered', 'error')
            cursor.close(); conn.close()
            return render_template('register.html')
        cursor.execute("SELECT * FROM employee WHERE username=%s", (username,))
        if cursor.fetchone():
            flash('Username already taken, choose another', 'error')
            cursor.close(); conn.close()
            return render_template('register.html')
        cursor.execute(
            "INSERT INTO employee (employeeID, name, speciality, username, passwordHash, salt) "
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
    # Table 'maintenancejob' lowercase
    cursor.execute("SELECT COUNT(*) as cnt FROM maintenancejob WHERE status='Pending'")
    pending = cursor.fetchone()['cnt']
    cursor.execute("SELECT COUNT(*) as cnt FROM maintenancejob WHERE status='Ongoing'")
    ongoing = cursor.fetchone()['cnt']
    cursor.execute("SELECT COUNT(*) as cnt FROM maintenancejob WHERE status='Done'")
    done = cursor.fetchone()['cnt']
    cursor.execute("SELECT COUNT(*) as cnt FROM maintenancejob")
    total = cursor.fetchone()['cnt']
    cursor.close()
    conn.close()
    stats = {'pending': pending, 'ongoing': ongoing, 'done': done, 'total': total}
    return render_template('dashboard.html', stats=stats)

# ─── ANONYMOUS REPORTING ──────────────────────────────────────────────

@app.route('/report_issue', methods=['GET', 'POST'])
def report_issue():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        asset_id = request.form['asset_id']
        description = request.form['description']
        mobile = request.form['mobile']
        today = datetime.now().strftime('%Y-%m-%d')
        # Table 'report', Column 'AssetID' (case sensitive)
        cursor.execute(
            "INSERT INTO report (AssetID, description, mobileNumber, status, reportDate) VALUES (%s, %s, %s, %s, %s)",
            (asset_id, description, mobile, 'Pending', today)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash('Issue reported successfully! Maintenance will check it soon.', 'success')
        return redirect(url_for('login'))
    # Table 'asset' lowercase
    cursor.execute("SELECT assetID, name FROM asset")
    assets = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('report_issue.html', assets=assets)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def my_profile():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    emp_id = session.get('employee_id')
    if request.method == 'POST':
        new_name = request.form.get('name')
        new_username = request.form.get('username')
        new_password = request.form.get('password')
        # Table 'employee' lowercase
        if new_password:
            cursor.execute(
                "UPDATE employee SET name=%s, username=%s, passwordHash=%s WHERE employeeID=%s",
                (new_name, new_username, new_password, emp_id)
            )
        else:
            cursor.execute(
                "UPDATE employee SET name=%s, username=%s WHERE employeeID=%s",
                (new_name, new_username, emp_id)
            )
        conn.commit()
        session['employee_name'] = new_name
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('my_profile'))
    cursor.execute("SELECT * FROM employee WHERE employeeID = %s", (emp_id,))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('profile.html', user=user_data)

@app.route('/my-jobs')
@login_required
def my_jobs():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    emp_id = session.get('employee_id')
    # Table names matched to lowercase SQL schema
    cursor.execute("""
        SELECT j.jobID, j.assetID, j.description, j.report_date, j.status, a.name AS asset_name
        FROM maintenancejob j
        JOIN jobassignment ja ON j.jobID = ja.jobID
        JOIN asset a ON j.assetID = a.assetID
        WHERE ja.employeeID = %s
        ORDER BY j.report_date DESC
    """, (emp_id,))
    personal_jobs = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('my_jobs.html', jobs=personal_jobs)

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
        # Table 'maintenancejob' and 'report' lowercase
        cursor.execute(
            "INSERT INTO maintenancejob (description, report_date, status, assetID) VALUES (%s,%s,%s,%s)",
            (desc, report_date, 'Pending', asset_id)
        )
        cursor.execute(
            "UPDATE report SET status = 'Request Reviewed' WHERE AssetID = %s AND status = 'Pending'",
            (asset_id,)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash('Maintenance job created successfully!', 'success')
        return redirect(url_for('view_jobs', filter='all'))
    cursor.execute("""
        SELECT DISTINCT a.assetID, a.name, l.locationName AS location_name 
        FROM asset a
        JOIN report r ON a.assetID = r.AssetID
        JOIN location l ON a.locationID = l.locationID
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
    # Corrected table names to lowercase
    base_query = """
        SELECT j.*, a.name as asset_name, a.category, l.locationName
        FROM maintenancejob j
        LEFT JOIN asset a ON j.assetID = a.assetID
        LEFT JOIN location l ON a.locationID = l.locationID
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
    # Corrected table names to lowercase
    cursor.execute("""
        SELECT j.*, a.name as asset_name, a.category, l.locationName
        FROM maintenancejob j
        LEFT JOIN asset a ON j.assetID = a.assetID
        LEFT JOIN location l ON a.locationID = l.locationID
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
        FROM jobassignment ja JOIN employee e ON ja.employeeID = e.employeeID
        WHERE ja.jobID=%s
    """, (job_id,))
    assigned = cursor.fetchall()
    cursor.execute("""
        SELECT tu.*, t.tool_name
        FROM toolusage tu JOIN tool t ON tu.toolID = t.toolID
        WHERE tu.jobID=%s
    """, (job_id,))
    tools = cursor.fetchall()
    cursor.execute("SELECT * FROM employee ORDER BY name")
    all_employees = cursor.fetchall()
    cursor.execute("SELECT * FROM tool WHERE AvailableQuantity > 0 ORDER BY tool_name")
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
    cursor.execute("UPDATE maintenancejob SET status=%s WHERE jobID=%s", (new_status, job_id))
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
    cursor.execute("SELECT * FROM jobassignment WHERE jobID=%s AND employeeID=%s", (job_id, emp_id))
    existing = cursor.fetchone()
    if existing:
        flash('Employee already assigned to this job', 'warning')
    else:
        cursor.execute(
            "INSERT INTO jobassignment (jobID, employeeID, assignedDate) VALUES (%s,%s,%s)",
            (job_id, emp_id, assigned_date)
        )
        cursor.execute(
            "UPDATE maintenancejob SET status='Ongoing' WHERE jobID=%s AND status='Pending'",
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
    cursor.execute("DELETE FROM jobassignment WHERE jobID=%s AND employeeID=%s", (job_id, emp_id))
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
    cursor.execute("SELECT * FROM tool WHERE toolID=%s", (tool_id,))
    tool = cursor.fetchone()
    if not tool or tool['AvailableQuantity'] < quantity:
        flash('Not enough quantity available for this tool', 'error')
    else:
        cursor.execute(
            "INSERT INTO toolusage (jobID, toolID, borrowDate, quantity) VALUES (%s,%s,%s,%s)",
            (job_id, tool_id, borrow_date, quantity)
        )
        cursor.execute(
            "UPDATE tool SET AvailableQuantity = AvailableQuantity - %s WHERE toolID=%s",
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
    cursor.execute("SELECT * FROM toolusage WHERE usageID=%s", (usage_id,))
    usage = cursor.fetchone()
    if usage and not usage['returnDate']:
        cursor.execute("UPDATE toolusage SET returnDate=%s, damage_comment=%s WHERE usageID=%s", (return_date, comment, usage_id))
        cursor.execute(
            "UPDATE tool SET AvailableQuantity = AvailableQuantity + %s WHERE toolID=%s",
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
        # Table names corrected to lowercase
        cursor.execute("DELETE FROM toolusage WHERE jobID=%s", (job_id,))
        cursor.execute("DELETE FROM jobassignment WHERE jobID=%s", (job_id,))
        cursor.execute("DELETE FROM maintenancejob WHERE jobID=%s", (job_id,))
        conn.commit()
        flash(f'Job #{job_id:04d} has been permanently deleted.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting job: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('view_jobs'))

# ─── INVENTORY MANAGEMENT ───────────────────────────────────

@app.route('/inventory/remove-asset', methods=['POST'])
@login_required
@manager_only
def remove_asset_dropdown():
    asset_id = request.form.get('asset_id')
    conn = get_db()
    cursor = conn.cursor()
    try:
        # Table 'asset' lowercase
        cursor.execute("DELETE FROM asset WHERE assetID = %s", (asset_id,))
        conn.commit()
        flash('Asset removed successfully!', 'success')
    except:
        flash('Error: This asset is linked to existing job records.', 'danger')
    cursor.close()
    conn.close()
    return redirect(url_for('inventory_management'))

@app.route('/inventory/remove-tool', methods=['POST'])
@login_required
@manager_only
def remove_tool_dropdown():
    tool_id = request.form.get('tool_id')
    qty_to_remove = int(request.form.get('quantity'))
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    # Table 'tool' lowercase
    cursor.execute("SELECT AvailableQuantity FROM tool WHERE toolID = %s", (tool_id,))
    tool = cursor.fetchone()
    if tool and tool['AvailableQuantity'] >= qty_to_remove:
        new_qty = tool['AvailableQuantity'] - qty_to_remove
        cursor.execute("UPDATE tool SET AvailableQuantity = %s WHERE toolID = %s", (new_qty, tool_id))
        conn.commit()
        flash(f'Removed {qty_to_remove} items from tool stock.', 'success')
    else:
        flash('Error: Not enough stock to remove that amount.', 'warning')
    cursor.close()
    conn.close()
    return redirect(url_for('inventory_management'))

@app.route('/requests')
@login_required
def view_requests():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    # Table names matched to lowercase
    cursor.execute("""
        SELECT r.reportID, a.name AS asset_name, l.locationName AS location_name, r.description, r.status, r.reportDate
        FROM report r
        JOIN asset a ON r.AssetID = a.assetID
        JOIN location l ON a.locationID = l.locationID
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
    # Table names matched to lowercase
    cursor.execute("SELECT status, COUNT(*) as count FROM maintenancejob GROUP BY status")
    by_status = cursor.fetchall()
    cursor.execute("""
        SELECT e.name, e.speciality,
               COUNT(ja.jobID) as total_jobs,
               SUM(CASE WHEN j.status='Ongoing' THEN 1 ELSE 0 END) as ongoing,
               SUM(CASE WHEN j.status='Done' THEN 1 ELSE 0 END) as done
        FROM employee e
        LEFT JOIN jobassignment ja ON e.employeeID = ja.employeeID
        LEFT JOIN maintenancejob j ON ja.jobID = j.jobID
        GROUP BY e.employeeID ORDER BY total_jobs DESC
    """)
    emp_workload = cursor.fetchall()
    cursor.execute("""
        SELECT t.tool_name, t.AvailableQuantity,
               COUNT(tu.usageID) as times_used,
               SUM(CASE WHEN tu.returnDate IS NULL THEN tu.quantity ELSE 0 END) as currently_out
        FROM tool t
        LEFT JOIN toolusage tu ON t.toolID = tu.toolID
        GROUP BY t.toolID ORDER BY times_used DESC
    """)
    tool_report = cursor.fetchall()
    cursor.execute("""
        SELECT a.category, COUNT(j.jobID) as job_count
        FROM maintenancejob j JOIN asset a ON j.assetID = a.assetID
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

# ─── INVENTORY MANAGEMENT ─────────────────────────────────────────────

@app.route('/inventory')
@login_required
@manager_only
def inventory_management():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    # Table names matched to lowercase
    cursor.execute("SELECT locationID, locationName FROM location ORDER BY locationName ASC")
    locations = cursor.fetchall()
    cursor.execute("SELECT assetID, name FROM asset ORDER BY name ASC")
    assets = cursor.fetchall()
    cursor.execute("SELECT toolID, tool_name, AvailableQuantity FROM tool ORDER BY tool_name ASC")
    tools = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('inventory.html', locations=locations, assets=assets, tools=tools)

@app.route('/inventory/add_asset', methods=['POST'])
@login_required
@manager_only
def add_asset():
    name = request.form['name']
    category = request.form['category']
    loc_id = request.form['location_id']
    conn = get_db()
    cursor = conn.cursor()
    # Table 'asset' lowercase
    cursor.execute("INSERT INTO asset (name, category, locationID) VALUES (%s, %s, %s)", 
                   (name, category, loc_id))
    conn.commit()
    cursor.close()
    conn.close()
    flash('New Asset added successfully!', 'success')
    return redirect(url_for('inventory_management'))

@app.route('/inventory/add_tool', methods=['POST'])
@login_required
@manager_only
def add_tool():
    tool_name = request.form['tool_name']
    qty = request.form['quantity']
    conn = get_db()
    cursor = conn.cursor()
    # Table 'tool' lowercase
    cursor.execute("INSERT INTO tool (tool_name, AvailableQuantity) VALUES (%s, %s)", 
                   (tool_name, qty))
    conn.commit()
    cursor.close()
    conn.close()
    flash('New Tool added to store!', 'success')
    return redirect(url_for('inventory_management'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
