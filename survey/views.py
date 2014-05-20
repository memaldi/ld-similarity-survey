import redis
from django.shortcuts import render
from survey.forms import SurveyForm, UserForm
from survey.models import Dataset, Similarity
from django.contrib.auth.models import User
from random import randint
from django.db.utils import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
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
    if request.user.is_authenticated():
        return HttpResponseRedirect('/survey')
    else:
        errors = {}
        registered =  False
        if request.POST:
            username = request.POST['user']
            password = request.POST['password']
            repeat_password = request.POST['password-repeat']
            user_form = UserForm(data={'username': username})
            if len(password) <= 0:
                errors['empty_password'] = 'This field is required!'
            elif password != repeat_password:
                errors['different_passwords'] = 'Passwords do not match!'
            else:
                try:
                    user = User()
                    user.username = username
                    user.set_password(password)
                    user.save()
                    user = authenticate(username=username,password=password)
                    registered = True
                    login(request, user)
                except IntegrityError:
                    errors['user_error'] = 'User already exists!'
        else:
            user_form = UserForm()
        return render(request, 'survey/register.html', {'user_form': user_form, 'errors': errors, 'registered': registered})

def user_login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/survey')
    else:
        errors = {}
        username = None
        if request.POST:
            username = request.POST['user']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect('/survey')
            else:
                errors['bad_login'] = 'Invalid user or password!'
        return render(request, 'survey/login.html', {'errors': errors, 'username': username})

def user_logout(request):
    logout(request)
    return render(request, 'survey/thanks.html')