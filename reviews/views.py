from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json

from .models import Review
from workorders.models import WorkOrder
from users.decorators import student_required


@student_required
def review_create(request, work_order_id):
    work_order = get_object_or_404(WorkOrder, id=work_order_id)
    
    if work_order.repair_request.student != request.user:
        messages.error(request, '无权评价此工单')
        return redirect('repairs:my_repairs')
    
    if work_order.status != 'completed':
        messages.error(request, '只能评价已完成的工单')
        return redirect('repairs:my_repairs')
    
    if hasattr(work_order, 'review'):
        messages.error(request, '该工单已评价')
        return redirect('repairs:my_repairs')
    
    return render(request, 'reviews/review_create.html', {'work_order': work_order})


@login_required
def review_stats(request):
    return render(request, 'reviews/review_stats.html')


@student_required
@require_POST
def api_review_create(request):
    try:
        data = json.loads(request.body)
        work_order_id = data.get('work_order_id')
        rating = data.get('rating')
        comment = data.get('comment', '').strip()
        
        if not work_order_id or not rating:
            return JsonResponse({'success': False, 'message': '工单ID和评分为必填项'}, status=400)
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                return JsonResponse({'success': False, 'message': '评分必须在1-5之间'}, status=400)
        except ValueError:
            return JsonResponse({'success': False, 'message': '评分格式错误'}, status=400)
        
        work_order = get_object_or_404(WorkOrder, id=work_order_id)
        
        if work_order.repair_request.student != request.user:
            return JsonResponse({'success': False, 'message': '无权评价此工单'}, status=403)
        
        if work_order.status != 'completed':
            return JsonResponse({'success': False, 'message': '只能评价已完成的工单'}, status=400)
        
        if hasattr(work_order, 'review'):
            return JsonResponse({'success': False, 'message': '该工单已评价'}, status=400)
        
        review = Review.objects.create(
            work_order=work_order,
            rating=rating,
            comment=comment
        )
        
        return JsonResponse({
            'success': True,
            'message': '评价成功',
            'data': {
                'id': review.id,
                'rating': review.rating,
                'comment': review.comment,
                'created_at': review.created_at.strftime('%Y-%m-%d %H:%M')
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
@require_GET
def api_review_detail(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    return JsonResponse({
        'success': True,
        'data': {
            'id': review.id,
            'work_order_id': review.work_order.id,
            'repair_title': review.work_order.repair_request.title,
            'rating': review.rating,
            'rating_display': review.get_rating_display(),
            'comment': review.comment,
            'student_name': review.student.username,
            'worker_name': review.worker.username if review.worker else None,
            'created_at': review.created_at.strftime('%Y-%m-%d %H:%M')
        }
    })


@login_required
@require_GET
def api_review_list(request):
    reviews = Review.objects.all()
    
    worker_id = request.GET.get('worker_id')
    if worker_id:
        reviews = reviews.filter(work_order__worker_id=worker_id)
    
    student_id = request.GET.get('student_id')
    if student_id:
        reviews = reviews.filter(work_order__repair_request__student_id=student_id)
    
    min_rating = request.GET.get('min_rating')
    if min_rating:
        reviews = reviews.filter(rating__gte=min_rating)
    
    reviews = reviews.order_by('-created_at')
    
    result = []
    for r in reviews:
        result.append({
            'id': r.id,
            'work_order_id': r.work_order.id,
            'repair_title': r.work_order.repair_request.title,
            'rating': r.rating,
            'rating_display': r.get_rating_display(),
            'comment': r.comment,
            'student_name': r.student.username,
            'worker_name': r.worker.username if r.worker else None,
            'created_at': r.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return JsonResponse({
        'success': True,
        'data': result
    })


@require_GET
def api_review_stats(request):
    from django.db.models import Avg, Count
    
    worker_id = request.GET.get('worker_id')
    
    if worker_id:
        reviews = Review.objects.filter(work_order__worker_id=worker_id)
    else:
        reviews = Review.objects.all()
    
    total = reviews.count()
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    
    rating_distribution = {}
    for i in range(1, 6):
        rating_distribution[i] = reviews.filter(rating=i).count()
    
    return JsonResponse({
        'success': True,
        'data': {
            'total': total,
            'avg_rating': round(avg_rating, 2),
            'rating_distribution': rating_distribution
        }
    })


@require_GET
def api_worker_ranking(request):
    from django.db.models import Avg, Count
    
    workers = Review.objects.values(
        'work_order__worker__id',
        'work_order__worker__username'
    ).annotate(
        avg_rating=Avg('rating'),
        review_count=Count('id')
    ).order_by('-avg_rating', '-review_count')
    
    result = []
    for i, w in enumerate(workers, 1):
        if w['work_order__worker__id']:
            result.append({
                'rank': i,
                'worker_id': w['work_order__worker__id'],
                'worker_name': w['work_order__worker__username'],
                'avg_rating': round(w['avg_rating'], 2) if w['avg_rating'] else 0,
                'review_count': w['review_count']
            })
    
    return JsonResponse({
        'success': True,
        'data': result
    })
