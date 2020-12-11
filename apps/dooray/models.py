from django.db import models

# Create your models here.
class UserList(models.Model):
    name = models.CharField(max_length=50)
    member_id = models.CharField(max_length=50)
    email = models.CharField(max_length=50)

    def __str__(self):
        self.name

    class Meta:
        managed = True
        verbose_name = 'UserList'
        verbose_name_plural = 'UserLists'
