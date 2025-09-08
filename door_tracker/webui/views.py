from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
import json
import datetime

# Create your views here.
from .models import Log
from .models import Tag

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

def check_status(request):
    if not request.user.is_authenticated:
        return JsonResponse(
                    {'status': 'error', 'message': 'Error. Log in to view data.'},
                    status=400,
                )
    last_log = Log.objects.filter(tag__owner=request.user).select_related("tag").order_by("-time").first()
    if not last_log:
        return JsonResponse(
            {'status': 'error', 'message': 'Error. Log not found.'},
             status=400,
        )
    return JsonResponse({'status': last_log.get_type_display(), 'date': last_log.time.isoformat()}, status=200)

    
def change_status (request):
    last_status = check_status(request)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                    {'status': 'error', 'message': 'Error. Invalid json data.'},
                    status=400,
                )
        
        tag_id = data["tag_id"]
        tag_scanned  = Tag.objects.filter(id = tag_id).first()
        owner = tag.owner
        new_status = Log.LogEntryType.CHECKOUT

        if (last_status.status==Log.LogEntryType.CHECKOUT):
            new_status = Log.LogEntryType.CHECKIN

        log = Log.objects.create(type=new_status, tag=tag_scanned, time=datetime.datetime.now().isoformat())
        log.save(force_insert=True)
    return


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
    
