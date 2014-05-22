import itertools
from django.shortcuts import render
from survey.forms import SurveyForm, UserForm
from survey.models import Dataset, Similarity, UserProfile
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
# Create your views here.

@login_required
def survey(request):
    user = request.user

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
                user.userprofile.points = user.userprofile.points + 1;
                user.userprofile.rated_datasets.add(similarity)
                user.userprofile.save()

    selected_source_dataset = None
    selected_target_dataset = None

    combinations = itertools.combinations(Dataset.objects.all(), 2)

    for source_dataset, target_dataset in combinations:
        similarity = Similarity.objects.filter(source_dataset=source_dataset, target_dataset=target_dataset)
        if len(similarity) < 3:
            try:
                user_rating = user.userprofile.rated_datasets.get(source_dataset=source_dataset, target_dataset=target_dataset)
            except:
                user_rating = None
            if user_rating == None:
                selected_source_dataset = source_dataset
                selected_target_dataset = target_dataset
                break

    form = SurveyForm(initial={'similarity': 'undefined'})

    top_users = UserProfile.objects.filter(points__gt=0).order_by('-points')[:5]

    return render(request, 'survey/survey.html', {'form': form, 'source_dataset': selected_source_dataset, 'target_dataset': selected_target_dataset, 'top_users': top_users})

def about(request):
    return render(request, 'survey/about.html')

def register(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('survey.views.survey'))
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
                    user_profile = UserProfile()
                    user_profile.user = user
                    user_profile.points = 0
                    user_profile.save()
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
        return HttpResponseRedirect(reverse('survey.views.survey'))
    else:
        errors = {}
        username = None
        if request.POST:
            username = request.POST['user']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect(reverse('survey.views.survey'))
            else:
                errors['bad_login'] = 'Invalid user or password!'
        return render(request, 'survey/login.html', {'errors': errors, 'username': username})

def user_logout(request):
    logout(request)
    return render(request, 'survey/thanks.html')

def ranking(request):

    user_profiles = UserProfile.objects.filter(points__gt=0).order_by('-points')

    return render(request, 'survey/ranking.html', {'user_profiles': user_profiles})