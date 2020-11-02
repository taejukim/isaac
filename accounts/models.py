from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    kr_name = models.CharField(max_length=50)
    emp_no = models.CharField(max_length=50)
    department = models.CharField(max_length=100)
    title = models.CharField(max_length=50)
    position = models.CharField(max_length=50)
    dep_code = models.CharField(max_length=50)
    img_src = models.URLField(max_length=255)