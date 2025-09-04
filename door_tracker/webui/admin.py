from django.contrib import admin
from django.contrib.admin.views.main import ChangeList

from .models import Log, Membership, Tag, Person, SubTeam, Job


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
    list_display = ('name', 'owner', 'binary_id')


@admin.register(Person, SubTeam)
class NamedAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('name', 'quota')
