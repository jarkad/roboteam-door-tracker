from django.contrib import admin

from .models import Log, Membership, Tag, SubTeam, Job


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('time', 'type', 'person')
    ordering = ('time',)


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
    return self._build_app_dict(request, app_label).values()


admin.AdminSite.get_app_list = get_app_list
