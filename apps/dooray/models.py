from django.db import models

# Create your models here.
class UserList(models.Model):
    name = models.CharField(max_length=50)
    member_id = models.CharField(max_length=50)
    email = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        verbose_name = 'UserList'
        verbose_name_plural = 'UserLists'

class TargetProject(models.Model):

    TARGET_TIME_CHIOCES = [
        ('createdAt', 'createdAt'),
        ('updatedAt', 'updatedAt'),
    ]

    MEMBER_KEY_CHOICES = [
        ('toMemberIds', 'toMemberIds'),
        ('fromMemberIds', 'fromMemberIds'),
    ]

    project_id = models.CharField(max_length=100)
    project_name = models.CharField(max_length=50)
    target_time = models.CharField(max_length=50, choices=TARGET_TIME_CHIOCES)
    member_key = models.CharField(max_length=50, choices=MEMBER_KEY_CHOICES)

    def __str__(self):
        return self.project_name

    class Meta:
        managed = True
        verbose_name = 'TargetProject'
        verbose_name_plural = 'TargetProject'

class Tags(models.Model):

    project = models.ForeignKey(TargetProject, on_delete=models.CASCADE)
    tag_id = models.CharField(max_length=100)
    tag_name = models.CharField(max_length=100)
    tag_type = models.CharField(max_length=100, blank=True, null=True)
    tag_class = models.CharField(max_length=100, blank=True, null=True)
    esm_name = models.CharField(max_length=100, blank=True, null=True)
    esm_code = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.tag_name

    class Meta:
        managed = True
        verbose_name = 'DoorayTags'
        verbose_name_plural = 'DoorayTags'

# class GRMHistory(models.Model):

class Issues(models.Model):
    project_id = models.CharField(max_length=100)#
    projct_name = models.CharField(max_length=100)#
    post_id = models.CharField(max_length=100)#
    subject = models.TextField()#
    post_number = models.IntegerField()#
    url = models.URLField() #
    tags = models.ManyToManyField(Tags)
    defect_type = models.CharField(max_length=255, blank=True, null=True)
    defect_cause = models.CharField(max_length=255, blank=True, null=True)
    nondetect_reason = models.CharField(max_length=255, blank=True, null=True)
    detail = models.CharField(max_length=255, blank=True, null=True)
    grade = models.CharField(max_length=100, blank=True, null=True)
    environment = models.CharField(max_length=100, blank=True, null=True)
    owner = models.CharField(max_length=100, blank=True, null=True)
    remarks = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.task_id

    class Meta:
        managed = True
        verbose_name = 'Issues'
        verbose_name_plural = 'Issues'
