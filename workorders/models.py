from django.db import models
from django.conf import settings
from repairs.models import RepairRequest


class WorkOrder(models.Model):
    """
    工单模型
    管理员派单后生成工单，维修工接单并完成维修
    记录整个维修流程的时间节点和状态变化
    """

    STATUS_CHOICES = [
        ('assigned', '已派单'),
        ('accepted', '已接单'),
        ('in_progress', '维修中'),
        ('completed', '已完成'),
        ('rejected', '已拒绝'),
    ]

    repair_request = models.OneToOneField(
        RepairRequest,
        on_delete=models.CASCADE,
        related_name='work_order',
        verbose_name='报修单'
    )
    worker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_orders',
        verbose_name='维修工'
    )
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='assigned')
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_orders',
        verbose_name='派单管理员'
    )
    assigned_at = models.DateTimeField('派单时间', auto_now_add=True)
    accepted_at = models.DateTimeField('接单时间', null=True, blank=True)
    started_at = models.DateTimeField('开始维修时间', null=True, blank=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    remark = models.TextField('维修备注', blank=True, default='')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'work_orders'
        verbose_name = '工单'
        verbose_name_plural = '工单'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['worker']),
        ]

    def __str__(self):
        return f'工单 #{self.id} - {self.get_status_display()}'

    def can_accept(self):
        return self.status == 'assigned'

    def can_start(self):
        return self.status == 'accepted'

    def can_complete(self):
        return self.status == 'in_progress'

    def can_reject(self):
        return self.status in ['assigned', 'accepted']

    def accept(self, operator=None):
        from django.utils import timezone
        if not self.can_accept():
            raise ValueError('当前状态不允许接单')
        self.status = 'accepted'
        self.accepted_at = timezone.now()
        self.save()
        self._create_log('accept', '维修工接单', operator)

    def start_work(self, operator=None):
        from django.utils import timezone
        if not self.can_start():
            raise ValueError('当前状态不允许开始维修')
        self.status = 'in_progress'
        self.started_at = timezone.now()
        self.save()
        self._create_log('start', '开始维修', operator)

    def complete(self, remark='', operator=None):
        from django.utils import timezone
        if not self.can_complete():
            raise ValueError('当前状态不允许完成')
        self.status = 'completed'
        self.completed_at = timezone.now()
        if remark:
            self.remark = remark
        self.save()
        self._create_log('complete', f'完成维修: {remark}', operator)
        self.repair_request.status = 'completed'
        self.repair_request.save()

    def reject(self, reason='', operator=None):
        if not self.can_reject():
            raise ValueError('当前状态不允许拒绝')
        self.status = 'rejected'
        self.save()
        self._create_log('reject', f'拒绝工单: {reason}', operator)

    def _create_log(self, action, description, operator):
        WorkOrderLog.objects.create(
            work_order=self,
            operator=operator,
            action=action,
            description=description
        )


class WorkOrderLog(models.Model):
    """
    工单日志模型
    记录工单的所有操作历史，便于追溯和审计
    """

    ACTION_CHOICES = [
        ('assign', '派单'),
        ('accept', '接单'),
        ('start', '开始维修'),
        ('complete', '完成维修'),
        ('reject', '拒绝'),
        ('update', '更新'),
    ]

    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='工单'
    )
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='操作人'
    )
    action = models.CharField('操作类型', max_length=50, choices=ACTION_CHOICES)
    description = models.TextField('操作描述', blank=True, default='')
    created_at = models.DateTimeField('操作时间', auto_now_add=True)

    class Meta:
        db_table = 'work_order_logs'
        verbose_name = '工单日志'
        verbose_name_plural = '工单日志'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.work_order} - {self.get_action_display()}'
