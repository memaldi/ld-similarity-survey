from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Dataset(models.Model):
    title = models.CharField(max_length=20)
    description = models.CharField(max_length=1000)
    datahub_url = models.CharField(max_length=20)
    example_resource = models.CharField(max_length=100)
    similarity = models.ManyToManyField("self", through='Similarity', symmetrical=False)

class Similarity(models.Model):
    source_dataset = models.ForeignKey(Dataset, related_name='source_dataset')
    target_dataset = models.ForeignKey(Dataset, related_name='target_dataset')
    choices = (
        ('yes', 'Yes'),
        ('no', 'NO'),
        ('undefined', 'Undefined'),
        )
    similarity = models.CharField(max_length=10, choices=choices, default='undefined')

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    rated_datasets = models.ManyToManyField(Similarity)