from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.core.paginator import Paginator
from .models import User
import json


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
        if not request.user.is_admin():
            return JsonResponse({'success': False, 'message': '权限不足'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        role = request.POST.get('role', '')
        phone = request.POST.get('phone', '').strip()

        if not all([username, email, password1, password2, role]):
            messages.error(request, '请填写所有必填项')
            return render(request, 'register.html')

        if password1 != password2:
            messages.error(request, '两次输入的密码不一致')
            return render(request, 'register.html')

        if len(password1) < 6:
            messages.error(request, '密码长度至少6位')
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在')
            return render(request, 'register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, '邮箱已被注册')
            return render(request, 'register.html')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            role=role,
            phone=phone
        )

        messages.success(request, '注册成功，请登录')
        return redirect('users:login')

    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            messages.error(request, '请输入用户名和密码')
            return render(request, 'login.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'欢迎回来，{user.username}！')
            next_url = request.GET.get('next', 'index')
            return redirect(next_url)
        else:
            messages.error(request, '用户名或密码错误')
            return render(request, 'login.html')

    return render(request, 'login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, '已成功退出登录')
    return redirect('users:login')


@login_required
def profile(request):
    return render(request, 'users/profile.html', {'user': request.user})


@login_required
def profile_edit(request):
    if request.method == 'POST':
        user = request.user
        phone = request.POST.get('phone', '').strip()
        dorm_building = request.POST.get('dorm_building', '').strip()
        dorm_room = request.POST.get('dorm_room', '').strip()
        specialty = request.POST.get('specialty', '').strip()

        user.phone = phone
        user.dorm_building = dorm_building
        user.dorm_room = dorm_room
        user.specialty = specialty
        user.save()

        messages.success(request, '个人信息更新成功')
        return redirect('users:profile')

    return render(request, 'users/profile_edit.html', {'user': request.user})


@login_required
def user_manage(request):
    if not request.user.is_admin():
        messages.error(request, '权限不足')
        return redirect('index')
    
    role = request.GET.get('role', '')
    users = User.objects.all().order_by('-date_joined')
    if role:
        users = users.filter(role=role)
    
    paginator = Paginator(users, 10)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    
    context = {
        'page_obj': page_obj,
        'current_role': role,
        'total_users': User.objects.count(),
        'total_students': User.objects.filter(role='student').count(),
        'total_workers': User.objects.filter(role='worker').count(),
        'total_admins': User.objects.filter(role='admin').count(),
    }
    return render(request, 'users/user_manage.html', context)


@require_POST
def api_register(request):
    import json
    try:
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        role = data.get('role', '')
        phone = data.get('phone', '').strip()

        if not all([username, email, password, role]):
            return JsonResponse({'success': False, 'message': '请填写所有必填项'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'message': '用户名已存在'}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': '邮箱已被注册'}, status=400)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
            phone=phone
        )

        return JsonResponse({
            'success': True,
            'message': '注册成功',
            'data': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@require_POST
def api_login(request):
    import json
    try:
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        password = data.get('password', '')

        if not username or not password:
            return JsonResponse({'success': False, 'message': '请输入用户名和密码'}, status=400)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({
                'success': True,
                'message': '登录成功',
                'data': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'role_display': user.get_role_display()
                }
            })
        else:
            return JsonResponse({'success': False, 'message': '用户名或密码错误'}, status=401)

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
def api_profile(request):
    user = request.user
    return JsonResponse({
        'success': True,
        'data': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'role_display': user.get_role_display(),
            'phone': user.phone,
            'dorm_building': user.dorm_building,
            'dorm_room': user.dorm_room,
            'specialty': user.specialty
        }
    })


@login_required
@require_POST
def api_logout(request):
    logout(request)
    return JsonResponse({'success': True, 'message': '已成功退出登录'})


@login_required
@admin_required
@require_GET
def api_user_list(request):
    role = request.GET.get('role', '')
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    
    users = User.objects.all()
    if role:
        users = users.filter(role=role)
    
    paginator = Paginator(users, page_size)
    page_obj = paginator.get_page(page)
    
    user_list = []
    for user in page_obj:
        user_list.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'role_display': user.get_role_display(),
            'phone': user.phone,
            'dorm_building': user.dorm_building,
            'dorm_room': user.dorm_room,
            'specialty': user.specialty,
            'is_active': user.is_active,
            'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M')
        })
    
    return JsonResponse({
        'success': True,
        'data': {
            'users': user_list,
            'total': paginator.count,
            'page': page,
            'page_size': page_size,
            'total_pages': paginator.num_pages
        }
    })


@login_required
@admin_required
@require_GET
def api_user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return JsonResponse({
        'success': True,
        'data': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'role_display': user.get_role_display(),
            'phone': user.phone,
            'dorm_building': user.dorm_building,
            'dorm_room': user.dorm_room,
            'specialty': user.specialty,
            'is_active': user.is_active,
            'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M')
        }
    })


@login_required
@admin_required
@require_POST
def api_user_create(request):
    try:
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        role = data.get('role', 'student')
        phone = data.get('phone', '').strip()
        dorm_building = data.get('dorm_building', '').strip()
        dorm_room = data.get('dorm_room', '').strip()
        specialty = data.get('specialty', '').strip()
        
        if not username or not email or not password:
            return JsonResponse({'success': False, 'message': '用户名、邮箱和密码不能为空'}, status=400)
        
        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'message': '用户名已存在'}, status=400)
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': '邮箱已被注册'}, status=400)
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
            phone=phone,
            dorm_building=dorm_building,
            dorm_room=dorm_room,
            specialty=specialty
        )
        
        return JsonResponse({
            'success': True,
            'message': '用户创建成功',
            'data': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
@admin_required
@require_POST
def api_user_update(request, user_id):
    try:
        user = get_object_or_404(User, id=user_id)
        data = json.loads(request.body)
        
        if 'phone' in data:
            user.phone = data['phone'].strip()
        if 'dorm_building' in data:
            user.dorm_building = data['dorm_building'].strip()
        if 'dorm_room' in data:
            user.dorm_room = data['dorm_room'].strip()
        if 'specialty' in data:
            user.specialty = data['specialty'].strip()
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': '用户信息更新成功',
            'data': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
@admin_required
@require_POST
def api_user_delete(request, user_id):
    try:
        user = get_object_or_404(User, id=user_id)
        
        if user.id == request.user.id:
            return JsonResponse({'success': False, 'message': '不能删除自己的账号'}, status=400)
        
        username = user.username
        user.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'用户 {username} 已删除'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
@admin_required
@require_GET
def api_user_stats(request):
    total = User.objects.count()
    students = User.objects.filter(role='student').count()
    workers = User.objects.filter(role='worker').count()
    admins = User.objects.filter(role='admin').count()
    active = User.objects.filter(is_active=True).count()
    
    return JsonResponse({
        'success': True,
        'data': {
            'total': total,
            'students': students,
            'workers': workers,
            'admins': admins,
            'active': active
        }
    })
