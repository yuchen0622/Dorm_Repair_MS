from django.test import TestCase, Client
from django.urls import reverse
from users.models import User
from repairs.models import RepairRequest
from workorders.models import WorkOrder
from reviews.models import Review


class ReviewModelTest(TestCase):
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
            assigned_by=self.admin,
            status='completed'
        )
        self.review = Review.objects.create(
            work_order=self.work_order,
            rating=5,
            comment='非常满意'
        )
    
    def test_review_creation(self):
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.comment, '非常满意')
        self.assertEqual(self.review.work_order, self.work_order)
    
    def test_review_student_property(self):
        self.assertEqual(self.review.student, self.student)
    
    def test_review_worker_property(self):
        self.assertEqual(self.review.worker, self.worker)
    
    def test_review_str(self):
        self.assertIn('5星', str(self.review))
    
    def test_review_rating_validation(self):
        review = Review.objects.create(
            work_order=WorkOrder.objects.create(
                repair_request=RepairRequest.objects.create(
                    title='测试报修2',
                    description='描述',
                    repair_type='plumbing',
                    dorm_building='2号楼',
                    dorm_room='202',
                    contact_phone='13900139000',
                    student=self.student
                ),
                worker=self.worker,
                assigned_by=self.admin,
                status='completed'
            ),
            rating=3,
            comment='一般'
        )
        self.assertEqual(review.rating, 3)


class ReviewAPITest(TestCase):
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
        self.work_order = WorkOrder.objects.create(
            repair_request=self.repair,
            worker=self.worker,
            assigned_by=self.admin,
            status='completed'
        )
    
    def test_review_create_api(self):
        self.client.login(username='student', password='student123456')
        response = self.client.post(
            reverse('reviews:api_review_create'),
            data=f'{{"work_order_id":{self.work_order.id},"rating":5,"comment":"非常满意"}}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
    
    def test_review_list_api(self):
        Review.objects.create(
            work_order=self.work_order,
            rating=5,
            comment='满意'
        )
        self.client.login(username='student', password='student123456')
        response = self.client.get(reverse('reviews:api_review_list'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
    
    def test_worker_ranking_api(self):
        Review.objects.create(
            work_order=self.work_order,
            rating=5,
            comment='满意'
        )
        response = self.client.get(reverse('reviews:api_worker_ranking'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])


class ReviewPermissionTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.student1 = User.objects.create_user(
            username='student1',
            email='student1@test.com',
            password='student123456',
            role='student'
        )
        self.student2 = User.objects.create_user(
            username='student2',
            email='student2@test.com',
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
            title='学生1的报修',
            description='描述',
            repair_type='electrical',
            dorm_building='1号楼',
            dorm_room='101',
            contact_phone='13800138000',
            student=self.student1
        )
        self.work_order = WorkOrder.objects.create(
            repair_request=self.repair,
            worker=self.worker,
            assigned_by=self.admin,
            status='completed'
        )
    
    def test_student_cannot_review_other_order(self):
        self.client.login(username='student2', password='student123456')
        response = self.client.post(
            reverse('reviews:api_review_create'),
            data=f'{{"work_order_id":{self.work_order.id},"rating":5,"comment":"满意"}}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)
    
    def test_student_can_review_own_order(self):
        self.client.login(username='student1', password='student123456')
        response = self.client.post(
            reverse('reviews:api_review_create'),
            data=f'{{"work_order_id":{self.work_order.id},"rating":5,"comment":"满意"}}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
    
    def test_cannot_review_twice(self):
        Review.objects.create(
            work_order=self.work_order,
            rating=4,
            comment='满意'
        )
        self.client.login(username='student1', password='student123456')
        response = self.client.post(
            reverse('reviews:api_review_create'),
            data=f'{{"work_order_id":{self.work_order.id},"rating":5,"comment":"再次评价"}}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
