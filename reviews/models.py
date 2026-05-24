from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    RATING_CHOICES = [
        (1, '1星 - 很差'),
        (2, '2星 - 较差'),
        (3, '3星 - 一般'),
        (4, '4星 - 较好'),
        (5, '5星 - 很好'),
    ]
    
    work_order = models.OneToOneField(
        'workorders.WorkOrder',
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name='工单'
    )
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='评分'
    )
    comment = models.TextField(blank=True, default='', verbose_name='评价内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='评价时间')
    
    class Meta:
        db_table = 'reviews'
        verbose_name = '评价'
        verbose_name_plural = '评价'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.work_order} - {self.rating}星'
    
    @property
    def student(self):
        return self.work_order.repair_request.student
    
    @property
    def worker(self):
        return self.work_order.worker
