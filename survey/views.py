import redis
from django.shortcuts import render
from survey.forms import SurveyForm, UserForm
from survey.models import Dataset, Similarity
from django.contrib.auth.models import User
from random import randint
from django.db.utils import IntegrityError
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
            similarity = Similarity.objects.filter(source_dataset=source_dataset, target_dataset=target_dataset)
            if len(similarity) < 3:
                similarity = Similarity.objects.create(source_dataset=source_dataset, target_dataset=target_dataset, similarity=similarity_str)
                similarity.save()
                r = redis.StrictRedis(host='localhost', port=6379, db=0)
                id_list = eval(r.get('ld-survey:id_list'))
                id_list.remove((source_dataset.id, target_dataset.id))
                r.set('ld-survey:id_list', str(id_list))
            return render(request, 'survey/thanks.html')

    else:
        id_list = []
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        if r.exists('ld-survey:id_list'):
            id_list = eval(r.get('ld-survey:id_list'))
        else:
            for source_dataset in Dataset.objects.all():
                for target_dataset in Dataset.objects.all():
                    if source_dataset.id != target_dataset.id and (source_dataset.id, target_dataset.id) not in id_list:
                        similarity = Similarity.objects.filter(source_dataset=source_dataset, target_dataset=target_dataset)
                        if len(similarity) < 3:
                            id_list.append((source_dataset.id, target_dataset.id))
            r.set('ld-survey:id_list', str(id_list))
        random_id = randint(0, len(id_list) - 1)
        source_id = id_list[random_id][0]
        target_id = id_list[random_id][1]
        source_dataset = Dataset.objects.get(id=source_id)
        target_dataset = Dataset.objects.get(id=target_id)

        form = SurveyForm(initial={'similarity': 'undefined'})

        return render(request, 'survey/survey.html', {'form': form, 'source_dataset': source_dataset, 'target_dataset': target_dataset})

def about(request):
    return render(request, 'survey/about.html')

def register(request):
    errors = {}
    if request.POST:
        username = request.POST['user']
        password = request.POST['password']
        try:
            user = User()
            user.username = username
            user.password = password
            user.save()
        except IntegrityError:
            user_form = UserForm(data={'username': username, 'username_error': 'Username already exists!'})
            errors['user_error'] = 'User already exists!'
        except Exception as e:
            print e
    else:
        user_form = UserForm()
    return render(request, 'survey/register.html', {'user_form': user_form, 'errors': errors})