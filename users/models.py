from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    自定义用户模型
    继承Django内置的AbstractUser，扩展角色、电话、宿舍信息等字段
    支持三种角色：学生、维修工、管理员
    """
    
    ROLE_CHOICES = [
        ('student', '学生'),
        ('worker', '维修工'),
        ('admin', '管理员'),
    ]

    role = models.CharField('角色', max_length=20, choices=ROLE_CHOICES, default='student')
    phone = models.CharField('联系电话', max_length=20, blank=True, default='')
    dorm_building = models.CharField('宿舍楼', max_length=50, blank=True, default='')
    dorm_room = models.CharField('宿舍房间号', max_length=20, blank=True, default='')
    specialty = models.CharField('维修专长', max_length=50, blank=True, default='')

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'

    def is_student(self):
        """判断当前用户是否为学生"""
        return self.role == 'student'

    def is_worker(self):
        """判断当前用户是否为维修工"""
        return self.role == 'worker'

    def is_admin(self):
        """判断当前用户是否为管理员"""
        return self.role == 'admin'
