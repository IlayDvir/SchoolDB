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
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM my_table")
    result = cursor.fetchall()
    return render_template('index.html', data=result)

if __name__ == '__main__':
    app.run(debug=True)
