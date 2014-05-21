from django.test import TestCase, TransactionTestCase
from django.test.client import Client
from django.contrib.auth.models import User
# Create your tests here.
class UserTestCase(TransactionTestCase):
    def test_user(self):
        self.assertEqual(len(User.objects.all()), 0)
        c = Client()
        # Registering a user
        c.post('/register/', {'user': 'user1', 'password': 'user1', 'password-repeat': 'user1'})
        self.assertEqual(len(User.objects.all()), 1)
        # Registering a user with a repeated username
        c = Client()
        c.post('/register/', {'user': 'user1', 'password': 'user1', 'password-repeat': 'user1'})
        self.assertEqual(len(User.objects.all()), 1)
        # Registering a user wiht missmatched password
        c = Client()
        c.post('/register/', {'user': 'user2', 'password': 'user2', 'password-repeat': 'user1'})
        self.assertEqual(len(User.objects.all()), 1)
        # Registering another user
        c = Client()
        c.post('/register/', {'user': 'user2', 'password': 'user2', 'password-repeat': 'user2'})
        self.assertEqual(len(User.objects.all()), 2)
        # Login
        c = Client()
        request = c.post('/login/', {'user': 'user1', 'password': 'user1'})
        self.assertEqual(request.status_code, 302)
        self.assertEqual(request.url, 'http://testserver/survey')
        request = c.get('/register/')
        self.assertEqual(request.status_code, 302)
        self.assertEqual(request.url, 'http://testserver/survey')
        request = c.get('/login/')
        self.assertEqual(request.status_code, 302)
        self.assertEqual(request.url, 'http://testserver/survey')
        request = c.get('/survey/')
        self.assertEqual(request.status_code, 200)
        request = c.get('/about/')
        self.assertEqual(request.status_code, 200)
        request = c.get('/ranking/')
        self.assertEqual(request.status_code, 200)
        # Logout
        request = c.get('/logout/')
        self.assertEqual(request.status_code, 200)
        request = c.get('/survey/')
        self.assertEqual(request.status_code, 302)
        self.assertEqual(request.url, 'http://testserver/login?next=/survey/')
        request = c.get('/register/')
        self.assertEqual(request.status_code, 200)
        request = c.get('/login/')
        self.assertEqual(request.status_code, 200)
        request = c.get('/about/')
        self.assertEqual(request.status_code, 200)
        request = c.get('/ranking/')
        self.assertEqual(request.status_code, 200)