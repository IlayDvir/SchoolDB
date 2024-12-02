from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

# Database connection
db = mysql.connector.connect(
    port = 3306,
    host = "10.4.104.252",
    user="root",
    password="BestPassword",
    database="University"
)

def get_grades():
    """Fetch grades from the database."""
    print(f"Username: {session.get('username')}")
    print(f"Password: {session.get('password')}")
    print(f"Student ID: {session.get('ID')}")
    
    # Ensure Student ID is available
    student_id = session.get('ID')
    if not student_id:
        raise ValueError("Student ID not found in session")

    try:
        # Connect to the database
        
        # Execute the query
        query = "SELECT Grade, Section_ID FROM Stud_Takes WHERE Student_ID = %s"
        cursor=db.cursor(dictionary=True)
        cursor.execute(query, student_id)

        
        # Fetch all results to prevent unread result error
        grades = cursor.fetchall()
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        grades = []
    
    finally:
        # Ensure all resources are cleaned up properly
        cursor.close()
    
    return grades


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

@app.route('/checkaccfaculty', methods=['POST', 'GET'])
def checkaccfac():
    if request.method == 'POST':
        user = request.form.get('Username')
        pas = request.form.get('Password')
        session['username'] = user
        session['password'] = pas

        checkdatabase = "SELECT Security_Level FROM account WHERE Security_Level > 0 AND Username = %s AND Password = %s;"
        data = (user, pas)

        cursor = db.cursor()
        cursor.execute(checkdatabase, data)

        if cursor.fetchone():
            return redirect(url_for('faculty'))
        else:
            print("Here")
            flash('Invalid username or password. Please try again.')
            return redirect(url_for('checkaccfac'))

    # Render the form on a GET request
    return render_template('employee-login.html')


@app.route('/checkaccstudents', methods=['POST'])
def checkaccstu():
    user = request.form.get('Username')
    pas = request.form.get('Password')
    session['username'] = user
    session['password'] = pas
    checkdatabase = "select Security_Level from account where Security_Level=0 and Username = %s and Password=%s;"
    data = (user, pas)
    

    cursor = db.cursor()
    cursor.execute(checkdatabase, data)
    
    if cursor.fetchone():
            cursor.close()
            checkdatabase = "select I_D from account where Username = %s and Password=%s;"
            cursor = db.cursor()
            cursor.execute(checkdatabase, data)
            session['ID'] = cursor.fetchone()
            print(session['ID'])
            return redirect(url_for('students'))
    else:
        print("Here")
        flash('Invalid username or password. Please try again.')
        return redirect(url_for('checkaccstu'))

    
    # Render the form on a GET request
    return render_template('student-login.html')
    

@app.route('/students')
def students():
    grades = get_grades()
    return render_template('Studentpage.html', grades=grades)

@app.route('/faculty')
def faculty():
    return render_template('Facutlypage.html')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
