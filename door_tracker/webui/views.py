import json
import time

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Avg, Sum
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie

# Import Custom Files
from . import utils  # -> Helper functions
from .forms import RegistrationForm

# Create your views here.
from .models import Log, Statistics, Tag


def index(request):
    # Greetings from the Ancient One
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'webui/index.html', {'username': request.user.username})


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
            'user_id': log.tag.owner_id if (log.tag and log.tag.owner_id) else None,
        }
        for log in logs
    ]

    return JsonResponse({'status': 'success', 'logs': data}, status=200)


def minutes_today(request):
    today = timezone.localdate()  # gets the current date in the current timezone
    now = timezone.localtime()
    minutes_worked = 0

    logs = (
        Log.objects.filter(
            tag__owner=request.user,
            time__date=today,  # filter only logs that happened today
        )
        .select_related('tag')
        .order_by('time')
    )

    checkin_time = None
    first_log = True

    for log in logs:
        if log.type == Log.LogEntryType.CHECKIN:
            checkin_time = log.time
            first_log = False
        elif log.type == Log.LogEntryType.CHECKOUT:
            if checkin_time and not first_log:
                delta = timezone.localtime(log.time) - timezone.localtime(checkin_time)
                minutes_worked += int(delta.total_seconds() // 60)
                checkin_time = None
            elif first_log:
                # First log is a checkout with no prior checkin today
                midnight = timezone.make_aware(
                    timezone.datetime.combine(
                        timezone.localdate(log.time),
                        timezone.datetime.min.time(),
                    )
                )
                delta = timezone.localtime(log.time) - midnight
                minutes_worked += int(delta.total_seconds() // 60)
                first_log = False

    # If the last log was a checkin and no checkout yet, count time until now
    if checkin_time:
        delta = now - timezone.localtime(checkin_time)
        minutes_worked += int(delta.total_seconds() // 60)

    return minutes_worked


def minutes_week(request):
    today = timezone.localdate()
    start_of_week = today - timezone.timedelta(days=today.weekday())  # Monday

    total_week = (
        Statistics.objects.filter(
            person=request.user,
            date__date__gte=start_of_week,
            date__date__lte=today,
        ).aggregate(total=Sum('minutes_day'))['total']
        or 0
    )

    return total_week


def minutes_month(request):
    today = timezone.localdate()
    start_of_month = today.replace(day=1)

    total_month = (
        Statistics.objects.filter(
            person=request.user,
            date__date__gte=start_of_month,
            date__date__lte=today,
        ).aggregate(total=Sum('minutes_day'))['total']
        or 0
    )

    return total_month


def save_statistics(request):
    # Get current time in the active timezone
    now = timezone.localtime()

    # Get today's date (without time) to filter existing statistics
    today_date = now.date()

    minutes_today_val = minutes_today(request)

    stats, created = Statistics.objects.update_or_create(
        person=request.user,
        date__date=today_date,  # filter by date portion only
        defaults={
            'minutes_day': minutes_today_val,
            'date': now,
        },
    )

    minutes_week_val = minutes_week(request)
    minutes_month_val = minutes_month(request)

    # Update only the week/month fields
    stats.minutes_week = minutes_week_val
    stats.minutes_month = minutes_month_val

    # Calculate avg and total
    agg = Statistics.objects.filter(person=request.user).aggregate(
        average_week=Avg('minutes_week'),
        total_minutes=Sum('minutes_day'),
    )

    average_week = agg['average_week'] or 0
    total_minutes = agg['total_minutes'] or 0

    stats.average_week = average_week
    stats.total_minutes = total_minutes

    stats.save(
        update_fields=['minutes_week', 'minutes_month', 'average_week', 'total_minutes']
    )

    return JsonResponse(
        {
            'minutes_day': minutes_today_val,
            'minutes_week': minutes_week_val,
            'minutes_month': minutes_month_val,
            'average_minutes': average_week,
            'total_minutes': total_minutes,
            'date': stats.date,
            'created': created,
        },
        status=200,
    )


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
        tag = Tag.objects.select_related('owner').filter(id=int(raw_card_str)).first()

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
                tag = Tag.objects.select_related('owner').filter(tag=tag_bytes).first()
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


def sign_up(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # replace with your login URL
    else:
        form = RegistrationForm()
    return render(request, 'webui/sign_up.html', {'form': form})
