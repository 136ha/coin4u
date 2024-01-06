# https://medium.com/@dorianszafranski17/create-a-news-platform-in-django-f7b66f69be95

from django.shortcuts import render, get_object_or_404
from .models import Editorial, CryptoAnalysis, PressRelease

def index(request):
    editorials = Editorial.objects.all()[:45]
    crypto_analyses = CryptoAnalysis.objects.all()
    press_releases = PressRelease.objects.all()[:4]  # Add this line
    context = {
        'editorials': editorials,
        'crypto_analyses': crypto_analyses,
        'press_releases': press_releases,  # Add this line
    }
    return render(request, 'newsapp/index.html', context)


def editorial(request, slug):
    editorial = get_object_or_404(Editorial, slug=slug)
    return render(request, 'newsapp/editorial.html', {'editorial': editorial})

def tutorials(request):
    tutorials = Editorial.objects.all()
    return render(request, 'newsapp/tutorials.html', {'tutorials': tutorials})

# views.py
def press_release(request, slug):
    press_release = get_object_or_404(PressRelease, slug=slug)
    return render(request, 'newsapp/press_release.html', {'press_release': press_release})