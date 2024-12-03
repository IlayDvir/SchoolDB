import mysql.connector
import random

# Database connection setup
db = mysql.connector.connect(
    port = 3306,
    host = "10.4.50.156",
    user="root",
    password="BestPassword",
    database="University"
)

cursor = db.cursor()

# Fetch all student IDs
cursor.execute("SELECT Student_ID FROM Students")
students = cursor.fetchall()

# Fetch all course sections available (we'll assume students are enrolled in available sections)
cursor.execute("""
    SELECT Section_ID FROM Sections
""")
sections = cursor.fetchall()

# Function to enroll students
def enroll_students_in_courses():
    try:
        for student in students:
            student_id = student[0]

            # Select random number of courses for each student (e.g., 1 to 3 courses per student)
            num_courses = random.randint(1, 3)

            # Enroll the student in the selected courses
            selected_sections = random.sample(sections, num_courses)  # Randomly choose courses

            for section in selected_sections:
                section_id = section[0]

                # Insert into Stud_Takes to enroll the student
                cursor.execute("""
                    INSERT INTO Stud_Takes (Section_ID, Student_ID, Grade, Grade_Status)
                    VALUES (%s, %s, %s, 'Enrolled')
                """, (section_id, student_id, None))

        # Commit the changes
        db.commit()
        print("All students have been enrolled in courses successfully.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        db.rollback()

# Enroll students in courses
enroll_students_in_courses()

# Close the connection
cursor.close()
db.close()