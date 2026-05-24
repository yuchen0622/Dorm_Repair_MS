from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from users.models import User


def index(request):
    """首页视图"""
    context = {}
    
    if request.user.is_authenticated:
        from repairs.models import RepairRequest
        from workorders.models import WorkOrder
        from reviews.models import Review
        from django.db.models import Avg
        
        if request.user.is_admin():
            context['total_repairs'] = RepairRequest.objects.count()
            context['pending_repairs'] = RepairRequest.objects.filter(status='pending').count()
            context['processing_repairs'] = RepairRequest.objects.filter(status='processing').count()
            context['completed_repairs'] = RepairRequest.objects.filter(status='completed').count()
            
            context['total_workorders'] = WorkOrder.objects.count()
            context['assigned_workorders'] = WorkOrder.objects.filter(status='assigned').count()
            context['in_progress_workorders'] = WorkOrder.objects.filter(status='in_progress').count()
            
            context['total_reviews'] = Review.objects.count()
            avg_rating = Review.objects.aggregate(avg=Avg('rating'))['avg']
            context['avg_rating'] = round(avg_rating, 2) if avg_rating else 0
            
            context['total_users'] = User.objects.count()
            context['student_count'] = User.objects.filter(role='student').count()
            context['worker_count'] = User.objects.filter(role='worker').count()
            
        elif request.user.is_worker():
            my_workorders = WorkOrder.objects.filter(worker=request.user)
            context['my_assigned'] = my_workorders.filter(status='assigned').count()
            context['my_accepted'] = my_workorders.filter(status='accepted').count()
            context['my_in_progress'] = my_workorders.filter(status='in_progress').count()
            context['my_completed'] = my_workorders.filter(status='completed').count()
            
            my_reviews = Review.objects.filter(work_order__worker=request.user)
            context['my_review_count'] = my_reviews.count()
            my_avg = my_reviews.aggregate(avg=Avg('rating'))['avg']
            context['my_avg_rating'] = round(my_avg, 2) if my_avg else 0
            
        elif request.user.is_student():
            my_repairs = RepairRequest.objects.filter(student=request.user)
            context['my_pending'] = my_repairs.filter(status='pending').count()
            context['my_processing'] = my_repairs.filter(status='processing').count()
            context['my_completed'] = my_repairs.filter(status='completed').count()
    
    return render(request, 'index.html', context)


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
