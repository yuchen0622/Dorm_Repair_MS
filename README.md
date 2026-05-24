# 宿舍报修管理系统

一个基于 Django 的宿舍报修管理系统，支持学生报修、维修工接单、管理员派单等功能。

---

## 技术栈声明

**后端：** Django 4.2 (Python Web框架)

**前端：** Django模板引擎 + HTML5 + CSS3 + JavaScript

**数据库：** SQLite (开发环境)

**依赖库：** 
- Django (Web框架)
- Pillow (图片处理)

---

## 本地部署步骤

### 1. 环境准备

```bash
# 确保已安装 Python 3.10+，检查版本
python --version

# 进入项目目录
cd Dorm_Repai_MS
```

### 2. 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 安装依赖
pip install django
pip install pillow
```

### 3. 数据库初始化

```bash
# 进入项目根目录（包含 manage.py 的目录）
cd dorm_repair

# 执行数据库迁移，创建表结构
python manage.py makemigrations
python manage.py migrate
```

### 4. 创建管理员账号

```bash
# 通过命令行创建超级管理员
python manage.py createsuperuser

# 按提示输入：
# 用户名：admin
# 邮箱：（可留空直接回车）
# 密码：admin123
# 确认密码：admin123
```

### 5. 启动开发服务器

```bash
# 启动 Django 开发服务器
python manage.py runserver

# 访问系统
# 首页：http://127.0.0.1:8000/
# 管理后台：http://127.0.0.1:8000/admin/
```

### 6. 测试账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 学生 | sgm | 123456 |
| 维修工 | yc | 123456 |
---

## 项目目录结构

```
Dorm_Repai_MS/
├── dorm_repair/          # 项目配置目录
│   ├── settings.py       # 配置文件
│   ├── urls.py           # 主路由
│   └── wsgi.py           # WSGI入口
├── users/                # 用户模块
├── repairs/              # 报修模块
├── workorders/           # 工单模块
├── reviews/              # 评价模块
├── evaluations/          # 评价模块
├── templates/            # 模板文件
├── static/               # 静态文件
├── media/                # 上传文件
├── db.sqlite3            # SQLite数据库
└── manage.py             # Django管理脚本
```

---

## 功能模块

### 用户模块 (users)
- 用户注册、登录、登出
- 角色权限控制（学生/维修工/管理员）
- 用户信息管理

### 报修模块 (repairs)
- 报修单创建、编辑、查询
- 报修图片上传
- 报修状态管理

### 工单模块 (workorders)
- 工单派发（管理员）
- 工单接单/拒绝（维修工）
- 维修流程状态管理

### 评价模块 (reviews/evaluations)
- 评价提交
- 评价统计展示
- 维修工评分统计

---

