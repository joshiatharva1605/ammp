CREATE DATABASE manpower_db;
USE manpower_db;

CREATE TABLE login(
login_id INT AUTO_INCREMENT PRIMARY KEY,
username VARCHAR(50),
password VARCHAR(50),
role VARCHAR(20)
);

CREATE TABLE master_data(
part_id VARCHAR(20) PRIMARY KEY,
part_name VARCHAR(100),
station_A VARCHAR(10),
station_B VARCHAR(10),
station_C VARCHAR(10),
required_manpower INT,
skill_required VARCHAR(5)
);

CREATE TABLE employee(
emp_id VARCHAR(20) PRIMARY KEY,
emp_name VARCHAR(100),
skill VARCHAR(5)
);

CREATE TABLE attendance(
attendance_id INT AUTO_INCREMENT PRIMARY KEY,
emp_id VARCHAR(20),
date DATE,
status VARCHAR(20)
);

CREATE TABLE allocation(
allocation_id INT AUTO_INCREMENT PRIMARY KEY,
part_id VARCHAR(20),
station VARCHAR(10),
emp_id VARCHAR(20),
date DATE
);