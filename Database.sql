-- 1. Create the test database
DROP DATABASE IF EXISTS face_db;
CREATE DATABASE face_db;
USE face_db;

-- 2. Admin Table
CREATE TABLE admin (
    Admin_ID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(50) UNIQUE NOT NULL,
    Password VARCHAR(100) NOT NULL
);

-- Insert default admin credentials
INSERT INTO admin (Username, Password) VALUES ('admin', 'admin');

-- 3. Teachers
CREATE TABLE teachers (
    Teacher_ID INT AUTO_INCREMENT PRIMARY KEY,
    Full_Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    Phone VARCHAR(20),
    Username VARCHAR(50) UNIQUE NOT NULL,
    Password VARCHAR(100) NOT NULL
);

-- 4. Courses
CREATE TABLE course (
    CourseID INT AUTO_INCREMENT PRIMARY KEY,
    CourseCode VARCHAR(10) UNIQUE NOT NULL,
    CourseName VARCHAR(100) NOT NULL,
    CreditHours INT NOT NULL           -- 1, 2, or 3 CH
);

-- 5. Sections
CREATE TABLE section (
    SectionID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(10) NOT NULL,           -- e.g., SEA, SEB
    Semester VARCHAR(10) NOT NULL,       -- e.g., 2nd, 5th
    Department VARCHAR(100) NOT NULL     -- e.g., Computer Science
);

-- 6. Students (Roll_no is the PRIMARY KEY now)
CREATE TABLE student (
    Roll_no VARCHAR(20) PRIMARY KEY,
    Full_Name VARCHAR(100) NOT NULL,
    SectionID INT NOT NULL,
    PhotoSample VARCHAR(100),
    FOREIGN KEY (SectionID) REFERENCES section(SectionID) ON DELETE CASCADE
);

-- 7. Enrollment Table
CREATE TABLE enrollment (
    Teacher_ID INT,
    CourseID INT,
    SectionID INT,
    PRIMARY KEY (Teacher_ID, CourseID, SectionID),
    FOREIGN KEY (Teacher_ID) REFERENCES teachers(Teacher_ID) ON DELETE CASCADE,
    FOREIGN KEY (CourseID) REFERENCES course(CourseID) ON DELETE CASCADE,
    FOREIGN KEY (SectionID) REFERENCES section(SectionID) ON DELETE CASCADE
);

-- 8. Lecture Table


-- 9. Attendance Table (uses Roll_no as foreign key)

CREATE TABLE attendance (
    AttendanceID INT AUTO_INCREMENT PRIMARY KEY,
    Teacher_ID INT,
    CourseID INT,
    SectionID INT,
    Roll_no VARCHAR(20),
    Attendance_Timestamp DATETIME NOT NULL,
    Status ENUM('Present', 'Absent') NOT NULL,
    FOREIGN KEY (Teacher_ID, CourseID, SectionID)
        REFERENCES enrollment(Teacher_ID, CourseID, SectionID)
        ON DELETE CASCADE,
    FOREIGN KEY (Roll_no) REFERENCES student(Roll_no) ON DELETE CASCADE
);




INSERT INTO section (Name, Semester, Department)
VALUES ('SEA', '4th', 'Computer Science');
INSERT INTO section (Name, Semester, Department)
VALUES ('SEB', '4th', 'Computer Science');

INSERT INTO student (Roll_no, Full_Name, SectionID, PhotoSample)
VALUES 
('23-NTU-CS-1200', 'Zain', 1, NULL),
('23-NTU-CS-1196', 'Talha', 1, NULL),
('23-NTU-CS-1213', 'Taha', 1, NULL);

INSERT INTO student (Roll_no, Full_Name, SectionID, PhotoSample)
VALUES 
('23-NTU-CS-1221', 'Ahmed', 2, NULL),
('23-NTU-CS-1222', 'Ali', 2, NULL),
('23-NTU-CS-1223', 'Hamza', 2, NULL);



INSERT INTO teachers (Full_Name, Email, Phone, Username, Password)
VALUES ('Kasloom', 'kasloom@ntu.edu.pk', '03001234567', 'kasloom', 'kas123');
INSERT INTO teachers (Full_Name, Email, Phone, Username, Password)
VALUES ('Abdul Qadir', 'qadir@ntu.edu.pk', '03111234567', 'qadir', 'qadir123');


INSERT INTO course (CourseCode, CourseName, CreditHours)
VALUES ('CS420', 'Construction', 3);
INSERT INTO course (CourseCode, CourseName, CreditHours)
VALUES ('CS430', 'Software Engineering', 3);
-- Kasloom teaches second course to SEA
INSERT INTO course (CourseCode, CourseName, CreditHours)
VALUES ('CS450', 'Design Patterns', 3);

-- Enrollment
-- Kasloom (Teacher_ID = 1), CS450 (CourseID = 3), SEA (SectionID = 1)
INSERT INTO enrollment (Teacher_ID, CourseID, SectionID)
VALUES (1, 3, 1);

-- Abdul Qadir (Teacher_ID = 2), CS430 (CourseID = 2), SEB (SectionID = 2)
INSERT INTO enrollment (Teacher_ID, CourseID, SectionID)
VALUES (2, 2, 2);


INSERT INTO enrollment (Teacher_ID, CourseID, SectionID)
VALUES (1, 1, 1);



-- For Construction (Kasloom, Teacher_ID = 1, CourseID = 1, SectionID = 1)
-- For Construction (Kasloom)
INSERT INTO attendance (Teacher_ID, CourseID, SectionID, Roll_no, Attendance_Timestamp, Status)
VALUES 
(1, 1, 1, '23-NTU-CS-1200', NOW(), 'Present'),
(1, 1, 1, '23-NTU-CS-1196', NOW(), 'Present'),
(1, 1, 1, '23-NTU-CS-1213', NOW(), 'Absent');

-- For Design Patterns (Kasloom, CourseID = 3)
INSERT INTO attendance (Teacher_ID, CourseID, SectionID, Roll_no, Attendance_Timestamp, Status)
VALUES 
(1, 3, 1, '23-NTU-CS-1200', NOW(), 'Present'),
(1, 3, 1, '23-NTU-CS-1196', NOW(), 'Absent'),
(1, 3, 1, '23-NTU-CS-1213', NOW(), 'Present');

-- For Software Engineering (Qadir, CourseID = 2, SectionID = 2)
INSERT INTO attendance (Teacher_ID, CourseID, SectionID, Roll_no, Attendance_Timestamp, Status)
VALUES 
(2, 2, 2, '23-NTU-CS-1221', NOW(), 'Present'),
(2, 2, 2, '23-NTU-CS-1222', NOW(), 'Absent'),
(2, 2, 2, '23-NTU-CS-1223', NOW(), 'Present');


SELECT 
    s.Roll_no,
    s.Full_Name,
    sec.Name AS Section,
    c.CourseName,
    a.Status,
    a.Attendance_Timestamp
FROM attendance a
JOIN student s ON a.Roll_no = s.Roll_no
JOIN course c ON a.CourseID = c.CourseID
JOIN teachers t ON a.Teacher_ID = t.Teacher_ID
JOIN section sec ON a.SectionID = sec.SectionID
WHERE t.Full_Name = 'Kasloom'
  AND c.CourseName = 'Construction'
  AND sec.Name = 'SEA'
  AND DATE(a.Attendance_Timestamp) = '2025-04-30';




