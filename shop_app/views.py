from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate, logout

def home(request):
    categories = Category.objects.all()
    return render(request, 'home.html', {'categories': categories})
