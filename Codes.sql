use University;

-- create table Accounts
-- 	(Username			varchar(15),
-- 	 Password		    varchar(50),
-- 	 Security_Level			int(1),
--      ID					int(9),
-- 	 primary key (ID)
--     );
    

    
-- create table Courses
-- 	(Course_ID			int(9),
-- 	 Description	    varchar(100),
-- 	 Credit				int(1),
-- 	 Academic_Career	varchar(20),
-- 	 primary key (Course_ID)
--     );
    
-- create table PreCo
-- 	(Course_ID			int(9),
--      Req_ID				int(9),
-- 	 Type				varchar(3),
-- 	 primary key (Course_ID, Req_ID, Type),
--      foreign key (Req_ID) references Courses(Course_ID) 
--     );
    
-- create table Employees
-- 	(Employee_ID		int(9),
--      Security_Level		int(1),
-- 	 Type				varchar(3),
--      Name 				varchar(15),
--      Role				varchar(15),
-- 	 primary key (Employee_ID),
--      foreign key (Employee_ID) references Accounts(ID) 
-- 		on delete cascade
--     );
    
    
    
-- create table Students
-- 	(Student_ID			int(9),
--      Birthday			DATE,
-- 	 Address			varchar(50),
--      First_Name 		varchar(15),
--      Middle 			char(1),
--      Last_Name 			varchar(15),
--      Role				varchar(15),
--      Grad_Year			YEAR,
--      Email				varchar(50),
--      Gender				varchar (10),
--      Ethnicity			varchar(16),
--      Phone_Number		int,
--      Plan				varchar(40),
--      Major				varchar(15),
--      Minor				varchar(15),
--      Advisor_ID			int(9),
--      
-- 	 primary key (Student_ID),
--      foreign key (Advisor_ID) references Employees(Employee_ID) 
-- 		on delete cascade
--     );

-- create table Billing_Info
-- 	(	
-- 		ID				int(9),
--         Billing_Address	varchar(50),
--         Paid			float,
--         Due				float,
--         Total			float,
--         Bank_num		int,
--         
-- 	 primary key (ID, Billing_Address, Paid, Due, Total, Bank_Num),
--      foreign key (ID) references Students(Student_ID) 
-- 		on delete cascade
--     );

-- create table Emergancy_Contact
-- 	(	
-- 		ID				int(9),
--         Contact_Name	varchar(15),
--         NumberPhone		int,
--         Email			varchar(50),
--         
-- 	 primary key (NumberPhone),
--      foreign key (ID) references Students(Student_ID) 
--     );

-- create table Professors
-- 	(	
-- 		ID				int(9),
--         Name			varchar(15),
--         Type			varchar(15),
--         Email			varchar(50),
--         
-- 	 primary key (ID, Name, Type, Email),
--      foreign key (ID) references Employees(Employee_ID) 
-- 		on delete cascade
--     );

-- create table Sections
-- 	(	
-- 		Section_ID		int(9),
--         Days_Offered	varchar(15),
--         Capacity		int,
--         Time_Start 		varchar(15),
-- 		Time_End 		varchar(15),	
-- 		Room 			varchar(15),
--         Open_Seats		int,
--         Semester		varchar(20),
--         Year			year,
-- 		Course_ID		int(9),
--         Professor_ID	int(9),
--         
-- 	 primary key (Section_ID),
--      foreign key (Course_ID) references Courses(Course_ID) 
-- 		on delete cascade,
-- 	foreign key (Professor_ID) references Professors(ID) 
-- 		on delete cascade
--     );


create table Stud_Takes
	(Section_ID			int(9),
	 Student_ID		    int(9),
	 Grade				char(1),
	 Grade_Status		varchar(15),
	 primary key (Section_ID, Student_ID),
     foreign key (Section_ID) references Sections(Section_ID) 
		on delete cascade,
	 foreign key (Student_ID) references Students(Student_ID) 
		on delete cascade
    );