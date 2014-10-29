from survey.models import Dataset, Similarity
import requests

DATAHUB_API_URL = 'http://datahub.io/api/3'

def get_id(url):
    return url.replace('http://datahub.io/dataset/', '').replace('\n', '')

with open('survey_datasets.csv') as f:
    for line in f:
        sline = line.split(',')
        if sline[4] not in ['', '*'] and sline[1] != '':
            try:
                dataset = Dataset.objects.get(datahub_url=sline[1])
                dataset.nick = sline[4]
                dataset.save()
            except Exception as e:
                print e
                print sline[1]

with open('relations.csv') as f:
    for line in f:
        sline = line.split(';')
        source_dataset = Dataset.objects.get(nick=sline[0])
        target_dataset = Dataset.objects.get(nick=sline[1])
        similarity_source = Similarity.objects.filter(source_dataset=source_dataset, target_dataset=target_dataset)
        similarity_target = Similarity.objects.filter(source_dataset=target_dataset, target_dataset=source_dataset)
        if len(similarity_target) <= 0:
            for i in range(3 - len(similarity_source)):
                print 'Creating similarity for %s - %s' % (source_dataset.nick, target_dataset.nick)
                similarity = Similarity()
                similarity.source_dataset = source_dataset
                similarity.target_dataset = target_dataset
                similarity.similarity = None
                similarity.save()
        else:
            for i in range(3 - len(similarity_target)):
                print 'Creating similarity for %s - %s' % (target_dataset.nick, source_dataset.nick)
                similarity = Similarity()
                similarity.source_dataset = source_dataset
                similarity.target_dataset = target_dataset
                similarity.similarity = None
                similarity.save()