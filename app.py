from flask import Flask, render_template, request, redirect, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

app = Flask(__name__)
app.secret_key = "todo_secret_key"


# ---------------- DATABASE CONNECTION ----------------
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="emil@2003",  # change this
        database="todo_app"
    )


# ---------------- HOME ----------------
@app.route("/")
def home():
    return redirect("/login")


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        db = get_db()
        cursor = db.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (name, email, password)
            )
            db.commit()
        except:
            return "Email already exists!"

        return redirect("/login")

    return render_template("register.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            return redirect("/dashboard")
        else:
            return "Invalid Email or Password!"

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    filter_type = request.args.get("filter", "all")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    if filter_type == "completed":
        cursor.execute(
            "SELECT * FROM tasks WHERE user_id=%s AND status=TRUE ORDER BY created_at DESC",
            (session["user_id"],)
        )
    elif filter_type == "pending":
        cursor.execute(
            "SELECT * FROM tasks WHERE user_id=%s AND status=FALSE ORDER BY created_at DESC",
            (session["user_id"],)
        )
    else:
        cursor.execute(
            "SELECT * FROM tasks WHERE user_id=%s ORDER BY created_at DESC",
            (session["user_id"],)
        )

    tasks = cursor.fetchall()

    # Progress Calculation
    cursor.execute("SELECT COUNT(*) as total FROM tasks WHERE user_id=%s",
                   (session["user_id"],))
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as done FROM tasks WHERE user_id=%s AND status=TRUE",
                   (session["user_id"],))
    done = cursor.fetchone()["done"]

    progress = int((done / total) * 100) if total > 0 else 0

    return render_template("dashboard.html",
                           tasks=tasks,
                           progress=progress,
                           filter_type=filter_type,
                           today=date.today())


# ---------------- ADD TASK ----------------
@app.route("/add_task", methods=["POST"])
def add_task():
    if "user_id" not in session:
        return redirect("/login")

    task = request.form["task"]
    priority = request.form["priority"]
    due_date = request.form["due_date"]

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO tasks (user_id, task, priority, due_date) VALUES (%s, %s, %s, %s)",
        (session["user_id"], task, priority, due_date)
    )
    db.commit()

    return redirect("/dashboard")


# ---------------- DELETE ----------------
@app.route("/delete/<int:id>")
def delete(id):
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "DELETE FROM tasks WHERE id=%s AND user_id=%s",
        (id, session["user_id"])
    )
    db.commit()

    return redirect("/dashboard")


# ---------------- COMPLETE ----------------
@app.route("/complete/<int:id>")
def complete(id):
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE tasks SET status=TRUE WHERE id=%s AND user_id=%s",
        (id, session["user_id"])
    )
    db.commit()

    return redirect("/dashboard")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)