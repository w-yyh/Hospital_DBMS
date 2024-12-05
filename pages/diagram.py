from pyvis.network import Network
import pyvis

def add_users_diagram(G):
    # 添加实体
    G.add_node("users", size=30, shape="square", color="Blue", title="实体集", label="Users")

    # 添加属性字段，椭圆形，title包含数据类型
    G.add_node("users_id", size=30, shape="dot", color="lightgreen", title="SERIAL (Primary Key)", label="id")
    G.add_node("users_username", size=30, shape="dot", color="lightgreen", title="VARCHAR(50) (Unique)", label="username")
    G.add_node("users_password_hash", size=30, shape="dot", color="lightgreen", title="VARCHAR(255)", label="password_hash")
    G.add_node("users_role", size=30, shape="dot", color="lightgreen", title="VARCHAR(20)", label="role")
    G.add_node("users_email", size=30, shape="dot", color="lightgreen", title="VARCHAR(120) (Unique)", label="email")
    G.add_node("users_created_at", size=30, shape="dot", color="lightgreen", title="TIMESTAMP", label="created_at")
    G.add_node("users_updated_at", size=30, shape="dot", color="lightgreen", title="TIMESTAMP", label="updated_at")
    G.add_node("users_last_login", size=30, shape="dot", color="lightgreen", title="TIMESTAMP", label="last_login")
    G.add_node("users_is_deleted", size=30, shape="dot", color="lightgreen", title="BOOLEAN", label="is_deleted")

    # 连接实体和属性，实体与字段之间的连接，label标记Primary Key和Unique
    G.add_edge("users", "users_id", width=3, color="gray", label="Primary Key")
    G.add_edge("users", "users_username", width=3, color="gray", label="Unique")
    G.add_edge("users", "users_password_hash", width=3, color="gray")
    G.add_edge("users", "users_role", width=3, color="gray")
    G.add_edge("users", "users_email", width=3, color="gray", label="Unique")
    G.add_edge("users", "users_created_at", width=3, color="gray")
    G.add_edge("users", "users_updated_at", width=3, color="gray")
    G.add_edge("users", "users_last_login", width=3, color="gray")
    G.add_edge("users", "users_is_deleted", width=3, color="gray")

def add_dormitory_diagram(G):
    # 添加实体
    G.add_node("dormitory", size=30, shape="square", color="Blue", title="实体集", label="dormitory")

    # 添加属性字段，椭圆形，title包含数据类型
    G.add_node("dormitory_id", size=30, shape="dot", color="lightgreen", title="SERIAL (Primary Key)", label="id")
    G.add_node("dormitory_name", size=30, shape="dot", color="lightgreen", title="VARCHAR(100) (NOT NULL)", label="name")
    G.add_node("dormitory_description", size=30, shape="dot", color="lightgreen", title="TEXT", label="description")
    G.add_node("dormitory_created_at", size=30, shape="dot", color="lightgreen", title="TIMESTAMP", label="created_at")
    G.add_node("dormitory_updated_at", size=30, shape="dot", color="lightgreen", title="TIMESTAMP", label="updated_at")
    G.add_node("dormitory_is_deleted", size=30, shape="dot", color="lightgreen", title="BOOLEAN", label="is_deleted")

    # 连接实体和属性，实体与字段之间的连接，label标记Primary Key和约束
    G.add_edge("dormitory", "dormitory_id", width=3, color="gray", label="Primary Key")
    G.add_edge("dormitory", "dormitory_name", width=3, color="gray", label="NOT NULL")
    G.add_edge("dormitory", "dormitory_description", width=3, color="gray")
    G.add_edge("dormitory", "dormitory_created_at", width=3, color="gray")
    G.add_edge("dormitory", "dormitory_updated_at", width=3, color="gray")
    G.add_edge("dormitory", "dormitory_is_deleted", width=3, color="gray")

