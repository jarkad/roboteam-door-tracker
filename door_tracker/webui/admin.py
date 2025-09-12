# admin.py
import secrets
from datetime import datetime, timedelta

from django.contrib import admin
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import path, reverse

from .models import Job, Log, Membership, Scanner, SubTeam, Tag

admin.site.site_header = 'RoboTeam'
TOKEN_LIFETIME = 24 * 360  # How long until the link expires


class LogSubteamListFilter(admin.SimpleListFilter):
    title = 'subteam'
    parameter_name = 'subteam'

    def lookups(self, request, model_admin):
        return [(s.id, s) for s in SubTeam.objects.all()]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        members = Membership.objects.filter_effective().filter(subteam=self.value())
        return queryset.filter(tag__owner__in=members.values('person'))


class LogPersonListFilter(admin.SimpleListFilter):
    title = 'person'
    parameter_name = 'person'

    def lookups(self, request, model_admin):
        return [(u.id, u.get_full_name()) for u in User.objects.all()]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(tag__owner=self.value())


def export_selected_logs(modeladmin, request, queryset):
    ids = queryset.values_list('pk', flat=True)
    url = reverse('export', query={'ids': ids})
    return HttpResponseRedirect(url)


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    actions = [export_selected_logs]
    list_display = ('time', 'type', 'person', 'scanner')
    list_filter = (LogSubteamListFilter, LogPersonListFilter)
    ordering = ('-time',)
    search_fields = ('tag__owner__username', 'type')


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('starting_from', 'person', 'subteam', 'job')
    ordering = ('-starting_from',)
    search_fields = ('person__username', 'subteam__name')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner_name', 'status', 'binary_id')


@admin.register(SubTeam)
class NamedAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('name', 'quota')


@admin.register(Scanner)
class ScannerAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')

    def get_readonly_fields(self, request, obj=None):
        default = super().get_readonly_fields(request, obj)
        if obj is not None:  # when editing
            default = list(default) + ['id']
        return default


# this ungodly hack disables alphabetical sorting of models
# https://forum.djangoproject.com/t/reordering-list-of-models-in-django-admin/5300/9


def get_app_list(self, request, app_label=None):
    return list(self._build_app_dict(request, app_label).values())


def generate_register_link(request):
    token = secrets.token_urlsafe(16)
    cache.set(f'register_token_{token}', True, timeout=TOKEN_LIFETIME)
    link = request.build_absolute_uri(reverse('sign_up', query={'token': token}))
    expires_at = (datetime.now() + timedelta(seconds=TOKEN_LIFETIME)).isoformat()
    return JsonResponse({'link': link, 'expires_at': expires_at})


# admin.py (at the bottom)
def get_urls(original_get_urls):
    def custom_get_urls(self):
        urls = original_get_urls(self)
        custom_urls = [
            path(
                'generate-register-link/',
                self.admin_view(generate_register_link),
                name='generate_register_link',
            ),
        ]
        return custom_urls + urls

    return custom_get_urls


admin.AdminSite.get_app_list = get_app_list

admin.AdminSite.get_urls = get_urls(admin.AdminSite.get_urls)
