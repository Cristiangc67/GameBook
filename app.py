from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from database import init_db, get_db_connection

app = Flask(__name__, static_folder="static")
init_db()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/home", methods=["GET"])
def home():
    query = request.args.get("query")
    results = []
    if query:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE name LIKE ?", ("%" + query + "%",))
        results = cursor.fetchall()
        conn.close()
    return render_template("home.html", query=query, results=results)


@app.route("/mislistas")
def mislistas():
    return render_template("mislistas.html")


@app.route("/mislistas/<int:id>")
def selectedList():
    return render_template("mislistas.html")


@app.route("/create", methods=("GET", "POST"))
def create():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]

        conn = get_db_connection()
        conn.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
        conn.commit()
        conn.close()
        return redirect(url_for("list"))

    return render_template("create.html")


@app.route("/update/<int:id>", methods=("GET", "POST"))
def update(id):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (id,)).fetchone()

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]

        conn.execute(
            "UPDATE users SET name = ?, email = ? WHERE id = ?", (name, email, id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    conn.close()
    return render_template("update.html", user=user)


@app.route("/delete/<int:id>", methods=("POST",))
def delete(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM users WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
