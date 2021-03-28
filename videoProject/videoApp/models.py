from django.db import models

class Video(models.Model):
    video = models.FileField(upload_to='videos/')

    def __str__(self):
        return self.video.name
