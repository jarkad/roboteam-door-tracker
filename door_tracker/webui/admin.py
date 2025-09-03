from django.contrib import admin

# Register your models here.
from .models import SubTeam, Person, TagPerson, Membership, Log

admin.site.register([SubTeam, Person, TagPerson, Membership, Log])


