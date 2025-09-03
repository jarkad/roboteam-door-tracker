from django.contrib import admin
from django.contrib.admin.views.main import ChangeList

from .models import Log, Membership, Tag, Person, SubTeam, Job


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'type', 'person')


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('starting_from', 'person', 'subteam', 'job')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'binary_id')


@admin.register(Person, SubTeam)
class NamedAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('name', 'quota')
