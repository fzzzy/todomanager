from django.db import models


class Todo(models.Model):
    title = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")
    state = models.BooleanField(default=False)

