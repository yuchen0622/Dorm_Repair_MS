from django.http import JsonResponse


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
        if not request.user.is_admin():
            return JsonResponse({'success': False, 'message': '权限不足'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


def worker_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
        if not request.user.is_worker():
            return JsonResponse({'success': False, 'message': '仅维修工可访问'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


def student_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
        if not request.user.is_student():
            return JsonResponse({'success': False, 'message': '仅学生可访问'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper
