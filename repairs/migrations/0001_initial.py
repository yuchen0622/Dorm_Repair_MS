
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RepairImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='repairs/%Y/%m/%d/', verbose_name='图片')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='上传时间')),
            ],
            options={
                'verbose_name': '报修图片',
                'verbose_name_plural': '报修图片',
                'db_table': 'repair_images',
            },
        ),
        migrations.CreateModel(
            name='RepairRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='报修标题')),
                ('description', models.TextField(verbose_name='问题描述')),
                ('repair_type', models.CharField(choices=[('electric', '水电'), ('door', '门窗'), ('furniture', '家具'), ('network', '网络'), ('other', '其他')], default='other', max_length=50, verbose_name='报修类型')),
                ('dorm_building', models.CharField(max_length=50, verbose_name='宿舍楼')),
                ('dorm_room', models.CharField(max_length=20, verbose_name='房间号')),
                ('contact_phone', models.CharField(max_length=20, verbose_name='联系电话')),
                ('status', models.CharField(choices=[('pending', '待处理'), ('processing', '处理中'), ('completed', '已完成'), ('cancelled', '已取消')], default='pending', max_length=20, verbose_name='状态')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '报修单',
                'verbose_name_plural': '报修单',
                'db_table': 'repair_requests',
                'ordering': ['-created_at'],
            },
        ),
    ]
