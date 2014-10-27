from survey.models import Dataset, Similarity
import requests

DATAHUB_API_URL = 'http://datahub.io/api/3'

def get_id(url):
    return url.replace('http://datahub.io/dataset/', '').replace('\n', '')

with open('survey_datasets.csv') as f:
    for line in f:
        sline = line.split(',')
        if sline[4] not in ['', '*'] and sline[1] != '':
            url = sline[1]
            params = {'id': get_id(url)}
            r = requests.get('%s/action/package_show' % DATAHUB_API_URL, params=params)
            json_data = r.json()
            title = ''
            description = ''
            if 'result' in json_data:
                if 'title' in json_data['result']:
                    if json_data['result']['title'] != None:
                        title = json_data['result']['title']
                if 'notes' in json_data['result']:
                    if json_data['result']['notes'] != None:
                        description = json_data['result']['notes']
                example_resource = ''
                for resource in json_data['result']['resources']:
                    if resource['format'] == 'example/rdf+xml':
                        if resource['url'] != None:
                            example_resource = resource['url']
                print 'Saving %s...' % title
                nick = sline[4]
                dataset = Dataset()
                dataset.title = title
                dataset.description = description
                dataset.datahub_url = url
                dataset.example_resource = example_resource
                dataset.nick = nick
                dataset.save()
            else:
                print json_data

with open('relations.csv') as f:
    for line in f:
        sline = line.split(';')
        source_dataset = Dataset.objects.get(nick=sline[0])
        target_dataset = Dataset.objects.get(nick=sline[1])
        similarity_source = Similarity.objects.filter(source_dataset=source_dataset, target_dataset=target_dataset)
        similarity_target = Similarity.objects.filter(source_dataset=target_dataset, target_dataset=source_dataset)
        if len(similarity_target) <= 0:
            for i in range(3 - len(similarity_source)):
                similarity = Similarity()
                similarity.source_dataset = source_dataset
                similarity.target_dataset = target_dataset
                similarity.similarity = None
                similarity.save()
        else:
            for i in range(3 - len(similarity_target)):
                similarity = Similarity()
                similarity.source_dataset = source_dataset
                similarity.target_dataset = target_dataset
                similarity.similarity = None
                similarity.save()