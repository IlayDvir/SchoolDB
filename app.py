from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

# Database connection
db = mysql.connector.connect(
    port = 3306,
    host = "10.4.50.156",
    user="root",
    password="BestPassword",
    database="University"
)

def get_grades():
    """Fetch grades from the database."""
    # print(f"Username: {session.get('username')}")
    # print(f"Password: {session.get('password')}")
    # print(f"Student ID: {session.get('ID')}")
    
    # Ensure Student ID is available
    student_id = session.get('ID')
    if not student_id:
        raise ValueError("Student ID not found in session")

    try:
        cursor = db.cursor(dictionary=True)

        query = """
            SELECT 
                s.Course_ID,
                c.Description,
                st.Grade
            FROM 
                Stud_Takes st
            JOIN 
                Sections s ON st.Section_ID = s.Section_ID
            JOIN 
                Courses c ON s.Course_ID = c.Course_ID
            WHERE 
                st.Student_ID = %s;
        """
        
        cursor.execute(query, student_id)
        grades = cursor.fetchall()
        print(grades)
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

        checkdatabase = "SELECT Security_Level FROM Accounts WHERE Security_Level > 0 AND Username = %s AND Password = %s;"
        data = (user, pas)

        cursor = db.cursor()
        cursor.execute(checkdatabase, data)

        if cursor.fetchone():
            return redirect(url_for('faculty_page'))
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
    checkdatabase = "select Security_Level from Accounts where Security_Level=0 and Username = %s and Password=%s;"
    data = (user, pas)

    cursor = db.cursor()
    cursor.execute(checkdatabase, data)
    
    if cursor.fetchone():
            cursor.close()
            checkdatabase = "select ID from Accounts where Username = %s and Password=%s;"
            cursor = db.cursor()
            cursor.execute(checkdatabase, data)
            session['ID'] = cursor.fetchone()
            print(session['ID'])
            return redirect(url_for('students'))
    else:
        print(user,pas)
        print("Here")
        flash('Invalid username or password. Please try again.')
        return redirect(url_for('checkaccstu'))

    
    # Render the form on a GET request
    return render_template('student-login.html')
    

@app.route('/students')
def students():
    grades = get_grades()
    return render_template('Studentpage.html', grades=grades)

@app.route('/faculty', methods=['GET', 'POST'])
def faculty_page():
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        # Handle enroll, drop or grade update
        student_id = request.form['student_id']
        course_id = request.form['course_id']
        section_id = request.form['section_id']

        action = request.form['action']
        grade = request.form.get('grade')  # use .get() to handle missing grades

        # Check that grade is provided if the action is 'update_grade'
        if action == 'update_grade' and not grade:
            # If the action is to update the grade, but no grade was provided, handle the case
            return render_template('Facutlypage.html', message="Grade is required for grade update!")

        try:
            if action == 'enroll':
                # Check if course_id and student_id are valid before enrolling
                cursor.execute("""
                    INSERT INTO Stud_Takes (Section_ID, Student_ID, Grade, Grade_Status)
                    VALUES (%s, %s, %s, 'Enrolled')
                """, (section_id, student_id, grade))
                db.commit()

            elif action == 'drop':
                # Drop student from course
                cursor.execute("""
                    DELETE FROM Stud_Takes
                    WHERE Student_ID = %s AND Section_ID = %s
                """, (student_id, section_id))
                db.commit()

            elif action == 'update_grade':
                print("Grade = " + grade  + " Student ID = " + student_id + " Course ID = " + course_id)
                # Update student's grade
                Query = "Update Stud_Takes Set Grade = %s Where Student_ID = %s AND Section_ID = %s"
                Data = (grade, student_id, section_id)
                cursor.execute(Query,Data)
                db.commit()

            return redirect(url_for('faculty_page'))

        except mysql.connector.Error as err:
            # Handle any database errors
            db.rollback()
            return render_template('Facutlypage.html', message=f"Error: {err}")

    # Fetch all courses for faculty
    cursor.execute("SELECT * FROM Courses")
    courses = cursor.fetchall()

    # Fetch all students currently enrolled in courses taught by the faculty
    cursor.execute("""
        SELECT st.Student_ID, s.First_Name, s.Last_Name, st.Grade, c.Course_ID, c.Description, sec.Section_ID
        FROM Stud_Takes st
        JOIN Sections sec ON st.Section_ID = sec.Section_ID
        JOIN Courses c ON sec.Course_ID = c.Course_ID
        JOIN Students s ON st.Student_ID = s.Student_ID
        
    """)  # <-- Ensure session['ID'] is passed as a tuple
    enrolled_students = cursor.fetchall()

    cursor.execute("SELECT * FROM Sections")
    sections = cursor.fetchall()
    cursor.close()

    return render_template('Facutlypage.html', courses=courses, enrolled_students=enrolled_students, sections=sections)

@app.route('/StudentDetails', methods=['GET', 'POST'])
def advisor():
    cursor = db.cursor(dictionary=True)
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        # Handle enroll, drop or grade update
        student_id = request.form['student_id']
        course_id = request.form['course_id']
        section_id = request.form['section_id']

        action = request.form['action']
        grade = request.form.get('grade')  # use .get() to handle missing grades

        # Check that grade is provided if the action is 'update_grade'
        if action == 'update_grade' and not grade:
            # If the action is to update the grade, but no grade was provided, handle the case
            return render_template('Facutlypage.html', message="Grade is required for grade update!")

        try:
            if action == 'enroll':
                # Check if course_id and student_id are valid before enrolling
                cursor.execute("""
                    INSERT INTO Stud_Takes (Section_ID, Student_ID, Grade, Grade_Status)
                    VALUES (%s, %s, %s, 'Enrolled')
                """, (section_id, student_id, grade))
                db.commit()

            elif action == 'drop':
                # Drop student from course
                cursor.execute("""
                    DELETE FROM Stud_Takes
                    WHERE Student_ID = %s AND Section_ID = %s
                """, (student_id, section_id))
                db.commit()

            elif action == 'update_grade':
                print("Grade = " + grade  + " Student ID = " + student_id + " Course ID = " + course_id)
                # Update student's grade
                Query = "Update Stud_Takes Set Grade = %s Where Student_ID = %s AND Section_ID = %s"
                Data = (grade, student_id, section_id)
                cursor.execute(Query,Data)
                db.commit()

            return redirect(url_for('faculty_page'))

        except mysql.connector.Error as err:
            # Handle any database errors
            db.rollback()
            return render_template('Facutlypage.html', message=f"Error: {err}")

    # Fetch all courses for faculty
    cursor.execute("SELECT * FROM Courses")
    courses = cursor.fetchall()

    # Fetch all students currently enrolled in courses taught by the faculty
    cursor.execute("""
        SELECT st.Student_ID, s.First_Name, s.Last_Name, st.Grade, c.Course_ID, c.Description, sec.Section_ID
        FROM Stud_Takes st
        JOIN Sections sec ON st.Section_ID = sec.Section_ID
        JOIN Courses c ON sec.Course_ID = c.Course_ID
        JOIN Students s ON st.Student_ID = s.Student_ID
        
    """)  # <-- Ensure session['ID'] is passed as a tuple
    enrolled_students = cursor.fetchall()

    cursor.execute("SELECT * FROM Sections")
    sections = cursor.fetchall()
    cursor.close()

    return render_template('Facutlypage.html', courses=courses, enrolled_students=enrolled_students, sections=sections)


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
