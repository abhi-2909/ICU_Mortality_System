CREATE DATABASE IF NOT EXISTS icu_mortality_db;
USE icu_mortality_db;

-- ===============================
-- STAFF TABLE
-- ===============================
CREATE TABLE staff (

    id INT AUTO_INCREMENT PRIMARY KEY,

    full_name VARCHAR(100) NOT NULL,

    username VARCHAR(50) UNIQUE NOT NULL,

    password VARCHAR(255) NOT NULL,

    role ENUM('Admin','Doctor','Nurse') NOT NULL,

    email VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

-- ===============================
-- PATIENT TABLE
-- ===============================
CREATE TABLE patients (

    patient_id INT AUTO_INCREMENT PRIMARY KEY,

    patient_name VARCHAR(100),

    age INT,

    gender VARCHAR(10),

    phone VARCHAR(20),

    admission_date DATE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

-- ===============================
-- PREDICTIONS TABLE
-- ===============================
CREATE TABLE predictions (

    prediction_id INT AUTO_INCREMENT PRIMARY KEY,

    patient_id INT,

    mortality_probability FLOAT,

    risk_level VARCHAR(20),

    prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (patient_id)
    REFERENCES patients(patient_id)

);

-- ===============================
-- LOGIN HISTORY
-- ===============================
CREATE TABLE login_history (

    id INT AUTO_INCREMENT PRIMARY KEY,

    staff_id INT,

    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (staff_id)
    REFERENCES staff(id)

);