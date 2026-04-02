# DAS Apparels – Maintenance Management System
### Group 11 | DBMS Mini Project | Case 11

---

## 📋 Project Overview

Web application for managing the maintenance division of DAS Apparels garment factory.
Built with **Flask (Python)** backend + **HTML/CSS/JS** frontend + **SQLite** database.

---

## 🗂️ Project Structure

```
das_maintenance/
├── app.py                   # Flask backend (routes, DB logic)
├── requirements.txt         # Python dependencies
├── maintenance.db           # SQLite database (auto-created)
├── static/
│   ├── css/style.css        # Stylesheet
│   └── js/main.js           # Frontend interactions
└── templates/
    ├── base.html            # Base layout with sidebar nav
    ├── login.html           # Login page
    ├── dashboard.html       # Dashboard with stats
    ├── new_job.html         # Create maintenance job form
    ├── view_jobs.html       # List jobs with filters
    ├── job_detail.html      # Job details + assign employees/tools
    └── reports.html         # Analytics reports
```

---

## ⚙️ Setup & Run

### 1. Install Python dependencies
```bash
pip install flask
```

### 2. Run the application
```bash
cd das_maintenance
python app.py
```

### 3. Open in browser
```
http://localhost:5000
```

---

## 🔑 Demo Login Credentials

| Username | Password  | Role     |
|----------|-----------|----------|
| admin    | admin123  | Manager  |
| john     | john123   | Electrician |
| nimal    | nimal123  | Plumber  |
| kamal    | kamal123  | Mechanic |

---

## 📊 Database Schema (from ER Diagram)

```sql
Location    (locationID, locationName, description)
Asset       (assetID, name, category, locationID→Location)
Employee    (employeeID, name, speciality, username, passwordHash, salt)
MaintenanceJob  (jobID, description, report_date, status, assetID→Asset)
Tool        (toolID, tool_name, AvailableQuantity)
JobAssignment   (jobID→MaintenanceJob, employeeID→Employee, assignedDate)
ToolUsage       (usageID, jobID→MaintenanceJob, toolID→Tool, borrowDate, returnDate, quantity)
```

---

## ✅ Features Implemented

- **Login / Logout** — Secure with salted SHA-256 password hashing
- **Dashboard** — Stats (Total / Ongoing / Pending / Done)
- **Enter Maintenance Job** — Create new jobs linked to assets
- **View Jobs** — Filter by All / Ongoing / Pending / Done
- **Job Detail** — Full job information with:
  - Update status (Pending → Ongoing → Done)
  - Assign / remove employees
  - Borrow tools from store
  - Return tools back to store
- **Reports** — 4 reports:
  1. Jobs by status
  2. Jobs by asset category
  3. Employee workload table
  4. Tool usage & availability

---

## 🗄️ Sample Data (auto-seeded)

- 5 Locations, 7 Assets, 4 Employees, 8 Tools
- 5 sample maintenance jobs (mix of Pending/Ongoing/Done)
- Sample assignments and tool borrowings
