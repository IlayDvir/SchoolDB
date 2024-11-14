from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Database connection
db = mysql.connector.connect(
    port = 3306,
    host = "10.4.26.236",
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
        #print("Database Query Result:", result)  # Debug line
        return render_template('index.html', data=result)
    except Exception as e:
        print(f"Error: {e}")  # Print error to console
        return f"An error occurred: {e}"

@app.route('/employee-login')
def employee_login():
    return render_template('employee-login.html')

@app.route('/student-login')
def student_login():
    return render_template('student-login.html')


@app.route('/insertstudent', methods=['POST'])
def insertstudent():
    id = request.form.get('ID')
    name = request.form.get('name')
    age = request.form.get('Age')
    insert_query = "INSERT INTO my_table (id, name, age) VALUES (%s, %s, %s)"
    data = (id, name, age)

    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute(insert_query, data)
        db.commit()  # Commit the transaction using the database connection
        return redirect(url_for('home'))
    except Exception as e:
        db.rollback()  # Rollback if there is an error
        print(f"Error: {e}")
        return f"An error occurred: {e}"


@app.route('/checkaccfaculty', methods=['POST'])
def checkaccfac():
    user = request.form.get('Username')
    pas = request.form.get('Password')
    checkdatabase = "select Security_Level from account where Security_Level>0 and Username = %s and Password=%s;"
    data = (user, pas)

    cursor = db.cursor()
    cursor.execute(checkdatabase, data)

    if cursor.fetchone():
        return(redirect(url_for('faculty')))
        print("LOGIN!")
    else:
        print("Not found!!")
        return redirect(url_for('home'))



@app.route('/checkaccstudents', methods=['POST'])
def checkaccstu():
    print("student")
    user = request.form.get('Username')
    pas = request.form.get('Password')
    checkdatabase = "select Security_Level from account where Security_Level=0 and Username = %s and Password=%s;"
    data = (user, pas)

    cursor = db.cursor()
    cursor.execute(checkdatabase, data)

    if cursor.fetchone():
        return(render_template('Studentpage.html'))
        print("LOGIN!")
    else:
        print("Not found!!")
        return redirect(url_for('home'))
    

@app.route('/students')
def students():
    print("here")
    return render_template('Studentpage.html')

@app.route('/faculty')
def faculty():
    return render_template('Facutlypage.html')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
