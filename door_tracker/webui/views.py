from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
import json

# Create your views here.
from .models import Log
from .models import Tag


def index(request):
    # Greetings from the Ancient One
    if not request.user.is_authenticated:
        return redirect('login')
    return render(
        request, 'webui/index.html', {'username': request.user.username}
    )


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
                    {
                        'status': 'success',
                        'message': f'Welcome Comrade {username}',
                    },
                    status=200,
                )
            else:
                return JsonResponse(
                    {
                        'status': 'error',
                        'message': 'Invalid username or password',
                    },
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
            {'status': 'error', 'message': 'Log in to view data.'},
            status=400,
        )

    last_log = (
        Log.objects.filter(tag__owner=request.user)
        .select_related('tag')
        .order_by('-time')
        .first()
    )

    if not last_log:
        # No logs yet for this user
        return JsonResponse(
            {
                'status': 'success',
                'state': None,
                'state_display': None,
                'date': None,
            },
            status=200,
        )

    return JsonResponse(
        {
            'status': 'success',
            'state': last_log.type,  # raw enum value: "IN" / "OUT" / "WTF"
            'state_display': last_log.get_type_display(),  # human label
            'date': last_log.time.isoformat(),
        },
        status=200,
    )


def change_status(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {'status': 'error', 'message': 'Log in to change status.'},
            status=400,
        )

    # Parse JSON body
    try:
        data = json.loads(request.body)
        tag_id = data['tag_id']
    except (json.JSONDecodeError, KeyError):
        return JsonResponse(
            {'status': 'error', 'message': 'Invalid JSON payload.'},
            status=400,
        )

    # Resolve tag and ensure it belongs to the current user
    tag_scanned = (
        Tag.objects.select_related('owner')
        .filter(id=tag_id, owner=request.user)
        .first()
    )
    if not tag_scanned:
        return JsonResponse(
            {'status': 'error', 'message': 'Tag not found or not yours.'},
            status=404,
        )

    # Determine next state from the last log for this tag
    last_log = Log.objects.filter(tag=tag_scanned).order_by('-time').first()
    if not last_log or last_log.type == Log.LogEntryType.CHECKOUT:
        new_type = Log.LogEntryType.CHECKIN
    else:
        new_type = Log.LogEntryType.CHECKOUT

    # Create new log (time is set via auto_now_add)
    log = Log.objects.create(
        type=new_type,
        tag=tag_scanned,  # correct field name (lowercase)
    )

    return JsonResponse(
        {
            'status': 'success',
            'state': log.type,
            'state_display': log.get_type_display(),
            'date': log.time.isoformat(),
            'tag': str(tag_scanned),
        },
        status=201,
    )


def current_user_data(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {'status': 'error', 'message': 'Log in to view data.'},
            status=400,
        )

    logs = (
        Log.objects.filter(tag__owner=request.user)
        .select_related('tag')
        .order_by('-time')
    )

    data = [
        {
            'id': log.id,
            'type': log.get_type_display(),
            'time': log.time.isoformat(),
            'tag': str(log.tag),
            'user_id': log.tag.owner_id
            if (log.tag and log.tag.owner_id)
            else None,
        }
        for log in logs
    ]

    return JsonResponse({'status': 'success', 'logs': data}, status=200)
