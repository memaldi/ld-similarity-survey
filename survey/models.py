from django.db import models

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
    similarity = models.BooleanField()