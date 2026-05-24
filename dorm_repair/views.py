from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from users.models import User


def index(request):
    """首页视图"""
    return render(request, 'index.html')


def login_view(request):
    """
    登录视图
    处理用户的登录请求，验证用户名和密码
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, '登录成功！')
            return redirect('index')
        else:
            messages.error(request, '用户名或密码错误')
    return render(request, 'login.html')


def register(request):
    """
    注册视图
    处理用户注册请求，创建新用户账号
    支持学生和维修工两种角色注册
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        role = request.POST.get('role')
        phone = request.POST.get('phone', '')

        # 检查两次密码是否一致
        if password1 != password2:
            messages.error(request, '两次密码不一致')
            return render(request, 'register.html')

        # 检查用户名是否已存在
        if User.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在')
            return render(request, 'register.html')

        # 检查邮箱是否已被注册
        if User.objects.filter(email=email).exists():
            messages.error(request, '邮箱已被注册')
            return render(request, 'register.html')

        # 创建用户
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            role=role,
            phone=phone
        )
        messages.success(request, '注册成功，请登录')
        return redirect('login')

    return render(request, 'register.html')


@login_required
def logout_view(request):
    """退出登录视图"""
    logout(request)
    messages.success(request, '已退出登录')
    return redirect('index')
