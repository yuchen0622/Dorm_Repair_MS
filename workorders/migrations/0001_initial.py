
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('repairs', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('assigned', '已派单'), ('accepted', '已接单'), ('in_progress', '维修中'), ('completed', '已完成'), ('rejected', '已拒绝')], default='assigned', max_length=20, verbose_name='状态')),
                ('assigned_at', models.DateTimeField(auto_now_add=True, verbose_name='派单时间')),
                ('accepted_at', models.DateTimeField(blank=True, null=True, verbose_name='接单时间')),
                ('started_at', models.DateTimeField(blank=True, null=True, verbose_name='开始维修时间')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='完成时间')),
                ('remark', models.TextField(blank=True, default='', verbose_name='维修备注')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('assigned_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_orders', to=settings.AUTH_USER_MODEL, verbose_name='派单管理员')),
                ('repair_request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='work_order', to='repairs.repairrequest', verbose_name='报修单')),
                ('worker', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='work_orders', to=settings.AUTH_USER_MODEL, verbose_name='维修工')),
            ],
            options={
                'verbose_name': '工单',
                'verbose_name_plural': '工单',
                'db_table': 'work_orders',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='WorkOrderLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('assign', '派单'), ('accept', '接单'), ('start', '开始维修'), ('complete', '完成维修'), ('reject', '拒绝'), ('update', '更新')], max_length=50, verbose_name='操作类型')),
                ('description', models.TextField(blank=True, default='', verbose_name='操作描述')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='操作时间')),
                ('operator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='操作人')),
                ('work_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='workorders.workorder', verbose_name='工单')),
            ],
            options={
                'verbose_name': '工单日志',
                'verbose_name_plural': '工单日志',
                'db_table': 'work_order_logs',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='workorder',
            index=models.Index(fields=['status'], name='work_orders_status_3f6c76_idx'),
        ),
        migrations.AddIndex(
            model_name='workorder',
            index=models.Index(fields=['worker'], name='work_orders_worker__2f7638_idx'),
        ),
    ]
