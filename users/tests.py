from django.test import TestCase, Client
from django.urls import reverse
from users.models import User


class UserModelTest(TestCase):
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
    
    def test_user_creation(self):
        self.assertEqual(self.student.username, 'test_student')
        self.assertEqual(self.student.role, 'student')
        self.assertTrue(self.student.check_password('test123456'))
    
    def test_user_role_methods(self):
        self.assertTrue(self.student.is_student())
        self.assertFalse(self.student.is_worker())
        self.assertFalse(self.student.is_admin())
        
        self.assertTrue(self.worker.is_worker())
        self.assertFalse(self.worker.is_student())
        
        self.assertTrue(self.admin.is_admin())
        self.assertFalse(self.admin.is_student())
    
    def test_user_str(self):
        self.assertEqual(str(self.student), 'test_student (学生)')


class UserAuthTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='test123456',
            role='student'
        )
    
    def test_login_success(self):
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'test123456'
        })
        self.assertEqual(response.status_code, 302)
    
    def test_login_fail(self):
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
    
    def test_logout(self):
        self.client.login(username='testuser', password='test123456')
        response = self.client.get(reverse('users:logout'))
        self.assertEqual(response.status_code, 302)


class UserAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='admin123456',
            role='admin'
        )
        self.student = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='student123456',
            role='student'
        )
    
    def test_user_list_api_admin(self):
        self.client.login(username='admin', password='admin123456')
        response = self.client.get(reverse('users:api_user_list'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
    
    def test_user_list_api_student(self):
        self.client.login(username='student', password='student123456')
        response = self.client.get(reverse('users:api_user_list'))
        self.assertEqual(response.status_code, 403)
    
    def test_user_detail_api(self):
        self.client.login(username='admin', password='admin123456')
        response = self.client.get(reverse('users:api_user_detail', args=[self.student.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['username'], 'student')