def add_wards_diagram(G):
    # 添加实体
    G.add_node("wards", size=30, shape="square", color="Blue", title="实体集", label="Wards")

    # 添加属性字段，椭圆形，title包含数据类型
    G.add_node("wards_id", size=30, shape="dot", color="lightgreen", title="SERIAL (Primary Key)", label="id")
    G.add_node("wards_room_number", size=30, shape="dot", color="lightgreen", title="VARCHAR(20) (Unique, NOT NULL)", label="room_number")
    G.add_node("wards_ward_type", size=30, shape="dot", color="lightgreen", title="VARCHAR(50) (NOT NULL)", label="ward_type")
    G.add_node("wards_bed_count", size=30, shape="dot", color="lightgreen", title="INTEGER (NOT NULL)", label="bed_count")
    G.add_node("wards_created_at", size=30, shape="dot", color="lightgreen", title="TIMESTAMP", label="created_at")
    G.add_node("wards_updated_at", size=30, shape="dot", color="lightgreen", title="TIMESTAMP", label="updated_at")
    G.add_node("wards_is_deleted", size=30, shape="dot", color="lightgreen", title="BOOLEAN", label="is_deleted")

    # 连接实体和属性，实体与字段之间的连接，label标记Primary Key和约束
    G.add_edge("wards", "wards_id", width=3, color="gray", label="Primary Key")
    G.add_edge("wards", "wards_room_number", width=3, color="gray", label="Unique, NOT NULL")
    G.add_edge("wards", "wards_ward_type", width=3, color="gray", label="NOT NULL")
    G.add_edge("wards", "wards_bed_count", width=3, color="gray", label="NOT NULL")
    G.add_edge("wards", "wards_created_at", width=3, color="gray")
    G.add_edge("wards", "wards_updated_at", width=3, color="gray")
    G.add_edge("wards", "wards_is_deleted", width=3, color="gray")

def add_doctors_diagram(G):
    # 添加实体
    G.add_node("doctors", size=30, shape="square", color="lightBlue", title="弱实体集", label="Doctors")

    # 添加属性字段，椭圆形，title包含数据类型
    G.add_node("doctors_id", size=30, shape="dot", color="lightgreen", title="SERIAL (Primary Key)", label="id")
    G.add_node("doctors_user_id", size=30, shape="dot", color="lightgreen", title="INTEGER (Foreign Key)", label="user_id")
    G.add_node("doctors_name", size=30, shape="dot", color="lightgreen", title="VARCHAR(100) (NOT NULL)", label="name")
    G.add_node("doctors_birth_date", size=30, shape="dot", color="lightgreen", title="DATE", label="birth_date")
    G.add_node("doctors_contact", size=30, shape="dot", color="lightgreen", title="VARCHAR(50)", label="contact")
    G.add_node("doctors_email", size=30, shape="dot", color="lightgreen", title="VARCHAR(120)", label="email")
    G.add_node("doctors_department_id", size=30, shape="dot", color="lightgreen", title="INTEGER (Foreign Key)", label="department_id")
    G.add_node("doctors_specialization", size=30, shape="dot", color="lightgreen", title="VARCHAR(100)", label="specialization")
    G.add_node("doctors_created_at", size=30, shape="dot", color="lightgreen", title="TIMESTAMP", label="created_at")
    G.add_node("doctors_updated_at", size=30, shape="dot", color="lightgreen", title="TIMESTAMP", label="updated_at")
    G.add_node("doctors_is_deleted", size=30, shape="dot", color="lightgreen", title="BOOLEAN", label="is_deleted")

    # 连接实体和属性，实体与字段之间的连接，label标记约束
    G.add_edge("doctors", "doctors_id", width=3, color="gray", label="Primary Key")
    G.add_edge("doctors", "doctors_user_id", width=3, color="gray", label="Foreign Key (users)")
    G.add_edge("doctors", "doctors_name", width=3, color="gray", label="NOT NULL")
    G.add_edge("doctors", "doctors_birth_date", width=3, color="gray")
    G.add_edge("doctors", "doctors_contact", width=3, color="gray")
    G.add_edge("doctors", "doctors_email", width=3, color="gray")
    G.add_edge("doctors", "doctors_department_id", width=3, color="gray", label="Foreign Key (dormitory)")
    G.add_edge("doctors", "doctors_specialization", width=3, color="gray")
    G.add_edge("doctors", "doctors_created_at", width=3, color="gray")
    G.add_edge("doctors", "doctors_updated_at", width=3, color="gray")
    G.add_edge("doctors", "doctors_is_deleted", width=3, color="gray")

