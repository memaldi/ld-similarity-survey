import itertools
import redis
from django.test import TestCase, TransactionTestCase
from django.test.client import Client
from django.contrib.auth.models import User
from survey.models import Dataset, Similarity
from random import randint
from scripts import kappa

r = redis.StrictRedis(host='localhost', port=6379, db=0)

# Create your tests here.
class UserTestCase(TransactionTestCase):
    def set_up(self):
        keys = r.keys('ld_survey:similarity:*')
        for key in keys:
            r.delete(key)
        for i in range(6):
            d = Dataset()
            d.save()
        combinations = itertools.combinations(Dataset.objects.all(), 2)
        print 'Creating similarities...'
        for source_dataset, target_dataset in combinations:
            similarity = Similarity(source_dataset=source_dataset, target_dataset=target_dataset, similarity=None)
            similarity.save()

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
        keys = r.keys('ld_survey:similarity:*')
        for key in keys:
            r.delete(key)
        for i in range(4):
            c = Client()
            c.post('/register/', {'user': 'user%s' % i, 'password': 'user%s' % i, 'password-repeat': 'user%s' % i})
        for i in range(5):
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

class RankingTestCase(TransactionTestCase):
    def setUp(self):
        keys = r.keys('ld_survey:similarity:*')
        for key in keys:
            r.delete(key)
        for i in range(4):
            c = Client()
            c.post('/register/', {'user': 'user%s' % i, 'password': 'user%s' % i, 'password-repeat': 'user%s' % i})
        for i in range(5):
            d = Dataset()
            d.save()
        combinations = itertools.combinations(Dataset.objects.all(), 2)
        for source_dataset, target_dataset in combinations:
            for i in range(3):
                similarity = Similarity(source_dataset=source_dataset, target_dataset=target_dataset, similarity=None)
                similarity.save()

    def test_ranking(self):
        c = Client()
        c.post('/login/', {'user': 'user0', 'password': 'user0'})
        for i in range(4):
            request = c.get('/survey')
            source_dataset = request.context['source_dataset']
            target_dataset = request.context['target_dataset']
            sim_id = request.context['sim_id']
            c.post('/survey', {'source_dataset_id': source_dataset.id, 'target_dataset_id': target_dataset.id, 'similarity': 'yes', 'sim_id': sim_id})

        c = Client()
        c.post('/login/', {'user': 'user1', 'password': 'user1'})
        for i in range(3):
            request = c.get('/survey')
            source_dataset = request.context['source_dataset']
            target_dataset = request.context['target_dataset']
            sim_id = request.context['sim_id']
            c.post('/survey', {'source_dataset_id': source_dataset.id, 'target_dataset_id': target_dataset.id, 'similarity': 'yes', 'sim_id': sim_id})

        c = Client()
        c.post('/login/', {'user': 'user2', 'password': 'user2'})
        for i in range(2):
            request = c.get('/survey')
            source_dataset = request.context['source_dataset']
            target_dataset = request.context['target_dataset']
            sim_id = request.context['sim_id']
            c.post('/survey', {'source_dataset_id': source_dataset.id, 'target_dataset_id': target_dataset.id, 'similarity': 'yes', 'sim_id': sim_id})

        c = Client()
        c.post('/login/', {'user': 'user3', 'password': 'user3'})
        for i in range(1):
            request = c.get('/survey')
            source_dataset = request.context['source_dataset']
            target_dataset = request.context['target_dataset']
            sim_id = request.context['sim_id']
            c.post('/survey', {'source_dataset_id': source_dataset.id, 'target_dataset_id': target_dataset.id, 'similarity': 'yes', 'sim_id': sim_id})

        request = c.get('/ranking/')
        user_list = {}
        for user_profile in request.context['user_profiles']:
            user_list[user_profile.user.username] = user_profile.points

        self.assertTrue(user_list == {'user0': 4, 'user1': 3, 'user2': 2, 'user3': 1})

class KappaTestCase(TestCase):

    def setUp(self):
        OPTIONS = ['yes', 'no', 'undefined']

        for i in range(4):
            c = Client()
            c.post('/register/', {'user': 'user%s' % i, 'password': 'user%s' % i, 'password-repeat': 'user%s' % i})
        for i in range(5):
            d = Dataset()
            d.save()
        combinations = itertools.combinations(Dataset.objects.all(), 2)
        for source_dataset, target_dataset in combinations:
            for i in range(3):
                similarity = Similarity(source_dataset=source_dataset, target_dataset=target_dataset, similarity=None)
                similarity.save()
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
                sim_id = request.context['sim_id']
                try:
                    user_rating = user.userprofile.rated_datasets.get(source_dataset=source_dataset, target_dataset=target_dataset)
                except:
                    user_rating = None
                similarity_value = OPTIONS[randint(0,2)]
                c.post('/survey', {'source_dataset_id': source_dataset.id, 'target_dataset_id': target_dataset.id, 'similarity': similarity_value, 'sim_id': sim_id})

    def test_kappa(self):
        kappa_value = kappa.kappa([])
        print kappa_value
        self.assertTrue(-1 <= kappa_value <= 1)