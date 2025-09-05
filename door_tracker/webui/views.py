from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.models import Permission, User
# Create your views here.

from .models import Log
from .models import Person


def index(request):
    return HttpResponse("Hello, world. You're at the WebUI index.")


def getPerson(request, name):
    person = Person.objects.get(
        name=name
    )  # returns a single Person, or raises DoesNotExist
    print(person)
    return HttpResponse(person)


def logs(request):
    latest_logs_list = Log.objects.order_by('-time')[:5]
    template = loader.get_template('webui/logs.html')
    context = {'latest_logs_list': latest_logs_list}
    return HttpResponse(template.render(context, request))

async def checkAuth(request):
    user = await request.auser()
    return HttpResponse(user.username)