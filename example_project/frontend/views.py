from django.conf import settings
from django.shortcuts import render


def index(request):
    context = {"username": settings.USERNAME, "password": settings.PASSWORD}
    return render(request, "index.html", context)
