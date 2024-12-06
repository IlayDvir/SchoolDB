from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

# Database connection
db = mysql.connector.connect(
    port = 3306,
    host = "192.168.1.61",
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
        level = cursor.fetchone()[0]
        print(level)
        if level:
            cursor.close()
            checkdatabase = "select ID from Accounts where Username = %s and Password=%s;"
            cursor = db.cursor()
            cursor.execute(checkdatabase, data)
            session['ID'] = cursor.fetchone()
            if level==2:
                return redirect(url_for('faculty_page'))
            else:
                return redirect(url_for('professor'))
        else:
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

@app.route('/professor', methods=['POST', 'GET'])
def professor():
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        Student_ID = request.form.get('student_id')
        Grade = request.form.get('grade')
        Section_ID = request.form.get('section_id')

        Query = "Update Stud_Takes Set Grade = %s Where Student_ID = %s AND Section_ID = %s"
        Data = (Grade, Student_ID, Section_ID)
        cursor.execute(Query,Data)
        db.commit()
        return redirect(url_for('professor'))


    query = "Select * from Sections s, Courses c where Professor_ID = %s AND s.Course_ID = c.Course_ID"
    cursor.execute(query, session['ID'])
    courses = cursor.fetchall()

    cursor.execute("""
        SELECT Count(DISTINCT st.Student_ID) as total_students
        FROM  Stud_Takes st, Sections s
        Where s.Professor_ID=%s AND s.Section_ID=st.Section_ID
    """, (session['ID']))  # <-- Ensure session['ID'] is passed as a tuple
    total_students = cursor.fetchone()['total_students']

    cursor.execute("""
    SELECT 
        s.Student_ID, 
        s.First_Name, 
        s.Middle, 
        s.Last_Name, 
        GROUP_CONCAT(CONCAT(sec.Section_ID, ' (Grade: ', st.Grade, ')') ORDER BY sec.Section_ID ASC SEPARATOR ', ') AS Section_ID
    FROM 
        Students s
    LEFT JOIN 
        Stud_Takes st ON s.Student_ID = st.Student_ID
    LEFT JOIN 
        Sections sec ON st.Section_ID = sec.Section_ID
    WHERE sec.Professor_ID = %s
    GROUP BY 
        s.Student_ID, s.First_Name, s.Middle, s.Last_Name
    ORDER BY 
        s.Student_ID ASC;
    """, (session['ID']))  # <-- Ensure session['ID'] is passed as a tuple
    list_student = cursor.fetchall()

    return render_template('professor.html', list_student=list_student, total_students=total_students, courses=courses, professor_id=session['ID'])

@app.route('/enroll', methods=['GET', 'POST'])
def enroll():
    cursor = db.cursor(dictionary=True)
    student_id = int(session['ID'][0])

    if request.method == 'POST':
        if 'enroll' in request.form:  
            section_id = request.form.get('section_id')
            cursor.execute("""
                SELECT COUNT(*) AS Prereq_Satisfied
                FROM PreCo pc
                JOIN Stud_Takes st ON pc.Req_ID = st.Section_ID
                WHERE pc.Type = 'PRE'
                AND pc.Course_ID = (SELECT Course_ID FROM Sections WHERE Section_ID = %s)
                AND st.Student_ID = %s
                AND st.Grade IN ('A', 'B', 'C')
            """, (section_id, student_id))

            countpre = cursor.fetchone()
            print(countpre)
            cursor.execute("""
                SELECT COUNT(*) AS Prereq_Satisfied
                FROM PreCo pc
                WHERE pc.Type = 'PRE'
                AND pc.Course_ID = (SELECT Course_ID FROM Sections WHERE Section_ID = %s)
            """, (section_id,))

            prereq_satisfied = cursor.fetchone()==countpre
            print(prereq_satisfied)
            # Check corequisites
            cursor.execute("""
                SELECT COUNT(*) AS Coreq_Satisfied
                FROM PreCo pc
                LEFT JOIN Stud_Takes st ON pc.Req_ID = st.Section_ID AND st.Student_ID = %s
                WHERE pc.Type = 'CO'
                AND pc.Course_ID = (SELECT Course_ID FROM Sections WHERE Section_ID = %s)
                AND (st.Section_ID IS NOT NULL OR EXISTS (
                    SELECT 1
                    FROM Stud_Takes st2
                    WHERE st2.Student_ID = %s AND st2.Section_ID = pc.Req_ID
                ))
            """, (student_id, section_id, student_id))
            k=cursor.fetchone()
            coreq_satisfied = k['Coreq_Satisfied']

            # Enrollment decision
            if not prereq_satisfied:
                    print("Enrollment failed: Prerequisites not met.")
            elif coreq_satisfied != 0:
                print("Enrollment failed: Corequisites not met.")
            else:
                try:

                    # Enroll the student
                    section_id = request.form['section_id']
                    print(section_id)
                    cursor.execute("""
                        INSERT INTO Stud_Takes (Section_ID, Student_ID, Grade, Grade_Status)
                        VALUES (%s, %s, 'N', 'Enrolled')
                    """, (int(section_id), int(student_id)))
                    
                    db.commit()
                    print("Enrollment successful!")
                except:
                    print("Enrollment failed: Database error.")
                    db.rollback()
    elif request.method == 'GET':
        search = request.args.get('search')
        sort_by = request.args.get('sort_by', 'Open_Seats')
        ascde = request.args.get('ascde', 'ASC')
        semester = request.args.get('semester', 'Fall')
        year = request.args.get('year', '2024')
        print(search)
        # Handle year filter dynamically
        where_clauses = [f"s.Semester = %s"]
        query_params = [semester]

        if search:
            where_clauses.append(f"(c.Course_ID LIKE %s OR c.Description LIKE %s OR p.Name LIKE %s)")
            query_params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
        
        # Only add the year condition if it is not empty
        if year and year != 'All':  # Assuming 'All' means no specific filter for year
            where_clauses.append(f"s.Year = %s")
            query_params.append(year)

        # Construct the ORDER BY clause
        if sort_by == 'Course_ID':
            order_by = 'c.Course_ID'
        elif sort_by == 'Open_Seats':
            order_by = '(s.Capacity - COUNT(st.Student_ID))'  # Calculating open seats
        elif sort_by == 'Time_Start':
            order_by = 's.Time_Start'
        else:
            order_by = 'Open_Seats'  # Default order if none is selected
        
        # Determine the sorting direction
        order_direction = ascde if ascde in ['ASC', 'DESC'] else 'ASC'

        # Build the complete SQL query
        where_clause = ' AND '.join(where_clauses)  # Join the where conditions
        print(where_clause)
        sql_query = f"""
            SELECT 
                s.Section_ID, 
                c.Course_ID, 
                s.Days_Offered, 
                (s.Capacity - COUNT(st.Student_ID)) AS Open_Seats, 
                s.Time_Start, 
                s.Time_End, 
                s.Room,  
                s.Semester, 
                s.Year, 
                p.Name, 
                c.Description
            FROM 
                Sections s
            LEFT JOIN 
                Stud_Takes st ON s.Section_ID = st.Section_ID
            JOIN 
                Courses c ON s.Course_ID = c.Course_ID
            JOIN 
                Professors p ON s.Professor_ID = p.ID
            WHERE 
                {where_clause}
            GROUP BY 
                s.Section_ID, 
                c.Course_ID, 
                s.Days_Offered, 
                s.Capacity, 
                s.Time_Start, 
                s.Time_End, 
                s.Room, 
                s.Semester, 
                s.Year, 
                p.Name, 
                c.Description
            ORDER BY 
                {order_by} {order_direction};
        """

        # Execute the query
        cursor.execute(sql_query, tuple(query_params))
        available_courses = cursor.fetchall()

        # Return the results to the template
    return render_template('enroll.html', available_courses=available_courses, sort_by=sort_by, ascde=ascde, semester=semester, year=year)
    

@app.route('/students', methods=['GET', 'POST'])
def students():
    grades = get_grades()
    student_id = int(session['ID'][0])
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        if 'update_student' in request.form:
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            address = request.form['address']
            phone_number = request.form['phone_number']
            major = request.form['major']
            minor = request.form['minor']

            cursor.execute("""
                UPDATE Students
                SET First_Name = %s, Last_Name = %s, Email = %s, Address = %s,
                    Phone_Number = %s, Major = %s, Minor = %s
                WHERE Student_ID = %s
            """, (first_name, last_name, email, address, phone_number, major, minor, student_id))
            db.commit()

        # Update Emergency Contact Information
        elif 'update_emer' in request.form:
            contact_name = request.form['contact_name']
            contact_phone = request.form['contact_phone']
            contact_email = request.form['contact_email']
            
            cursor.execute("""
                UPDATE Emergancy_Contact
                SET Contact_Name = %s, NumberPhone = %s, Email = %s
                WHERE ID = %s
            """, (contact_name, contact_phone, contact_email, student_id))
            db.commit()
        elif 'cupdate' in request.form:
            section_id = request.form['section_id']
            cursor.execute("""
                SELECT COUNT(*) AS Prereq_Satisfied
                FROM PreCo pc
                JOIN Stud_Takes st ON pc.Req_ID = st.Section_ID
                WHERE pc.Type = 'PRE'
                AND pc.Course_ID = (SELECT Course_ID FROM Sections WHERE Section_ID = %s)
                AND st.Student_ID = %s
                AND st.Grade IN ('A', 'B', 'C')
            """, (section_id, student_id))

            countpre = cursor.fetchone()
            print(countpre)
            cursor.execute("""
                SELECT COUNT(*) AS Prereq_Satisfied
                FROM PreCo pc
                WHERE pc.Type = 'PRE'
                AND pc.Course_ID = (SELECT Course_ID FROM Sections WHERE Section_ID = %s)
            """, (section_id,))

            prereq_satisfied = cursor.fetchone()==countpre
            print(prereq_satisfied)
            # Check corequisites
            cursor.execute("""
                SELECT COUNT(*) AS Coreq_Satisfied
                FROM PreCo pc
                LEFT JOIN Stud_Takes st ON pc.Req_ID = st.Section_ID AND st.Student_ID = %s
                WHERE pc.Type = 'CO'
                AND pc.Course_ID = (SELECT Course_ID FROM Sections WHERE Section_ID = %s)
                AND (st.Section_ID IS NOT NULL OR EXISTS (
                    SELECT 1
                    FROM Stud_Takes st2
                    WHERE st2.Student_ID = %s AND st2.Section_ID = pc.Req_ID
                ))
            """, (student_id, section_id, student_id))
            k=cursor.fetchone()
            print(k)
            coreq_satisfied = k['Coreq_Satisfied']

            # Enrollment decision
            if not prereq_satisfied:
                 print("Enrollment failed: Prerequisites not met.")
            elif coreq_satisfied != 0:
                print("Enrollment failed: Corequisites not met.")
            else:
                  try:

                    # Enroll the student
                    section_id = request.form['section_id']
                    print(section_id)
                    cursor.execute("""
                        INSERT INTO Stud_Takes (Section_ID, Student_ID, Grade, Grade_Status)
                        VALUES (%s, %s, 'N', 'Enrolled')
                    """, (int(section_id), int(student_id)))
                    
                    db.commit()
                    print("Enrollment successful!")
                  except:
                      print("Enrollment failed: Database error.")
                      db.rollback()



    # Fetch the current emergency contact details
    cursor.execute("""
        SELECT Contact_Name, NumberPhone, Email
        FROM Emergancy_Contact
        WHERE ID = %s
    """, (student_id, ))
    contact_info = cursor.fetchone()

    cursor.execute("""
        SELECT Billing_Address, Paid, Due, Total, Bank_num
        FROM Billing_Info
        WHERE ID = %s
    """, (student_id,))
    billing_info = cursor.fetchall()

    cursor.execute("""
        SELECT First_Name, Last_Name, Email, Address, Phone_Number, Major, Minor
        FROM Students
        WHERE Student_ID = %s
    """, (student_id,))
    student_info = cursor.fetchone()


    

    cursor.close()

    return render_template('Studentpage.html',  grades=grades, contact_info=contact_info, billing_info=billing_info, student_info=student_info)

@app.route('/faculty', methods=['GET', 'POST'])
def faculty_page():
    print(session['ID'][0])
    cursor = db.cursor(dictionary=True)
    advisor_id=session['ID']
    if request.method == 'POST':
        # Handle enroll, drop or grade update
        student_id = request.form['student_id']
        course_id = request.form.get('course_id')
        action = request.form['action']
        grade = request.form.get('grade')  # use .get() to handle missing grades
        course_id=str.split(course_id)
        cursor.execute("""
SELECT 
    (s.Capacity - COUNT(st.Student_ID)) AS Open_Seats, s.Capacity 
FROM 
    Sections s, Stud_Takes as st
WHERE
    s.Section_ID = %s AND s.Section_ID=st.Section_ID;""", (course_id[0],))
        
        open_seat = cursor.fetchall()
        try:
                if action == 'enroll' and str(open_seat[0]['Open_Seats']) == "None" or open_seat[0]['Open_Seats']>0:
                    # Check if course_id and student_id are valid before enrolling

                    cursor.execute("""
                        INSERT INTO Stud_Takes (Section_ID, Student_ID, Grade, Grade_Status)
                        VALUES (%s, %s, 'N', 'Enrolled')
                    """, (course_id[0], student_id))
                    db.commit()

                elif action == 'drop':
                    # Drop student from course
                    print(student_id)
                    cursor.execute("""
                        DELETE FROM Stud_Takes
                        WHERE Student_ID = %s AND Section_ID = %s
                    """, (student_id, course_id[0]))
                    db.commit()

                elif action == 'update_grade':
                    # Update student's grade
                    Query = "Update Stud_Takes Set Grade = %s Where Student_ID = %s AND Section_ID = %s"
                    Data = (grade, student_id, course_id[0])
                    cursor.execute(Query,Data)
                    db.commit()


        except mysql.connector.Error as err:
                # Handle any database errors
                db.rollback()
                print(err)

    # Fetch all courses for faculty
    cursor.execute("SELECT * FROM Courses C,Sections S Where S.Course_ID=C.Course_ID")
    courses = cursor.fetchall()

    # Fetch all students currently enrolled in courses taught by the faculty
    cursor.execute("""
        SELECT st.Student_ID, s.First_Name, s.Last_Name, st.Grade, c.Course_ID, c.Description, sec.Section_ID
        FROM Stud_Takes st
        JOIN Sections sec ON st.Section_ID = sec.Section_ID
        JOIN Courses c ON sec.Course_ID = c.Course_ID
        JOIN Students s ON st.Student_ID = s.Student_ID
        Where s.Advisor_ID=%s
        ORDER BY st.Student_ID
    """, (advisor_id))  # <-- Ensure session['ID'] is passed as a tuple
    enrolled_students = cursor.fetchall()

    cursor.execute("SELECT * FROM Sections")
    sections = cursor.fetchall()
    print(sections)

    cursor.execute("""
        SELECT Count(Student_ID) as total_students
        FROM Students s
        Where s.Advisor_ID=%s
    """, (advisor_id))  # <-- Ensure session['ID'] is passed as a tuple
    total_students = cursor.fetchone()['total_students']


    cursor.close()

    return render_template('Facutlypage.html', total_students=total_students, courses=courses, enrolled_students=enrolled_students, sections=sections)


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
