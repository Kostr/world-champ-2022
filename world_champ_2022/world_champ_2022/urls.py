"""world_champ_2022 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve

from . import views

urlpatterns = [
    re_path(r'^', include('gambling.urls', namespace='gambling')),
    re_path(r'^logout/$', views.logout_page),
    re_path(r'^$', views.start_page, name='home'),
    re_path(r'^euro2020/$', views.euro2020, name='euro2020'),
    re_path(r'^accounts/', include('allauth.urls')),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
]