def add_nurses_diagram(G):
    # 添加实体
    G.add_node("nurses", size=30, shape="square", color="lightBlue", title="弱实体集", label="Nurses")

    # 添加属性字段，椭圆形，title包含数据类型
    G.add_node("nurses_id", size=30, shape="dot", color="lightgreen", title="SERIAL (Primary Key)", label="id")
    G.add_node("nurses_user_id", size=30, shape="dot", color="lightgreen", title="INTEGER (Foreign Key)", label="user_id")
    G.add_node("nurses_name", size=30, shape="dot", color="lightgreen", title="VARCHAR(100) (NOT NULL)", label="name")
    G.add_node("nurses_birth_date", size=30, shape="dot", color="lightgreen", title="DATE", label="birth_date")
    G.add_node("nurses_contact", size=30, shape="dot", color="lightgreen", title="VARCHAR(50)", label="contact")
    G.add_node("nurses_email", size=30, shape="dot", color="lightgreen", title="VARCHAR(120)", label="email")
    G.add_node("nurses_department_id", size=30, shape="dot", color="lightgreen", title="INTEGER (Foreign Key)", label="department_id")
    G.add_node("nurses_qualification", size=30, shape="dot", color="lightgreen", title="VARCHAR(50)", label="qualification")
    G.add_node("nurses_created_at", size=30, shape="dot", color="lightgreen", title="TIMESTAMP", label="created_at")
    G.add_node("nurses_updated_at", size=30, shape="dot", color="lightgreen", title="TIMESTAMP", label="updated_at")
    G.add_node("nurses_is_deleted", size=30, shape="dot", color="lightgreen", title="BOOLEAN", label="is_deleted")

    # 连接实体和属性，实体与字段之间的连接，label标记约束
    G.add_edge("nurses", "nurses_id", width=3, color="gray", label="Primary Key")
    G.add_edge("nurses", "nurses_user_id", width=3, color="gray", label="Foreign Key (users)")
    G.add_edge("nurses", "nurses_name", width=3, color="gray", label="NOT NULL")
    G.add_edge("nurses", "nurses_birth_date", width=3, color="gray")
    G.add_edge("nurses", "nurses_contact", width=3, color="gray")
    G.add_edge("nurses", "nurses_email", width=3, color="gray")
    G.add_edge("nurses", "nurses_department_id", width=3, color="gray", label="Foreign Key (dormitory)")
    G.add_edge("nurses", "nurses_qualification", width=3, color="gray")
    G.add_edge("nurses", "nurses_created_at", width=3, color="gray")
    G.add_edge("nurses", "nurses_updated_at", width=3, color="gray")
    G.add_edge("nurses", "nurses_is_deleted", width=3, color="gray")

def add_patients_diagram(G):
    # 添加实体
    G.add_node("patients", size=30, shape="square", color="lightBlue", title="弱实体集", label="Patients")

    # 添加属性字段，椭圆形，title包含数据类型
    G.add_node("patients_id", size=30, shape="dot", color="lightgreen", title="SERIAL (Primary Key)", label="id")
    G.add_node("patients_user_id", size=30, shape="dot", color="lightgreen", title="INTEGER (Foreign Key)", label="user_id")
    G.add_node("patients_name", size=30, shape="dot", color="lightgreen", title="VARCHAR(100) (NOT NULL)", label="name")
    G.add_node("patients_birth_date", size=30, shape="dot", color="lightgreen", title="DATE", label="birth_date")
    G.add_node("patients_gender", size=30, shape="dot", color="lightgreen", title="CHAR(1)", label="gender")
    G.add_node("patients_contact", size=30, shape="dot", color="lightgreen", title="VARCHAR(50)", label="contact")
    G.add_node("patients_address", size=30, shape="dot", color="lightgreen", title="TEXT", label="address")
    G.add_node("patients_medical_history", size=30, shape="dot", color="lightgreen", title="TEXT", label="medical_history")
    G.add_node("patients_created_at", size=30, shape="dot", color="lightgreen", title="TIMESTAMP", label="created_at")
    G.add_node("patients_updated_at", size=30, shape="dot", color="lightgreen", title="TIMESTAMP", label="updated_at")

    # 连接实体和属性，实体与字段之间的连接，label标记约束
    G.add_edge("patients", "patients_id", width=3, color="gray", label="Primary Key")
    G.add_edge("patients", "patients_user_id", width=3, color="gray", label="Foreign Key (users)")
    G.add_edge("patients", "patients_name", width=3, color="gray", label="NOT NULL")
    G.add_edge("patients", "patients_birth_date", width=3, color="gray")
    G.add_edge("patients", "patients_gender", width=3, color="gray")
    G.add_edge("patients", "patients_contact", width=3, color="gray")
    G.add_edge("patients", "patients_address", width=3, color="gray")
    G.add_edge("patients", "patients_medical_history", width=3, color="gray")
    G.add_edge("patients", "patients_created_at", width=3, color="gray")
    G.add_edge("patients", "patients_updated_at", width=3, color="gray")