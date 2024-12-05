# API 响应格式文档

## 认证相关 (/auth)

### 注册 POST /auth/register
请求：
```json
{
    "username": "string",
    "password": "string",
    "role": "admin|doctor|nurse|patient",
    "email": "string",
    // 医生注册额外信息
    "doctor_info": {
        "name": "string",
        "birth_date": "date",
        "contact": "string",
        "department_id": "integer",
        "specialization": "string"
    },
    // 护士注册额外信息
    "nurse_info": {
        "name": "string",
        "birth_date": "date",
        "contact": "string",
        "department_id": "integer",
        "qualification": "string"
    },
    // 患者注册额外信息
    "patient_info": {
        "name": "string",
        "birth_date": "date",
        "gender": "string",
        "contact": "string",
        "address": "string",
        "medical_history": "string"
    }
}
```
成功响应 (201)：
```json
{
    "message": "用户注册成功",
    "user_id": "integer",
    "role_id": "integer",
    "role": "string"
}
```

### 登录 POST /auth/login
请求：
```json
{
    "username": "string",
    "password": "string"
}
```
成功响应 (200)：
```json
{
    "token": "string",
    "user_id": "integer",
    "role": "string"
}
```

### 修改密码 POST /auth/change-password
请求：
```json
{
    "old_password": "string",
    "new_password": "string"
}
```
成功响应 (200)：
```json
{
    "message": "密码修改成功"
}
```

### 重置密码 POST /auth/password-reset
请求：
```json
{
    "token": "string",
    "new_password": "string"
}
```
成功响应 (200)：
```json
{
    "message": "密码重置成功"
}
```

### 获取角色列表 GET /auth/roles
需要管理员权限
成功响应 (200)：
```json
[
    {
        "role": "string",
        "user_count": "integer"
    }
]
```

### 更新用户角色 PUT /auth/user/<id>/role
需要管理员权限
请求：
```json
{
    "role": "admin|doctor|nurse|patient"
}
```
成功响应 (200)：
```json
{
    "message": "用户角色更新成功"
}
```

## 医生相关 (/doctor)

### 获取医生信息 GET /doctor/profile/<id>
成功响应 (200)：
```json
{
    "id": "integer",
    "name": "string",
    "birth_date": "date",
    "contact": "string",
    "email": "string",
    "department_name": "string",
    "specialization": "string"
}
```

### 创建医生信息 POST /doctor
请求：
```json
{
    "name": "string",
    "birth_date": "date",
    "contact": "string",
    "email": "string",
    "department_id": "integer",
    "specialization": "string"
}
```
成功响应 (201)：
```json
{
    "message": "医生创建成功",
    "doctor_id": "integer"
}
```

### 获取患者列表 GET /doctor/patients
成功响应 (200)：
```json
[
    {
        "id": "integer",
        "name": "string",
        "gender": "string",
        "contact": "string",
        "relationship_start": "date",
        "notes": "string"
    }
]
```

## 患者相关 (/patient)

### 获取患者信息 GET /patient/profile/<id>
成功响应 (200)：
```json
{
    "id": "integer",
    "name": "string",
    "birth_date": "date",
    "gender": "string",
    "contact": "string",
    "address": "string",
    "medical_history": "string"
}
```

### 创建患者信息 POST /patient
请求：
```json
{
    "name": "string",
    "birth_date": "date",
    "contact": "string",
    "address": "string",
    "gender": "string",
    "medical_history": "string"
}
```
成功响应 (201)：
```json
{
    "message": "患者记录创建成功",
    "patient_id": "integer"
}
```

## 护士相关 (/nurse)

### 获取护士信息 GET /nurse/profile/<id>
成功响应 (200)：
```json
{
    "id": "integer",
    "name": "string",
    "birth_date": "date",
    "contact": "string",
    "email": "string",
    "department_name": "string",
    "qualification": "string"
}
```

### 获取负责病房 GET /nurse/<id>/wards
成功响应 (200)：
```json
[
    {
        "id": "integer",
        "room_number": "string",
        "ward_type": "string",
        "shift": "string",
        "start_date": "date",
        "end_date": "date"
    }
]
```

## 管理员相关 (/admin)

### 创建科室 POST /admin/department
请求：
```json
{
    "name": "string",
    "description": "string"
}
```
成功响应 (201)：
```json
{
    "message": "科室创建成功",
    "department_id": "integer"
}
```

### 获取科室统计 GET /admin/department/<id>/stats
成功响应 (200)：
```json
{
    "department": {
        "id": "integer",
        "name": "string",
        "doctor_count": "integer"
    },
    "doctors": [
        {
            "id": "integer",
            "name": "string",
            "specialization": "string",
            "contact": "string",
            "email": "string"
        }
    ]
}
```

## 统计信息 (/api)

### 获取基本统计 GET /api/stats
需要登录权限
成功响应 (200)：
```json
{
    "doctors": "integer",
    "patients": "integer",
    "nurses": "integer",
    "departments": "integer"
}
```

## 通用错误响应

未授权访问 (401)：
```json
{
    "error": "未授权访问"
}
```

权限不足 (403)：
```json
{
    "error": "需要xxx权限"
}
```

请求错误 (400)：
```json
{
    "error": "缺少必填字段: {field_name}"
}
```
```json
{
    "error": "用户名已存在"
}
```
```json
{
    "error": "无效的用户角色"
}
```
```json
{
    "error": "缺少xxx相关信息"
}
```

认证错误 (401)：
```json
{
    "error": "密码错误"
}
```
```json
{
    "error": "旧密码错误"
}
```

资源不存在 (404)：
```json
{
    "error": "用户不存在"
}
```

服务器错误 (500)：
```json
{
    "error": "xxx失败: 具体错误信息"
}
```

## 注意事项

1. 所有需要认证的接口都需要在请求头中包含 token：
```
Authorization: Bearer <token>
```

2. 日期格式统一使用：YYYY-MM-DD
3. 所有响应都使用 JSON 格式
4. 成功响应状态码：200（成功）或 201（创建成功）
5. 错误响应包含具体的错误信息