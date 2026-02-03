from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

DB_NAME = "budget_manager.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Expenses table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        date TEXT NOT NULL,
        category TEXT NOT NULL,
        user_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()


@app.get("/api/health")
def health_check():
    return jsonify({"status": "OK"}), 200


@app.post("/api/register")
def register():
    data = request.get_json() #retrieving data sent from the user
    print(data)
    name = data.get("name")
    email = data.get("email")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute( "INSERT INTO users (name, email) VALUES (?, ?)",(name, email))
    conn.commit()
    conn.close()

    return jsonify({"message": "User registered successfully"}), 201


@app.get("/api/users")
def get_users():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, email FROM users")
    rows = cursor.fetchall()
    conn.close()

    users = [
        {"id": row["id"], 
        "name": row["name"], 
        "email": row["email"
        ]}
        for row in rows
    ]

    return jsonify({
        "success": True,
        "message": "Users retrieved successfully",
        "data": users
    }), 200


@app.get("/api/users/<int:user_id>")
def get_user_by_id(user_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, email FROM users WHERE id=?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({"success": False, "message": "User not found"}), 404

    return jsonify({
        "success": True,
        "data": {
            "id": row["id"],
            "name": row["name"],
            "email": row["email"]
        }
    }), 200


@app.put("/api/users/<int:user_id>")
def update_user(user_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE id=?", (user_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"error": "User not found"}), 404

    cursor.execute("""
        UPDATE users
        SET
            name = COALESCE(?, name),
            email = COALESCE(?, email),
            password = COALESCE(?, password)
        WHERE id = ?
    """, (
        data.get("name"),
        data.get("email"),
        data.get("password"),
        user_id
    ))

    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "User updated successfully"}), 200


@app.delete("/api/users/<int:user_id>")
def delete_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE id=?", (user_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"success": False, "message": "User not found"}), 404

    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "User deleted successfully"}), 200

@app.post("/api/expenses")
def create_expense():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    title = data.get("title")
    description = data.get("description")
    amount = data.get("amount")
    date = data.get("date")
    category = data.get("category")
    user_id = data.get("user_id")

    if not description or amount is None or not date or not category or not user_id:
        return jsonify({
            "error": "description, amount, date, category, and user_id are required"
        }), 400

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute("SELECT id FROM users WHERE id=?", (user_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"error": "User not found"}), 404

    cursor.execute("""
        INSERT INTO expenses (title, description, amount, date, category, user_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title, description, amount, date, category, user_id))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Expense created successfully"
    }), 201



if __name__ == "__main__":
    init_db()
    app.run(debug=True)