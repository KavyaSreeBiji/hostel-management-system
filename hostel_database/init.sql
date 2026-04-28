-- Create the database
DROP DATABASE IF EXISTS hostel_db;
CREATE DATABASE hostel_db;
USE hostel_db;

-- 1. Rooms
CREATE TABLE Rooms (
    Room_ID INT PRIMARY KEY AUTO_INCREMENT,
    Capacity INT NOT NULL,
    Occupancy INT NOT NULL DEFAULT 0,
    Availability_Status VARCHAR(50) NOT NULL,
    Price DECIMAL(10, 2) NOT NULL DEFAULT 0.00
);

-- 2. Students
CREATE TABLE Students (
    Student_ID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    Phone VARCHAR(20),
    Password VARCHAR(255) NOT NULL,
    Room_ID INT,
    FOREIGN KEY (Room_ID) REFERENCES Rooms(Room_ID) ON DELETE SET NULL
);

-- 3. Billing
CREATE TABLE Billing (
    Bill_ID INT PRIMARY KEY AUTO_INCREMENT,
    Student_ID INT,
    Amount DECIMAL(10, 2) NOT NULL,
    Issue_Date DATE NOT NULL,
    Due_Date DATE NOT NULL,
    Status VARCHAR(50) NOT NULL,
    FOREIGN KEY (Student_ID) REFERENCES Students(Student_ID) ON DELETE CASCADE
);

-- 4. Admin
CREATE TABLE Admin (
    Admin_ID INT PRIMARY KEY AUTO_INCREMENT,
    Username VARCHAR(50) UNIQUE NOT NULL,
    Password VARCHAR(255) NOT NULL
);

-- Insert one Admin user for immediate login
INSERT INTO Admin (Username, Password) VALUES ('admin', 'admin123');

-- 5. Room_Requests
CREATE TABLE Room_Requests (
    Request_ID INT PRIMARY KEY AUTO_INCREMENT,
    Student_ID INT NOT NULL,
    Room_ID INT NOT NULL,
    Status VARCHAR(20) NOT NULL,
    FOREIGN KEY (Student_ID) REFERENCES Students(Student_ID) ON DELETE CASCADE,
    FOREIGN KEY (Room_ID) REFERENCES Rooms(Room_ID) ON DELETE CASCADE
);

-- 6. Complaints
CREATE TABLE Complaints (
    Complaint_ID INT PRIMARY KEY AUTO_INCREMENT,
    Student_ID INT NOT NULL,
    Category VARCHAR(50) NOT NULL,
    Description TEXT NOT NULL,
    Status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    FOREIGN KEY (Student_ID) REFERENCES Students(Student_ID) ON DELETE CASCADE
);
