from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    kr_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="이름")
    emp_no = models.CharField(max_length=50, blank=True, null=True, verbose_name="사번")
    department = models.CharField(max_length=100, blank=True, null=True, verbose_name="부서")
    title = models.CharField(max_length=50, blank=True, null=True, verbose_name="직함")
    position = models.CharField(max_length=50, blank=True, null=True, verbose_name="직책")
    dept_code = models.CharField(max_length=50, blank=True, null=True, verbose_name="부서 코드")
    img_src = models.URLField(max_length=255, blank=True, null=True, verbose_name="Profile 이미지")
    is_member = models.BooleanField(default=False, verbose_name="Isaac 회원")
