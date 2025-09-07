from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import Log, Tag
from django.http import JsonResponse

# Create your views here.


def index(request):
    return render(request, 'webui/index.html', {'username': request.user.username})


def new_login(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'status': 'success', 'message': f'Welcome Comrade {username}'}, status=200)
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid username or password'}, status=401)
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid username or password'}, status=400)
    
    return render(request, 'webui/login.html')

def new_logout(request):
    logout(request)
    messages.success(request, "Logged out")
    return redirect('login')