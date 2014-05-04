from survey.models import Dataset
import requests

DATAHUB_API_URL = 'http://datahub.io/api/3'

def get_id(url):
    return url.replace('http://datahub.io/dataset/', '').replace('\n', '')

with open('survey_datasets.csv') as f:
    for line in f:
        sline = line.split(',')
        url = sline[1]
        params = {'id': get_id(url)}
        r = requests.get('%s/action/package_show' % DATAHUB_API_URL, params=params)
        json_data = r.json()
        title = ''
        description = ''
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
        dataset = Dataset()
        dataset.title = title
        dataset.description = description
        dataset.datahub_url = url
        dataset.example_resource = example_resource
        dataset.save()