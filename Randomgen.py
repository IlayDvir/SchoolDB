import mysql.connector

# Database connection
db = mysql.connector.connect(
    port = 3306,
    host = "10.4.109.189",
    user="root",
    password="BestPassword",
    database="University"
)

cursor = db.cursor()

try:
    # Insert 1,000 courses and sections
    for i in range(1, 1001):
        course_id = 50000 + i  # Unique course IDs starting from 50001
        description = f"Course {i}: Advanced Concepts"
        credit = 3  # Example credit value
        academic_calendar = "Undergrad"

        # Insert the course
        cursor.execute("""
            INSERT INTO Courses (Course_ID, Description, Credit, Academic_Career)
            VALUES (%s, %s, %s, %s)
        """, (course_id, description, credit, academic_calendar))

        # Create the section
        section_id = 60000 + i  # Unique section IDs starting from 60001
        days_offered = "MWF" if i % 2 == 0 else "TR"  # Alternate days
        capacity = 30 + (i % 3) * 10  # Vary capacity between 30, 40, and 50
        time_start = "09:00" if i % 2 == 0 else "10:30"  # Alternate start times
        time_end = "10:15" if i % 2 == 0 else "11:45"  # Alternate end times
        room = f"Room {chr(65 + (i % 5))}"  # Alternate between Room A, B, C, etc.
        semester = "Fall" if i % 2 == 0 else "Spring"  # Alternate semesters
        year = 2024
        professor_id = 10003

        # Insert into the Sections table
        cursor.execute("""
            INSERT INTO Sections (Section_ID, Days_Offered, Capacity, Time_Start, Time_End, Room, Semester, Year, Course_ID, Professor_ID)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (section_id, days_offered, capacity, time_start, time_end, room, semester, year, course_id, professor_id))

    db.commit()
    print("Successfully added 1,000 courses and linked sections to Professor_ID 10003")

except mysql.connector.Error as err:
    print(f"Error: {err}")
    db.rollback()

finally:
    cursor.close()
    db.close()