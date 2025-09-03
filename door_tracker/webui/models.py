from django.db import models

class SubTeam(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name

class Person(models.Model):
    name = models.TextField()
    subteam_id = models.ManyToManyRel(SubTeam)

    def __str__(self):
        return self.name

class TagPerson(models.Model):
    person_id = models.ForeignKey(Person, on_delete=models.CASCADE)

class Log(models.Model):
    type = models.TextField()
    tag_id = models.ForeignKey(TagPerson, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)


