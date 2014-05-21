from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ld_similarity_survey.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'survey.views.survey'),
    url(r'^survey', 'survey.views.survey'),
    url(r'^about', 'survey.views.about'),
    url(r'^register', 'survey.views.register'),
    url(r'^login', 'survey.views.user_login'),
    url(r'^logout', 'survey.views.user_logout'),
    url(r'^ranking', 'survey.views.ranking'),
)
