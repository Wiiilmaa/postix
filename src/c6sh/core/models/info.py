from django.db import models


class Info(models.Model):
    content = models.CharField(max_length=2500)
    name = models.CharField(max_length=40, null=True, blank=True)
    is_printable = models.BooleanField(default=True)
