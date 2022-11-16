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
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings

from . import views

from django.contrib.auth import views as auth_views
from django.views.static import serve

urlpatterns = [
    re_path(r'^gambling/', include('gambling.urls', namespace='gambling')),
    re_path(r'^logout/$', views.logout_page),
    re_path(r'^accounts/login/$', views.login_redirect),
    re_path(r'^results/$', views.results, name='results'),
    re_path(r'^updates/$', views.updates, name='updates'),
    re_path(r'^news/$', views.news, name='news'),
    re_path(r'^stats/$', views.stats, name='stats'),
    re_path(r'^tournament/$', views.tournament, name='tournament'),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    #re_path(r'^password-reset/$', auth_views.password_reset, name='password_reset'),
    #re_path(r'^password-reset/done/$', auth_views.password_reset_done,
    #    name='password_reset_done'),
    #re_path(r'^password-reset/confirm/(?P<uidb64>[-\w]+)/(?P<token>[-\w]+)/$',
    #    auth_views.password_reset_confirm, name='password_reset_confirm'),
    #re_path(r'^password-reset/complete/$', auth_views.password_reset_complete ,name='password_reset_complete'),
    re_path(r'^$', views.start_page, name='home'),
#    re_path(r'^accounts/', include('allauth.urls')),
    re_path(r'^', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
]
