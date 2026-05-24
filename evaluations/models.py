from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from workorders.models import WorkOrder


class Evaluation(models.Model):
    """
    评价模型
    学生对完成的工单进行评价，包含1-5星评分和文字评价
    用于统计维修工的服务质量
    """

    work_order = models.OneToOneField(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name='evaluation',
        verbose_name='工单'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='evaluations',
        verbose_name='评价学生'
    )
    worker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_evaluations',
        verbose_name='被评价维修工'
    )
    rating = models.IntegerField(
        '评分',
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='1-5星评分'
    )
    comment = models.TextField('评价内容', blank=True, default='')
    created_at = models.DateTimeField('评价时间', auto_now_add=True)

    class Meta:
        db_table = 'evaluations'
        verbose_name = '评价'
        verbose_name_plural = '评价'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['rating']),
            models.Index(fields=['worker']),
        ]

    def __str__(self):
        return f'评价 - {self.work_order} ({self.rating}星)'

    @property
    def rating_display(self):
        """返回星级显示字符串，如 ★★★☆☆"""
        return '★' * self.rating + '☆' * (5 - self.rating)
