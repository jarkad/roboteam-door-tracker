from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse

# Create your views here.
from .models import Log

def index(request):
    if not request.user.is_authenticated:
        return redirect('login')
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
                return JsonResponse(
                    {'status': 'success', 'message': f'Welcome Comrade {username}'},
                    status=200,
                )
            else:
                return JsonResponse(
                    {'status': 'error', 'message': 'Invalid username or password'},
                    status=401,
                )
        else:
            return JsonResponse(
                {'status': 'error', 'message': 'Invalid username or password'},
                status=400,
            )

    return render(request, 'webui/login.html')


def new_logout(request):
    logout(request)
    messages.success(request, 'Logged out')
    return redirect('login')


def current_user_data(request):
    if not request.user.is_authenticated:
        return JsonResponse(
                    {'status': 'error', 'message': 'Error. Log in to view data.'},
                    status=400,
                )
    
    logs = Log.objects.filter(tag__owner=request.user).select_related("tag").order_by("-time")

    data = []
    for log in logs:
        data.append({
            "id": log.id,
            "type": log.get_type_display(),
            "time": log.time.isoformat(),
            "tag": str(log.tag),
            "user_id": log.tag.owner.id,
        })

    return JsonResponse({"status": "success", "logs": data}, status=200)
    
