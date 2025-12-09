from django.db import models

# Create your models here.
class Profiles(models.Model):
    user_name = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.user_name