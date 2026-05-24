from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import User


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
    return redirect('login')


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
