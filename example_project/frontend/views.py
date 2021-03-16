from django.conf import settings
from django.shortcuts import render


def index(request):
    context = {
        "username": settings.USERNAME,
        "password": settings.PASSWORD,
        "aws_secret": settings.AWS_SECRET,
    }
    return render(request, "index.html", context)
