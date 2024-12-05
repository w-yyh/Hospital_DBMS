CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50),
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    email VARCHAR(120),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    last_login TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS wards (
    id SERIAL PRIMARY KEY,
    room_number VARCHAR(20),
    ward_type VARCHAR(50),
    bed_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS doctors (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    name VARCHAR(100),
    birth_date DATE,
    contact VARCHAR(50),
    email VARCHAR(120),
    department_id INTEGER,
    specialization VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS nurses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    name VARCHAR(100),
    birth_date DATE,
    contact VARCHAR(50),
    email VARCHAR(120),
    department_id INTEGER,
    qualification VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS patients (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    name VARCHAR(100),
    birth_date DATE,
    gender CHAR(1),
    contact VARCHAR(50),
    address TEXT,
    medical_history TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS nurse_ward_assignments (
    id SERIAL PRIMARY KEY,
    nurse_id INTEGER,
    ward_id INTEGER,
    start_date DATE NOT NULL,
    end_date DATE,
    shift VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS admissions (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER,
    doctor_id INTEGER,
    ward_id INTEGER,
    admission_date DATE NOT NULL,
    discharge_date DATE,
    expected_discharge_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS treatments (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER,
    doctor_id INTEGER,
    diagnosis TEXT,
    treatment_plan TEXT,
    medications TEXT,
    treatment_date DATE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS patient_doctor (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER,
    doctor_id INTEGER,
    start_date DATE NOT NULL,
    end_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

DELETE FROM users WHERE username IN ('testadmin', 'testdoctor', 'testnurse', 'testpatient');
