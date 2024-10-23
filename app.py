from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)

# Database connection
db = mysql.connector.connect(
    user="root",
    password="BestPassword",
    database="University"
)

@app.route('/')
def home():
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM my_table")
        result = cursor.fetchall()
        print("Database Query Result:", result)  # Debug line
        return render_template('index.html', data=result)
    except Exception as e:
        print(f"Error: {e}")  # Print error to console
        return f"An error occurred: {e}"

if __name__ == '__main__':
    app.run(debug=True)
