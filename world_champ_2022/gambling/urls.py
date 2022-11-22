from django.urls import re_path

from . import views

app_name = 'gambling'

urlpatterns = [
    re_path(r'^gambling/$', views.gambling_list, name='list'),
    re_path(r'^results/$', views.results, name='results'),
    re_path(r'^results_JSON/$', views.results_JSON, name='results_JSON'),
    re_path(r'^news/$', views.news, name='news'),
    re_path(r'^stats/$', views.stats, name='stats'),
    re_path(r'^stats_JSON/$', views.stats_JSON, name='stats_JSON'),
    re_path(r'^tournament/$', views.tournament, name='tournament'),
]
