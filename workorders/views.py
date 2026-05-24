from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
import json

from .models import WorkOrder, WorkOrderLog
from repairs.models import RepairRequest


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
        if not request.user.is_admin():
            return JsonResponse({'success': False, 'message': '仅管理员可操作'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


def worker_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
        if not request.user.is_worker():
            return JsonResponse({'success': False, 'message': '仅维修工可操作'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
def assign_page(request, repair_id):
    if not request.user.is_admin():
        messages.error(request, '仅管理员可访问')
        return redirect('index')
    
    repair = get_object_or_404(RepairRequest, id=repair_id)
    
    if hasattr(repair, 'work_order'):
        messages.warning(request, '该报修单已派单')
        return redirect('repairs:repair_manage')
    
    from users.models import User
    workers = User.objects.filter(role='worker')
    
    context = {
        'repair': repair,
        'workers': workers,
    }
    return render(request, 'workorders/assign.html', context)


@admin_required
@require_GET
def api_worker_list(request):
    from users.models import User
    workers = User.objects.filter(role='worker')
    
    worker_list = []
    for w in workers:
        pending_count = WorkOrder.objects.filter(worker=w, status='assigned').count()
        processing_count = WorkOrder.objects.filter(worker=w, status__in=['accepted', 'in_progress']).count()
        worker_list.append({
            'id': w.id,
            'username': w.username,
            'phone': w.phone or '',
            'pending_count': pending_count,
            'processing_count': processing_count,
        })
    
    return JsonResponse({
        'success': True,
        'data': workers
    })


@admin_required
@require_POST
def api_assign(request):
    try:
        data = json.loads(request.body)
        repair_id = data.get('repair_id')
        worker_id = data.get('worker_id')
        remark = data.get('remark', '')
        
        if not repair_id or not worker_id:
            return JsonResponse({'success': False, 'message': '参数不完整'}, status=400)
        
        repair = get_object_or_404(RepairRequest, id=repair_id)
        
        if hasattr(repair, 'work_order'):
            return JsonResponse({'success': False, 'message': '该报修单已派单'}, status=400)
        
        from users.models import User
        worker = get_object_or_404(User, id=worker_id, role='worker')
        
        with transaction.atomic():
            work_order = WorkOrder.objects.create(
                repair_request=repair,
                worker=worker,
                assigned_by=request.user,
                remark=remark
            )
            
            WorkOrderLog.objects.create(
                work_order=work_order,
                operator=request.user,
                action='assign',
                description=f'派单给维修工: {worker.username}'
            )
            
            repair.status = 'processing'
            repair.save()
        
        send_notification(worker, '派单通知', f'您有新的工单: {repair.title}')
        
        return JsonResponse({
            'success': True,
            'message': '派单成功',
            'data': {
                'work_order_id': work_order.id,
                'worker_name': worker.username
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@admin_required
@require_POST
def api_reassign(request):
    try:
        data = json.loads(request.body)
        work_order_id = data.get('work_order_id')
        new_worker_id = data.get('worker_id')
        
        if not work_order_id or not new_worker_id:
            return JsonResponse({'success': False, 'message': '参数不完整'}, status=400)
        
        work_order = get_object_or_404(WorkOrder, id=work_order_id)
        
        if work_order.status not in ['assigned', 'accepted']:
            return JsonResponse({'success': False, 'message': '当前状态不允许重新派单'}, status=400)
        
        from users.models import User
        new_worker = get_object_or_404(User, id=new_worker_id, role='worker')
        
        old_worker = work_order.worker
        work_order.worker = new_worker
        work_order.status = 'assigned'
        work_order.accepted_at = None
        work_order.save()
        
        WorkOrderLog.objects.create(
            work_order=work_order,
            operator=request.user,
            action='assign',
            description=f'重新派单: {old_worker.username if old_worker else "无"} -> {new_worker.username}'
        )
        
        send_notification(new_worker, '派单通知', f'您有新的工单: {work_order.repair_request.title}')
        
        return JsonResponse({
            'success': True,
            'message': '重新派单成功',
            'data': {
                'work_order_id': work_order.id,
                'worker_name': new_worker.username
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@admin_required
@require_GET
def api_work_order_list(request):
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    status = request.GET.get('status', '')
    worker_id = request.GET.get('worker_id', '')
    
    work_orders = WorkOrder.objects.all()
    
    if status:
        work_orders = work_orders.filter(status=status)
    if worker_id:
        work_orders = work_orders.filter(worker_id=worker_id)
    
    work_orders = work_orders.order_by('-created_at')
    
    from django.core.paginator import Paginator
    paginator = Paginator(work_orders, page_size)
    page_obj = paginator.get_page(page)
    
    result = []
    for wo in page_obj:
        result.append({
            'id': wo.id,
            'repair_id': wo.repair_request.id,
            'repair_title': wo.repair_request.title,
            'repair_type': wo.repair_request.get_repair_type_display(),
            'dorm': f'{wo.repair_request.dorm_building} {wo.repair_request.dorm_room}',
            'worker_id': wo.worker.id if wo.worker else None,
            'worker_name': wo.worker.username if wo.worker else None,
            'status': wo.status,
            'status_display': wo.get_status_display(),
            'assigned_at': wo.assigned_at.strftime('%Y-%m-%d %H:%M'),
            'accepted_at': wo.accepted_at.strftime('%Y-%m-%d %H:%M') if wo.accepted_at else None,
            'completed_at': wo.completed_at.strftime('%Y-%m-%d %H:%M') if wo.completed_at else None,
        })
    
    return JsonResponse({
        'success': True,
        'data': {
            'work_orders': result,
            'total': paginator.count,
            'page': page,
            'total_pages': paginator.num_pages
        }
    })


@admin_required
@require_GET
def api_work_order_detail(request, work_order_id):
    work_order = get_object_or_404(WorkOrder, id=work_order_id)
    
    logs = []
    for log in work_order.logs.all():
        logs.append({
            'action': log.get_action_display(),
            'operator': log.operator.username if log.operator else '系统',
            'description': log.description,
            'created_at': log.created_at.strftime('%Y-%m-%d %H:%M'),
        })
    
    return JsonResponse({
        'success': True,
        'data': {
            'id': work_order.id,
            'repair_id': work_order.repair_request.id,
            'repair_title': work_order.repair_request.title,
            'repair_description': work_order.repair_request.description,
            'repair_type': work_order.repair_request.get_repair_type_display(),
            'dorm_building': work_order.repair_request.dorm_building,
            'dorm_room': work_order.repair_request.dorm_room,
            'contact_phone': work_order.repair_request.contact_phone,
            'worker_id': work_order.worker.id if work_order.worker else None,
            'worker_name': work_order.worker.username if work_order.worker else None,
            'worker_phone': work_order.worker.phone if work_order.worker else None,
            'status': work_order.status,
            'status_display': work_order.get_status_display(),
            'assigned_by': work_order.assigned_by.username if work_order.assigned_by else None,
            'assigned_at': work_order.assigned_at.strftime('%Y-%m-%d %H:%M'),
            'accepted_at': work_order.accepted_at.strftime('%Y-%m-%d %H:%M') if work_order.accepted_at else None,
            'started_at': work_order.started_at.strftime('%Y-%m-%d %H:%M') if work_order.started_at else None,
            'completed_at': work_order.completed_at.strftime('%Y-%m-%d %H:%M') if work_order.completed_at else None,
            'remark': work_order.remark,
            'logs': logs,
        }
    })


@worker_required
@require_POST
def api_accept(request, work_order_id):
    try:
        work_order = get_object_or_404(WorkOrder, id=work_order_id)
        
        if work_order.worker != request.user:
            return JsonResponse({'success': False, 'message': '这不是您的工单'}, status=403)
        
        work_order.accept(operator=request.user)
        
        return JsonResponse({
            'success': True,
            'message': '接单成功'
        })
    except ValueError as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@worker_required
@require_POST
def api_start_work(request, work_order_id):
    try:
        work_order = get_object_or_404(WorkOrder, id=work_order_id)
        
        if work_order.worker != request.user:
            return JsonResponse({'success': False, 'message': '这不是您的工单'}, status=403)
        
        work_order.start_work(operator=request.user)
        
        return JsonResponse({
            'success': True,
            'message': '已开始维修'
        })
    except ValueError as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@worker_required
@require_POST
def api_complete(request, work_order_id):
    try:
        work_order = get_object_or_404(WorkOrder, id=work_order_id)
        
        if work_order.worker != request.user:
            return JsonResponse({'success': False, 'message': '这不是您的工单'}, status=403)
        
        data = json.loads(request.body) if request.body else {}
        remark = data.get('remark', '')
        
        work_order.complete(remark=remark, operator=request.user)
        
        send_notification(
            work_order.repair_request.student,
            '维修完成通知',
            f'您的报修单 "{work_order.repair_request.title}" 已完成维修'
        )
        
        return JsonResponse({
            'success': True,
            'message': '维修完成'
        })
    except ValueError as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@worker_required
@require_POST
def api_reject(request, work_order_id):
    try:
        work_order = get_object_or_404(WorkOrder, id=work_order_id)
        
        if work_order.worker != request.user:
            return JsonResponse({'success': False, 'message': '这不是您的工单'}, status=403)
        
        data = json.loads(request.body) if request.body else {}
        reason = data.get('reason', '')
        
        work_order.reject(reason=reason, operator=request.user)
        
        work_order.repair_request.status = 'pending'
        work_order.repair_request.save()
        
        return JsonResponse({
            'success': True,
            'message': '已拒绝工单'
        })
    except ValueError as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


def send_notification(user, title, content):
    print(f'[通知] 用户: {user.username}, 标题: {title}, 内容: {content}')
