from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.shortcuts import render


def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')

def start_page(request):
    return render(request, 'home.html')

def euro2020(request):
    return render(request, 'euro2020.html')

def world2018(request):
    return render(request, 'world2018.html')

def euro2016(request):
    return render(request, 'euro2016.html')
