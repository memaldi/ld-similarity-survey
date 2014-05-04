from django.shortcuts import render
from survey.forms import SurveyForm
from survey.models import Dataset, Similarity
from random import randint
# Create your views here.

def survey(request):
    if request.method == 'POST':
        form = SurveyForm(request.POST)
        if form.is_valid():
            source_id = form.cleaned_data['source_dataset_id']
            target_id = form.cleaned_data['target_dataset_id']
            similarity_str = form.cleaned_data['similarity']

            source_dataset = Dataset.objects.get(id=source_id)
            target_dataset = Dataset.objects.get(id=target_id)
            similarity = Similarity.objects.create(source_dataset=source_dataset, target_dataset=target_dataset, similarity=similarity_str)
            similarity.save()
            return render(request, 'survey/thanks.html')

    else:
        id_list = []
        for dataset in Dataset.objects.all():
            id_list.append(dataset.id)

        source_id = randint(0, len(id_list) - 1)
        found = False
        while not found:
            target_id = randint(0, len(id_list) - 1)
            if source_id != target_id:
                found = True

        source_dataset = Dataset.objects.get(id=source_id)
        target_dataset = Dataset.objects.get(id=target_id)
        form = SurveyForm(initial={'similarity': 'undefined'})

        return render(request, 'survey/survey.html', {'form': form, 'source_dataset': source_dataset, 'target_dataset': target_dataset})

def about(request):
    return render(request, 'survey/about.html')