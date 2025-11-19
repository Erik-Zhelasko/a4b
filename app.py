from flask import Flask, render_template, request, redirect, session, flash
import psycopg2
import psycopg2.extras
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "CHANGE_THIS_SECRET_KEY"   # Change this before submission

# ---------------------------
# DATABASE CONNECTION
# ---------------------------
def get_db():
    return psycopg2.connect(
        dbname="company",
        user="owner",
        host="localhost"
    )

# ---------------------------
# LOGIN REQUIRED DECORATOR
# ---------------------------
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper

# ---------------------------
# LOGIN ROUTE (A1)
# ---------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cur.execute("SELECT * FROM app_user WHERE username=%s", (username,))
        user = cur.fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            return redirect("/")
        else:
            flash("Invalid username or password")

    return render_template("login.html")

# ---------------------------
# LOGOUT (A1)
# ---------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------------------
# HOME ROUTE (A2)
# ---------------------------
@app.route("/")
@login_required
def home():
    search = request.args.get("search", "")
    sort = request.args.get("sort", "name_asc")
    dept = request.args.get("dept", "")   # NEW: selected department

    # Sorting whitelist
    allowed_sorts = {
        "name_asc": "e.lname ASC, e.fname ASC",
        "name_desc": "e.lname DESC, e.fname DESC",
        "hours_asc": "total_hours ASC",
        "hours_desc": "total_hours DESC"
    }
    order_by = allowed_sorts.get(sort, "e.lname ASC")

    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # NEW: Load department names for dropdown
    cur.execute("SELECT dname FROM department ORDER BY dname;")
    departments = [row[0] for row in cur.fetchall()]

    # Build WHERE clause
    where_clauses = []
    params = []

    # Name search (case-insensitive, partial)
    where_clauses.append("(e.fname ILIKE %s OR e.lname ILIKE %s)")
    params.extend([f"%{search}%", f"%{search}%"])

    # Department filter (optional)
    if dept != "":
        where_clauses.append("d.dname = %s")
        params.append(dept)

    where_sql = " AND ".join(where_clauses)

    # FINAL QUERY
    query = f"""
        SELECT
            e.ssn,
            e.fname || ' ' || e.lname AS full_name,
            d.dname,
            COALESCE(dep.count_dep, 0) AS num_dependents,
            COALESCE(w.count_proj, 0) AS num_projects,
            COALESCE(w.total_hours, 0) AS total_hours
        FROM employee e
        JOIN department d ON e.dno = d.dnumber

        LEFT JOIN (
            SELECT essn, COUNT(*) AS count_dep
            FROM dependent
            GROUP BY essn
        ) dep ON dep.essn = e.ssn

        LEFT JOIN (
            SELECT essn, COUNT(*) AS count_proj, SUM(hours) AS total_hours
            FROM works_on
            GROUP BY essn
        ) w ON w.essn = e.ssn

        WHERE {where_sql}
        ORDER BY {order_by};
    """

    cur.execute(query, tuple(params))
    employees = cur.fetchall()

    return render_template(
        "home.html",
        employees=employees,
        departments=departments,   # NEW
        selected_dept=dept,        # NEW
        search=search              # so form remembers search
    )

# ---------------------------
# ADMIN ONLY DECORATOR (RBAC)
# ---------------------------
def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        if session.get("role") != "admin":
            return "Access denied (Admin only)", 403
        return f(*args, **kwargs)
    return wrapper


# ---------------------------
# RUN FLASK APP
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)
