from base64 import b64encode
from django.db import models
from django.utils import timezone


class Log(models.Model):
    class LogEntryType(models.TextChoices):
        CHECKIN = 'IN', 'Check-in'
        CHECKOUT = 'OUT', 'Check-out'
        UNKNOWN = 'WTF', 'Card not linked'

    type = models.CharField(max_length=3, choices=LogEntryType.choices)
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE, related_name='logs')
    time = models.DateTimeField(auto_now_add=True)

    def timestamp(self):
        return self.time.strftime('%c')

    def person(self):
        return f'{self.tag.owner} ({self.tag.name})'

    def __str__(self):
        return ' — '.join([self.timestamp(), self.type, self.person()])


class Membership(models.Model):
    person = models.ForeignKey(
        'Person', on_delete=models.CASCADE, related_name='memberships'
    )
    subteam = models.ForeignKey(
        'SubTeam',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='members',
    )
    job = models.ForeignKey('Job', blank=True, null=True, on_delete=models.CASCADE)
    starting_from = models.DateTimeField(default=timezone.now)


class Tag(models.Model):
    tag = models.BinaryField()
    name = models.CharField()
    owner = models.ForeignKey('Person', on_delete=models.CASCADE, related_name='tags')

    def binary_id(self):
        return b64encode(self.tag).decode()

    def __str__(self):
        return f'{self.name} ({self.owner})'


class Person(models.Model):
    name = models.CharField()

    def __str__(self):
        return self.name


class SubTeam(models.Model):
    name = models.CharField()

    def __str__(self):
        return self.name


class Job(models.Model):
    name = models.CharField()
    quota = models.IntegerField(verbose_name='Quota (hours per week)')

    def __str__(self):
        return f'{self.name} ({self.quota} hrs/week)'
