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

#--------Health-----------
@app.get("/api/health")
def health_check():
    return jsonify({"status": "OK"}), 200

#--------Register-----------
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

#--------Users (GET)-----------
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

#--------Users(GET)(param)-----------
#http://127.0.0.1:5000/api/users/2
@app.get("/api/users/<int:user_id>") #RESTFUL
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

#--------Users(PUT)(param)-----------
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

#--------Users(DELETE)(user_id)-----------
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

#-------------EXPENSE(POST)---------------
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

#-------------EXPENSE(GET)---------------
@app.get("/api/expenses")
def get_expenses():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            title,
            description,
            amount,
            date,
            category,
            user_id
        FROM expenses
    """)
    rows = cursor.fetchall()
    conn.close()

    expenses = [
        {
            "id": row["id"],
            "title": row["title"],
        #   "description": row["description"],
        #   "amount": row["amount"],
        # "date": row["date"],
            "category": row["category"], 
            "user_id": row["user_id"]
        }
        for row in rows
    ]

    return jsonify({
        "success": True,
        "data": expenses,
        "message": "expenses retrieved sucessfully"
    }), 200

#-------------EXPENSE(GET)(user_id)---------------
@app.route("/api/expenses/<int:expense_id>")
def get_expense(expense_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses WHERE id = ?",(expense_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({
            "success": False,
            "message": "Expense not found"
        }), 404

    return jsonify({
        "success": True,
        "message": "Expense retrieved successfully",
        "data": dict(row)
    }), 200

#-------------EXPENSE(Delete)(user_id)---------------
@app.put("/api/expenses/<int:expense_id>")
def update_expense_by_id(expense_id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data found"}), 400

    title = data.get("title")
    description = data.get("description")
    amount = data.get("amount")
    date_str = data.get("date")
    category = data.get("category")
    user_id = data.get("user", {}).get("id")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE expenses
            SET title = ?, description = ?, amount = ?, date = ?, category = ?, user_id = ?
            WHERE id = ?
        """, (title, description, amount, date_str, category, user_id, expense_id))

        conn.commit()

       
        if cursor.rowcount == 0:
            return jsonify({
                "error": "Expense not found"
            }), 404

        return jsonify({
            "success": True,
            "message": "Expense updated successfully"
        }), 200

    except sqlite3.IntegrityError as e:
        return jsonify({"error": f"Something went wrong: {str(e)}"}), 400

    except sqlite3.OperationalError as e:
        return jsonify({"error": f"Database Operational Error: {str(e)}"}), 500

    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    app.run(debug=True)