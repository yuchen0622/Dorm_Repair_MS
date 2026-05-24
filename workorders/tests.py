from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from users.models import User
from repairs.models import RepairRequest
from workorders.models import WorkOrder, WorkOrderLog


class WorkOrderModelTest(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username='test_student',
            email='student@test.com',
            password='test123456',
            role='student'
        )
        self.worker = User.objects.create_user(
            username='test_worker',
            email='worker@test.com',
            password='test123456',
            role='worker'
        )
        self.admin = User.objects.create_user(
            username='test_admin',
            email='admin@test.com',
            password='test123456',
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
        self.work_order = WorkOrder.objects.create(
            repair_request=self.repair,
            worker=self.worker,
            assigned_by=self.admin
        )
    
    def test_work_order_creation(self):
        self.assertEqual(self.work_order.status, 'assigned')
        self.assertEqual(self.work_order.worker, self.worker)
        self.assertEqual(self.work_order.assigned_by, self.admin)
    
    def test_work_order_status_methods(self):
        self.assertTrue(self.work_order.can_accept())
        self.assertFalse(self.work_order.can_start())
        self.assertFalse(self.work_order.can_complete())
        self.assertTrue(self.work_order.can_reject())
    
    def test_work_order_accept(self):
        self.work_order.accept()
        self.assertEqual(self.work_order.status, 'accepted')
        self.assertIsNotNone(self.work_order.accepted_at)
        self.assertFalse(self.work_order.can_accept())
        self.assertTrue(self.work_order.can_start())
    
    def test_work_order_start(self):
        self.work_order.accept()
        self.work_order.start_work()
        self.assertEqual(self.work_order.status, 'in_progress')
        self.assertIsNotNone(self.work_order.started_at)
    
    def test_work_order_complete(self):
        self.work_order.accept()
        self.work_order.start_work()
        self.work_order.complete('维修完成')
        self.assertEqual(self.work_order.status, 'completed')
        self.assertIsNotNone(self.work_order.completed_at)
        self.assertEqual(self.work_order.remark, '维修完成')
    
    def test_work_order_reject(self):
        self.work_order.reject('无法维修')
        self.assertEqual(self.work_order.status, 'rejected')
    
    def test_work_order_str(self):
        self.assertIn('工单', str(self.work_order))
        self.assertIn('已派单', str(self.work_order))


class WorkOrderAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='student123456',
            role='student'
        )
        self.worker = User.objects.create_user(
            username='worker',
            email='worker@test.com',
            password='worker123456',
            role='worker'
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
    
    def test_assign_work_order_api(self):
        self.client.login(username='admin', password='admin123456')
        response = self.client.post(
            reverse('workorders:api_assign'),
            data=f'{{"repair_id":{self.repair.id},"worker_id":{self.worker.id}}}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
    
    def test_accept_work_order_api(self):
        work_order = WorkOrder.objects.create(
            repair_request=self.repair,
            worker=self.worker,
            assigned_by=self.admin
        )
        self.client.login(username='worker', password='worker123456')
        response = self.client.post(
            reverse('workorders:api_accept', args=[work_order.id])
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
    
    def test_worker_work_order_detail_api(self):
        work_order = WorkOrder.objects.create(
            repair_request=self.repair,
            worker=self.worker,
            assigned_by=self.admin
        )
        self.client.login(username='worker', password='worker123456')
        response = self.client.get(reverse('workorders:api_work_order_detail', args=[work_order.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])


class WorkOrderPermissionTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='student123456',
            role='student'
        )
        self.worker1 = User.objects.create_user(
            username='worker1',
            email='worker1@test.com',
            password='worker123456',
            role='worker'
        )
        self.worker2 = User.objects.create_user(
            username='worker2',
            email='worker2@test.com',
            password='worker123456',
            role='worker'
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
        self.work_order = WorkOrder.objects.create(
            repair_request=self.repair,
            worker=self.worker1,
            assigned_by=self.admin
        )
    
    def test_worker_cannot_accept_other_order(self):
        self.client.login(username='worker2', password='worker123456')
        response = self.client.post(
            reverse('workorders:api_accept', args=[self.work_order.id])
        )
        self.assertEqual(response.status_code, 403)
    
    def test_student_cannot_assign_order(self):
        self.client.login(username='student', password='student123456')
        repair2 = RepairRequest.objects.create(
            title='测试报修2',
            description='描述',
            repair_type='plumbing',
            dorm_building='2号楼',
            dorm_room='202',
            contact_phone='13900139000',
            student=self.student
        )
        response = self.client.post(
            reverse('workorders:api_assign'),
            data=f'{{"repair_id":{repair2.id},"worker_id":{self.worker1.id}}}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)
