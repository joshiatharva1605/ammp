DROP DATABASE IF EXISTS ammp_db;

CREATE DATABASE ammp_db;

USE ammp_db;

-- =====================================================
-- USERS TABLE
-- =====================================================

CREATE TABLE users (

```
user_id INT PRIMARY KEY AUTO_INCREMENT,

username VARCHAR(50) UNIQUE NOT NULL,

password VARCHAR(255) NOT NULL,

role VARCHAR(20) NOT NULL,

status VARCHAR(20) DEFAULT 'Active'
```

);

INSERT INTO users(username,password,role)
VALUES
('admin','admin123','admin'),
('supervisor','super123','supervisor');

-- =====================================================
-- PRODUCTS TABLE
-- =====================================================

CREATE TABLE products (

```
product_id INT PRIMARY KEY AUTO_INCREMENT,

machine_name VARCHAR(100) NOT NULL,

part_number VARCHAR(100) NOT NULL
```

);

-- =====================================================
-- MASTER DATA TABLE
-- =====================================================

CREATE TABLE master_data (

```
id INT PRIMARY KEY AUTO_INCREMENT,

product_id INT NOT NULL,

shop_name VARCHAR(100) NOT NULL,

station_name VARCHAR(100) NOT NULL,

required_manpower INT NOT NULL,

skill_required VARCHAR(20),

FOREIGN KEY(product_id)
REFERENCES products(product_id)
ON DELETE CASCADE
```

);

-- =====================================================
-- EMPLOYEE TABLE
-- =====================================================

CREATE TABLE employee (

```
emp_id VARCHAR(20) PRIMARY KEY,

emp_name VARCHAR(100) NOT NULL,

skill_level VARCHAR(20),

shift_name VARCHAR(20),

operator_type VARCHAR(30),

joining_date DATE,

mobile VARCHAR(15),

status VARCHAR(20) DEFAULT 'Active'
```

);

-- =====================================================
-- ATTENDANCE TABLE
-- =====================================================

CREATE TABLE attendance (

```
attendance_id INT PRIMARY KEY AUTO_INCREMENT,

emp_id VARCHAR(20),

date DATE,

status VARCHAR(20),

FOREIGN KEY(emp_id)
REFERENCES employee(emp_id)
ON DELETE CASCADE
```

);

-- =====================================================
-- ALLOCATION TABLE
-- =====================================================

CREATE TABLE allocation (

```
allocation_id INT PRIMARY KEY AUTO_INCREMENT,

emp_id VARCHAR(20),

master_data_id INT,

allocation_date DATE,

shift_name VARCHAR(20),

FOREIGN KEY(emp_id)
REFERENCES employee(emp_id)
ON DELETE CASCADE,

FOREIGN KEY(master_data_id)
REFERENCES master_data(id)
ON DELETE CASCADE
```

);

-- =====================================================
-- SHIFTS TABLE
-- =====================================================

CREATE TABLE shifts (

```
shift_id INT PRIMARY KEY AUTO_INCREMENT,

shift_name VARCHAR(20),

start_time TIME,

end_time TIME
```

);

INSERT INTO shifts(shift_name,start_time,end_time)
VALUES
('A','06:00:00','14:00:00'),
('B','14:00:00','22:00:00'),
('C','22:00:00','06:00:00');

-- =====================================================
-- MACHINE STATUS TABLE
-- =====================================================

CREATE TABLE machine_status (

```
status_id INT PRIMARY KEY AUTO_INCREMENT,

master_data_id INT,

machine_status VARCHAR(30),

updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

FOREIGN KEY(master_data_id)
REFERENCES master_data(id)
ON DELETE CASCADE
```

);

-- =====================================================
-- SYSTEM LOGS TABLE
-- =====================================================

CREATE TABLE system_logs (

```
log_id INT PRIMARY KEY AUTO_INCREMENT,

user_name VARCHAR(100),

action_done VARCHAR(255),

log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

);

-- =====================================================
-- DASHBOARD SETTINGS TABLE
-- =====================================================

CREATE TABLE dashboard_settings (

```
id INT PRIMARY KEY AUTO_INCREMENT,

total_stations INT DEFAULT 0,

buffer_required INT DEFAULT 0
```

);

INSERT INTO dashboard_settings(
total_stations,
buffer_required
)
VALUES(14,5);

-- =====================================================
-- SETTINGS TABLE
-- =====================================================

CREATE TABLE settings (

```
id INT PRIMARY KEY AUTO_INCREMENT,

setting_name VARCHAR(100),

setting_value VARCHAR(100)
```

);

-- =====================================================
-- BUFFER ALLOCATIONS TABLE
-- =====================================================

CREATE TABLE buffer_allocations (

```
emp_id VARCHAR(20) NOT NULL,

buffer_index INT NOT NULL,

station_name VARCHAR(100),

PRIMARY KEY(emp_id),

FOREIGN KEY(emp_id)
REFERENCES employee(emp_id)
ON DELETE CASCADE
```

);

-- =====================================================
-- DEFAULT SETTINGS DATA
-- =====================================================

INSERT INTO settings(setting_name, setting_value)
VALUES
('total_stations','14'),
('buffer_required','5');
