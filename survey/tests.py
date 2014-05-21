from django.test import TestCase, TransactionTestCase
from django.test.client import Client
from django.contrib.auth.models import User
# Create your tests here.
class UserTestCase(TransactionTestCase):
    def test_register_user(self):
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

    def test_user_access(self):
        c = Client()
        request = c.post('/login/', {'user': 'user1', 'password': 'user1'})
        print request, url