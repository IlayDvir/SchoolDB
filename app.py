from flask import Flask, render_template
from flask import Flask, request
from flask import Flask, render_template, request, redirect, url_for


import mysql.connector

app = Flask(__name__)

# Database connection
db = mysql.connector.connect(
    port = 3306,
    host = "10.4.56.134",
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

@app.route('/insertstudent', methods=['POST'])
def insertstudent():


    id = request.form.get('ID')
    name = request.form.get('name')
    age = request.form.get('Age')
    insert_query = "INSERT INTO my_table (id, name, age) VALUES (%s, %s, %s)"
    data = (id, name, age)

    # Use the data as needed
    #+str(name)+", "
    cursor = db.cursor(dictionary=True)
    cursor.execute(insert_query, data)

    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
