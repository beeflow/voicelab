import uuid

from django.db import models


class WaveFile(models.Model):
    class Status(models.IntegerChoices):
        """Queue processing statuses."""

        IN_QUEUE = 1
        IN_PROGRESS = 5
        DONE = 10

    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    filename = models.CharField(max_length=250, null=True, blank=True)
    channels = models.IntegerField(null=True, blank=True)
    sampwidth = models.IntegerField(null=True, blank=True)
    framerate = models.IntegerField(null=True, blank=True)
    nframes = models.IntegerField(null=True, blank=True)
    audiogram = models.BinaryField(null=True, blank=True)
    status = models.IntegerField(choices=Status.choices, blank=False, null=False, default=Status.IN_QUEUE)

    def __str__(self):
        """Returns UUID"""
        return f'{self.id}'
