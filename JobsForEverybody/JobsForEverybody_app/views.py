from django.shortcuts import render, HttpResponse


def index(request):
    return HttpResponse('index')


def login(request):
    return HttpResponse('login')


def logout(request):
    return HttpResponse('logout')


def registration(request):
    return HttpResponse('registration')


def settings(request):
    return HttpResponse('settings')


def delete_vacancy(request, vac_id):
    return HttpResponse(f'delete_vacancy id = {vac_id}')
