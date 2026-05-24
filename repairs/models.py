from django.db import models
from django.conf import settings


class RepairRequest(models.Model):
    """
    报修单模型
    学生提交的报修申请，包含问题描述、宿舍位置、联系方式等信息
    """

    TYPE_CHOICES = [
        ('electric', '水电'),
        ('door', '门窗'),
        ('furniture', '家具'),
        ('network', '网络'),
        ('other', '其他'),
    ]

    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='repair_requests',
        verbose_name='报修学生'
    )
    title = models.CharField('报修标题', max_length=100)
    description = models.TextField('问题描述')
    repair_type = models.CharField('报修类型', max_length=50, choices=TYPE_CHOICES, default='other')
    dorm_building = models.CharField('宿舍楼', max_length=50)
    dorm_room = models.CharField('房间号', max_length=20)
    contact_phone = models.CharField('联系电话', max_length=20)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'repair_requests'
        verbose_name = '报修单'
        verbose_name_plural = '报修单'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f'{self.title} - {self.get_status_display()}'


class RepairImage(models.Model):
    """
    报修图片模型
    用于存储报修单附带的问题图片，支持多图上传
    """

    repair_request = models.ForeignKey(
        RepairRequest,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='报修单'
    )
    image = models.ImageField('图片', upload_to='repairs/%Y/%m/%d/')
    uploaded_at = models.DateTimeField('上传时间', auto_now_add=True)

    class Meta:
        db_table = 'repair_images'
        verbose_name = '报修图片'
        verbose_name_plural = '报修图片'

    def __str__(self):
        return f'图片 - {self.repair_request.title}'
