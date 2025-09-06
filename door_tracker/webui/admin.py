from django.contrib.auth.models import User
from django.contrib import admin

from .models import Log, Membership, Tag, SubTeam, Job


class LogSubteamListFilter(admin.SimpleListFilter):
    title = 'subteam'
    parameter_name = 'subteam'

    def lookups(self, request, model_admin):
        return [(s.id, s) for s in SubTeam.objects.all()]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        members = Membership.objects.filter_effective().filter(
            subteam=self.value()
        )
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


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('time', 'type', 'person')
    ordering = ('time',)
    list_filter = (LogSubteamListFilter, LogPersonListFilter)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('starting_from', 'person', 'subteam', 'job')
    ordering = ('starting_from',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner_name', 'binary_id')


@admin.register(SubTeam)
class NamedAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('name', 'quota')


# this ungodly hack disables alphabetical sorting of models
# https://forum.djangoproject.com/t/reordering-list-of-models-in-django-admin/5300/9


def get_app_list(self, request, app_label=None):
    return list(self._build_app_dict(request, app_label).values())


admin.AdminSite.get_app_list = get_app_list
