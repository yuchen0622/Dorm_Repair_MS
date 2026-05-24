from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.contrib import messages
from .models import RepairRequest, RepairImage
import json


def student_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
        if not request.user.is_student():
            return JsonResponse({'success': False, 'message': '仅学生可操作'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
def my_repairs(request):
    if not request.user.is_student():
        messages.error(request, '仅学生可访问')
        return redirect('index')
    
    status = request.GET.get('status', '')
    repairs = RepairRequest.objects.filter(student=request.user).order_by('-created_at')
    if status:
        repairs = repairs.filter(status=status)
    
    paginator = Paginator(repairs, 10)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    
    context = {
        'page_obj': page_obj,
        'current_status': status,
        'total': RepairRequest.objects.filter(student=request.user).count(),
        'pending': RepairRequest.objects.filter(student=request.user, status='pending').count(),
        'processing': RepairRequest.objects.filter(student=request.user, status='processing').count(),
        'completed': RepairRequest.objects.filter(student=request.user, status='completed').count(),
    }
    return render(request, 'repairs/my_repairs.html', context)


@login_required
def repair_create(request):
    if not request.user.is_student():
        messages.error(request, '仅学生可提交报修')
        return redirect('index')
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        repair_type = request.POST.get('repair_type', 'other')
        dorm_building = request.POST.get('dorm_building', '').strip()
        dorm_room = request.POST.get('dorm_room', '').strip()
        contact_phone = request.POST.get('contact_phone', '').strip()
        
        if not all([title, description, dorm_building, dorm_room, contact_phone]):
            messages.error(request, '请填写所有必填项')
            return render(request, 'repairs/repair_create.html')
        
        repair = RepairRequest.objects.create(
            student=request.user,
            title=title,
            description=description,
            repair_type=repair_type,
            dorm_building=dorm_building,
            dorm_room=dorm_room,
            contact_phone=contact_phone
        )
        
        if request.FILES.getlist('images'):
            for image_file in request.FILES.getlist('images')[:5]:
                if image_file.size > 5 * 1024 * 1024:
                    messages.warning(request, f'图片 {image_file.name} 超过5MB，已跳过')
                    continue
                RepairImage.objects.create(
                    repair_request=repair,
                    image=image_file
                )
        
        messages.success(request, '报修单提交成功')
        return redirect('repairs:my_repairs')
    
    context = {
        'user': request.user,
    }
    return render(request, 'repairs/repair_create.html', context)


@login_required
@require_GET
def api_repair_list(request):
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    status = request.GET.get('status', '')
    
    if request.user.is_student():
        repairs = RepairRequest.objects.filter(student=request.user)
    elif request.user.is_worker():
        repairs = RepairRequest.objects.filter(status='pending')
    else:
        repairs = RepairRequest.objects.all()
    
    if status:
        repairs = repairs.filter(status=status)
    
    paginator = Paginator(repairs, page_size)
    page_obj = paginator.get_page(page)
    
    repair_list = []
    for repair in page_obj:
        images = [img.image.url for img in repair.images.all()]
        repair_list.append({
            'id': repair.id,
            'title': repair.title,
            'description': repair.description,
            'repair_type': repair.repair_type,
            'repair_type_display': repair.get_repair_type_display(),
            'dorm_building': repair.dorm_building,
            'dorm_room': repair.dorm_room,
            'contact_phone': repair.contact_phone,
            'status': repair.status,
            'status_display': repair.get_status_display(),
            'student_name': repair.student.username,
            'created_at': repair.created_at.strftime('%Y-%m-%d %H:%M'),
            'images': images
        })
    
    return JsonResponse({
        'success': True,
        'data': {
            'repairs': repair_list,
            'total': paginator.count,
            'page': page,
            'page_size': page_size,
            'total_pages': paginator.num_pages
        }
    })


@login_required
@require_GET
def api_repair_detail(request, repair_id):
    repair = get_object_or_404(RepairRequest, id=repair_id)
    
    if request.user.is_student() and repair.student != request.user:
        return JsonResponse({'success': False, 'message': '无权查看此报修单'}, status=403)
    
    images = [{'id': img.id, 'url': img.image.url} for img in repair.images.all()]
    
    return JsonResponse({
        'success': True,
        'data': {
            'id': repair.id,
            'title': repair.title,
            'description': repair.description,
            'repair_type': repair.repair_type,
            'repair_type_display': repair.get_repair_type_display(),
            'dorm_building': repair.dorm_building,
            'dorm_room': repair.dorm_room,
            'contact_phone': repair.contact_phone,
            'status': repair.status,
            'status_display': repair.get_status_display(),
            'student_id': repair.student.id,
            'student_name': repair.student.username,
            'created_at': repair.created_at.strftime('%Y-%m-%d %H:%M'),
            'updated_at': repair.updated_at.strftime('%Y-%m-%d %H:%M'),
            'images': images
        }
    })


@student_required
@require_POST
def api_repair_create(request):
    try:
        data = json.loads(request.body)
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        repair_type = data.get('repair_type', 'other')
        dorm_building = data.get('dorm_building', '').strip()
        dorm_room = data.get('dorm_room', '').strip()
        contact_phone = data.get('contact_phone', '').strip()
        
        if not all([title, description, dorm_building, dorm_room, contact_phone]):
            return JsonResponse({'success': False, 'message': '请填写所有必填项'}, status=400)
        
        repair = RepairRequest.objects.create(
            student=request.user,
            title=title,
            description=description,
            repair_type=repair_type,
            dorm_building=dorm_building,
            dorm_room=dorm_room,
            contact_phone=contact_phone
        )
        
        return JsonResponse({
            'success': True,
            'message': '报修单创建成功',
            'data': {
                'id': repair.id,
                'title': repair.title,
                'status': repair.status
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@student_required
@require_POST
def api_repair_update(request, repair_id):
    try:
        repair = get_object_or_404(RepairRequest, id=repair_id)
        
        if repair.student != request.user:
            return JsonResponse({'success': False, 'message': '无权修改此报修单'}, status=403)
        
        if repair.status != 'pending':
            return JsonResponse({'success': False, 'message': '只能修改待处理的报修单'}, status=400)
        
        data = json.loads(request.body)
        
        if 'title' in data:
            repair.title = data['title'].strip()
        if 'description' in data:
            repair.description = data['description'].strip()
        if 'repair_type' in data:
            repair.repair_type = data['repair_type']
        if 'dorm_building' in data:
            repair.dorm_building = data['dorm_building'].strip()
        if 'dorm_room' in data:
            repair.dorm_room = data['dorm_room'].strip()
        if 'contact_phone' in data:
            repair.contact_phone = data['contact_phone'].strip()
        
        repair.save()
        
        return JsonResponse({
            'success': True,
            'message': '报修单更新成功',
            'data': {
                'id': repair.id,
                'title': repair.title
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@student_required
@require_POST
def api_repair_delete(request, repair_id):
    try:
        repair = get_object_or_404(RepairRequest, id=repair_id)
        
        if repair.student != request.user:
            return JsonResponse({'success': False, 'message': '无权删除此报修单'}, status=403)
        
        if repair.status != 'pending':
            return JsonResponse({'success': False, 'message': '只能删除待处理的报修单'}, status=400)
        
        repair.delete()
        
        return JsonResponse({
            'success': True,
            'message': '报修单已删除'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
@require_POST
def api_image_upload(request, repair_id):
    try:
        repair = get_object_or_404(RepairRequest, id=repair_id)
        
        if request.user.is_student() and repair.student != request.user:
            return JsonResponse({'success': False, 'message': '无权上传图片'}, status=403)
        
        if 'image' not in request.FILES:
            return JsonResponse({'success': False, 'message': '请选择图片文件'}, status=400)
        
        image_file = request.FILES['image']
        
        if image_file.size > 5 * 1024 * 1024:
            return JsonResponse({'success': False, 'message': '图片大小不能超过5MB'}, status=400)
        
        allowed_types = ['image/jpeg', 'image/png', 'image/gif']
        if image_file.content_type not in allowed_types:
            return JsonResponse({'success': False, 'message': '仅支持JPG、PNG、GIF格式'}, status=400)
        
        if repair.images.count() >= 5:
            return JsonResponse({'success': False, 'message': '每个报修单最多上传5张图片'}, status=400)
        
        image = RepairImage.objects.create(
            repair_request=repair,
            image=image_file
        )
        
        return JsonResponse({
            'success': True,
            'message': '图片上传成功',
            'data': {
                'id': image.id,
                'url': image.image.url
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
@require_POST
def api_image_delete(request, image_id):
    try:
        image = get_object_or_404(RepairImage, id=image_id)
        
        if request.user.is_student() and image.repair_request.student != request.user:
            return JsonResponse({'success': False, 'message': '无权删除此图片'}, status=403)
        
        image.delete()
        
        return JsonResponse({
            'success': True,
            'message': '图片已删除'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
@require_GET
def api_repair_stats(request):
    if request.user.is_student():
        total = RepairRequest.objects.filter(student=request.user).count()
        pending = RepairRequest.objects.filter(student=request.user, status='pending').count()
        processing = RepairRequest.objects.filter(student=request.user, status='processing').count()
        completed = RepairRequest.objects.filter(student=request.user, status='completed').count()
    else:
        total = RepairRequest.objects.count()
        pending = RepairRequest.objects.filter(status='pending').count()
        processing = RepairRequest.objects.filter(status='processing').count()
        completed = RepairRequest.objects.filter(status='completed').count()
    
    return JsonResponse({
        'success': True,
        'data': {
            'total': total,
            'pending': pending,
            'processing': processing,
            'completed': completed
        }
    })
