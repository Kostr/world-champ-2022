from django.urls import path, include, re_path

from . import views

app_name = 'gambling'

urlpatterns = [
	re_path(r'^$', views.gambling_list, name='list'),
]