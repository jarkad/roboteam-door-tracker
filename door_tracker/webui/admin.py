from django.contrib import admin

from .models import SubTeam, Person, TagPerson, Log

admin.site.register([SubTeam, Person, TagPerson, Log])
