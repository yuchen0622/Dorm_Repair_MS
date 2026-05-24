from django.test import TestCase, Client
from django.urls import reverse
from users.models import User
from repairs.models import RepairRequest, RepairImage


class RepairModelTest(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username='test_student',
            email='student@test.com',
            password='test123456',
            role='student'
        )
        self.repair = RepairRequest.objects.create(
            title='测试报修',
            description='测试描述',
            repair_type='electrical',
            dorm_building='1号楼',
            dorm_room='101',
            contact_phone='13800138000',
            student=self.student
        )
    
    def test_repair_creation(self):
        self.assertEqual(self.repair.title, '测试报修')
        self.assertEqual(self.repair.status, 'pending')
        self.assertEqual(self.repair.student, self.student)
    
    def test_repair_status(self):
        self.assertEqual(self.repair.get_status_display(), '待处理')
        self.repair.status = 'processing'
        self.repair.save()
        self.assertEqual(self.repair.get_status_display(), '处理中')
    
    def test_repair_str(self):
        self.assertEqual(str(self.repair), '测试报修 - 待处理')


class RepairAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='student123456',
            role='student'
        )
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='admin123456',
            role='admin'
        )
        self.repair = RepairRequest.objects.create(
            title='测试报修',
            description='测试描述',
            repair_type='electrical',
            dorm_building='1号楼',
            dorm_room='101',
            contact_phone='13800138000',
            student=self.student
        )
    
    def test_repair_create_api(self):
        self.client.login(username='student', password='student123456')
        response = self.client.post(
            reverse('repairs:api_repair_create'),
            data='{"title":"新报修","description":"描述","repair_type":"plumbing","dorm_building":"2号楼","dorm_room":"202","contact_phone":"13900139000"}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
    
    def test_repair_list_api(self):
        self.client.login(username='student', password='student123456')
        response = self.client.get(reverse('repairs:api_repair_list'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
    
    def test_repair_detail_api(self):
        self.client.login(username='student', password='student123456')
        response = self.client.get(reverse('repairs:api_repair_detail', args=[self.repair.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['title'], '测试报修')
    
    def test_repair_update_api(self):
        self.client.login(username='student', password='student123456')
        response = self.client.post(
            reverse('repairs:api_repair_update', args=[self.repair.id]),
            data='{"title":"更新标题","description":"更新描述"}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
    
    def test_repair_delete_api(self):
        self.client.login(username='student', password='student123456')
        response = self.client.post(reverse('repairs:api_repair_delete', args=[self.repair.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
    
    def test_repair_stats_api(self):
        self.client.login(username='student', password='student123456')
        response = self.client.get(reverse('repairs:api_repair_stats'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])


class RepairPermissionTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.student1 = User.objects.create_user(
            username='student1',
            email='student1@test.com',
            password='test123456',
            role='student'
        )
        self.student2 = User.objects.create_user(
            username='student2',
            email='student2@test.com',
            password='test123456',
            role='student'
        )
        self.repair = RepairRequest.objects.create(
            title='学生1的报修',
            description='描述',
            repair_type='electrical',
            dorm_building='1号楼',
            dorm_room='101',
            contact_phone='13800138000',
            student=self.student1
        )
    
    def test_student_cannot_access_other_repair(self):
        self.client.login(username='student2', password='test123456')
        response = self.client.post(
            reverse('repairs:api_repair_update', args=[self.repair.id]),
            data='{"title":"恶意修改"}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)
    
    def test_student_can_access_own_repair(self):
        self.client.login(username='student1', password='test123456')
        response = self.client.get(reverse('repairs:api_repair_detail', args=[self.repair.id]))
        self.assertEqual(response.status_code, 200)
