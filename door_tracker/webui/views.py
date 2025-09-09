from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
import json
import time
from django.views.decorators.csrf import ensure_csrf_cookie


# Import Custom Files
from . import utils  # -> Helper functions

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

@ensure_csrf_cookie
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


@utils.require_authentication
def check_status(request):
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
            'state': last_log.type,
            'state_display': last_log.get_type_display(),
            'date': last_log.time.isoformat(),
        },
        status=200,
    )


@utils.require_authentication
def change_status(request):
    # at this point, request.user is guaranteed authenticated
    try:
        data = json.loads(request.body)
        tag_id = data['tag_id']
    except (json.JSONDecodeError, KeyError):
        return JsonResponse(
            {'status': 'error', 'message': 'Invalid JSON payload.'},
            status=400,
        )

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

    last_log = Log.objects.filter(tag=tag_scanned).order_by('-time').first()
    new_type = (
        Log.LogEntryType.CHECKIN
        if not last_log or last_log.type == Log.LogEntryType.CHECKOUT
        else Log.LogEntryType.CHECKOUT
    )

    log = Log.objects.create(type=new_type, tag=tag_scanned)

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


def register_scan(request):
    try:
        body = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse(
            {'status': 'error', 'message': 'Invalid JSON payload'}, status=400
        )

    raw_card = body.get('cardID')
    # device_id = body.get('deviceID')  # not used yet

    if raw_card is None or str(raw_card).strip() == '':
        return JsonResponse(
            {'status': 'error', 'message': 'cardID is required'}, status=400
        )

    # Always treat it as string for normalization steps
    raw_card_str = str(raw_card).strip()
    tag = None

    # 1) Try as integer primary key
    if raw_card_str.isdigit():
        tag = (
            Tag.objects.select_related('owner')
            .filter(id=int(raw_card_str))
            .first()
        )

    # 2) Try as name (case-insensitive), including a normalized version (strip colons/spaces)
    if tag is None:
        normalized_name = ''.join(ch for ch in raw_card_str if ch.isalnum())
        tag = (
            Tag.objects.select_related('owner')
            .filter(name__iexact=raw_card_str)
            .first()
            or Tag.objects.select_related('owner')
            .filter(name__iexact=normalized_name)
            .first()
        )

    # 3) Try as hex-encoded UID for BinaryField `tag`
    if tag is None:
        try:
            # Keep only hex chars, ignore separators like ":" or spaces
            hex_str = ''.join(
                ch for ch in raw_card_str if ch in '0123456789abcdefABCDEF'
            )
            if hex_str:
                tag_bytes = bytes.fromhex(hex_str)
                tag = (
                    Tag.objects.select_related('owner')
                    .filter(tag=tag_bytes)
                    .first()
                )
        except ValueError:
            # Not valid hex — ignore
            pass

    if tag is None:
        return JsonResponse(
            {'status': 'error', 'message': 'Card not registered'}, status=404
        )

    if not tag.owner:
        return JsonResponse(
            {'status': 'error', 'message': 'Card has no owner'}, status=404
        )

    user = tag.owner

    # Build response matching your OpenAPI schema (hours left None for now)
    data = {
        'name': user.first_name or '',
        'last-name': user.last_name or '',
        'user-name': user.username,
        'state': 'register',  # you can later switch to checkin/checkout
        'time': int(time.time()),  # epoch time
        'dailyhours': None,
        'weeklyhours': None,
        'tag_id': tag.id,
    }

    return JsonResponse(data, status=200)
