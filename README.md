# 医院管理系统后端 API
这是一个基于 Flask 的医院管理系统后端，提供了完整的用户认证和数据管理功能。

## 项目结构
```
hospital_management/
├── app/
│ ├── init.py # Flask应用初始化
│ ├── routes/ # API路由
│ │ ├── auth.py # 认证相关路由
│ │ ├── admin.py # 管理员路由
│ │ ├── doctor.py # 医生路由
│ │ └── patient.py # 病人路由
│ └── utils/ # 工具函数
│ ├── auth.py # 认证工具
│ └── db.py # 数据库工具
├── database/
│ ├── Hospital_Management_System.sql # 数据库结构
│ └── db_initializer.py # 数据库初始化工具
├── tests/
│ └── test_hospital_system.py # 测试用例
├── config.py # 配置文件
└── run.py # 应用入口
```

## 安装和配置
1. 安装依赖：
    `pip install -r requirements.txt`
2. 初始化数据库：
    `python database/db_initializer.py`
    请按提示输入MySQL配置信息。
3. 运行应用：
    `python run.py`

## 测试

运行测试：
1. 基本测试： 
`python -m tests.test_hospital_system`
2. 接口测试：
`pytest tests/test_hospital_system.py -v`


测试覆盖：
- 数据库连接测试
- 表结构完整性测试
- 触发器功能测试
- API端点测试
- 数据完整性测试
- 用户认证测试


## 功能特性

### 用户认证
- 用户注册 `/auth/register`
- 用户登录 `/auth/login`
- 修改密码 `/auth/change-password`

### 医生功能
- 获取个人信息 `/doctor/profile/<id>`
- 创建医生信息 `/doctor`
- 更新医生信息 `/doctor/<id>`
- 删除医生信息 `/doctor/<id>`
- 获取患者列表 `/doctor/patients`
- 更新诊断信息 `/doctor/update-diagnosis`

### 治疗记录管理
- 创建治疗记录 `/doctor/treatment`
- 获取治疗记录 `/doctor/treatment/<id>`
- 更新治疗记录 `/doctor/treatment/<id>`
- 删除治疗记录 `/doctor/treatment/<id>`
- 获取患者治疗记录 `/doctor/patient/<id>/treatments`

### 医患关系管理
- 创建医患关系 `/doctor/patient-relation`
- 获取医患关系 `/doctor/patient-relation/<id>`
- 更新医患关系 `/doctor/patient-relation/<id>`
- 删除医患关系 `/doctor/patient-relation/<id>`
- 获取患者的医生列表 `/doctor/patient/<id>/doctors`

### 入院记录管理
- 创建入院记录 `/doctor/admission`
- 更新入院记录 `/doctor/admission/<id>`
- 删除入院记录 `/doctor/admission/<id>`
- 获取患者入院记录 `/doctor/patient/<id>/admissions`

### 护士管理
- 创建护士信息 `/nurse`
- 获取护士信息 `/nurse/profile/<id>`
- 更新护士信息 `/nurse/<id>`
- 删除护士信息 `/nurse/<id>`
- 获取负责病房 `/nurse/<id>/wards`
- 更新排班信息 `/nurse/<id>/schedule`
- 获取病房患者 `/nurse/<id>/patients`

### 管理员功能
- 科室管理
  - 创建科室 `/admin/department`
  - 获取科室信息 `/admin/department/<id>`
  - 更新科室信息 `/admin/department/<id>`
  - 删除科室 `/admin/department/<id>`
  - 获取科室统计 `/admin/department/<id>/stats`

- 病房管理
  - 创建病房 `/admin/ward`
  - 获取病房信息 `/admin/ward/<id>`
  - 更新病房信息 `/admin/ward/<id>`
  - 删除病房 `/admin/ward/<id>`
  - 获取病房统计 `/admin/ward/stats`

- 护士排班
  - 分配护士到病房 `/admin/nurse-assignment`
  - 获取病房护士 `/admin/ward/<id>/nurses`
  - 更新护士排班 `/admin/nurse-assignment/<id>`
  - 删除护士排班 `/admin/nurse-assignment/<id>`

### 认证相关
#### 登录
路径: /login
方法: POST
请求体:
```
{
"user_type": "doctor|admin|patient",
"email": "user@example.com",
"password": "password"
}
```
响应:
```
{
"token": "jwt_token"
}
```
### 管理员接口
所有管理员接口需要在请求头中包含：`Authorization: Bearer <token>`
#### 获取所有医生
路径: /admin/doctors
方法: GET
响应: 医生列表
#### 添加新医生
路径: /admin/doctor
方法: POST
请求体:
```
{
"doctor_id": 1000,
"name": "Dr. Name",
"dob": "1990-01-01",
"contact_number": "13800138000",
"specialization": "Surgery",
"department_id": 1,
"email": "doctor@example.com"
}
```
### 医生接口
所有医生接口需要在请求头中包含：`Authorization: Bearer <token>`
#### 获取病人列表
路径: /doctor/patients
方法: GET
响应: 该医生的病人列表
#### 更新诊断
路径: /doctor/update-diagnosis
方法: POST
请求体:
```
{
"patient_id": 1,
"diagnosis": "诊断内容"
}
```
### 病人接口
所有病人接口需要在请求头中包含：`Authorization: Bearer <token>`
#### 获取个人信息
路径: /patient/profile/<patient_id>
方法: GET
说明: 病人只能访问自己的信息
#### 获取主治医生
路径: /patient/doctors/<patient_id>
方法: GET
说明: 病人只能查看自己的主治医生
## 数据库设计
### 主要表结构
1. departments - 部门信息
- department_id (PK)
- department_name
- description
2. doctors - 医生信息
- doctor_id (PK)
- name
- dob
- contact_number
- specialization
- department_id (FK)
- email
3. patients - 病人信息
- patient_id (PK)
- name
- dob
- contact_number
- address
- gender
- admission_date
- discharge_date
- treatment_record
4. patient_doctor - 病人-医生关系
- patient_id (FK)
- doctor_id (FK)
- visit_date
- diagnosis
5. patient_room - 病人-房间关系
- patient_id (FK)
- room_id (FK)
- admission_date
- discharge_date
6. rooms - 房间信息
- room_id (PK)
- room_type
- capacity
- room_number


## 前端集成指南
1. 认证流程：
调用登录接口获取token
将token存储在本地
在后续请求中添加Authorization头
2. 示例代码：
```
// 登录
async function login(userType, email, password) {
const response = await fetch('/login', {
method: 'POST',
headers: {
'Content-Type': 'application/json'
},
body: JSON.stringify({
user_type: userType,
email: email,
password: password
})
});
const data = await response.json();
localStorage.setItem('token', data.token);
return data.token;
}
// API请求
async function makeAuthRequest(url, method = 'GET', body = null) {
const token = localStorage.getItem('token');
const options = {
method,
headers: {
'Authorization': Bearer ${token},
'Content-Type': 'application/json'
}
};
if (body) {
options.body = JSON.stringify(body);
}
const response = await fetch(url, options);
return await response.json();
}
```
## 错误处理
API返回的错误格式：
```
{
"error": "错误描述"
}
```
常见状态码：
200: 成功
400: 请求错误
401: 未认证
403: 无权限
404: 资源不存在
500: 服务器错误

## 维护和更新
更新数据库：
1. 修改SQL文件
2. 重新运行初始化工具
