from django.test import TestCase, TransactionTestCase
from django.test.client import Client
from django.contrib.auth.models import User
from survey.models import Dataset, Similarity
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

class RatingTestCase(TransactionTestCase):
    def setUp(self):
        for i in range(4):
            c = Client()
            c.post('/register/', {'user': 'user%s' % i, 'password': 'user%s' % i, 'password-repeat': 'user%s' % i})
        for i in range(10):
            d = Dataset()
            d.save()


    def test_rating(self):
        for user in User.objects.all():
            c = Client()
            c.post('/login/', {'user': user.username, 'password': user.username})
            end = False
            while not end:
                request = c.get('/survey')
                source_dataset = request.context['source_dataset']
                if source_dataset == None:
                    break
                target_dataset = request.context['target_dataset']
                sim = Similarity.objects.filter(source_dataset=source_dataset, target_dataset=target_dataset)
                self.assertTrue(len(sim) <= 3)
                try:
                    user_rating = user.userprofile.rated_datasets.get(source_dataset=source_dataset, target_dataset=target_dataset)
                except:
                    user_rating = None
                self.assertEqual(user_rating, None)
                c.post('/survey', {'source_dataset_id': source_dataset.id, 'target_dataset_id': target_dataset.id, 'similarity': 'yes'})
