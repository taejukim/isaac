from django.db import models

class ServiceInfo(models.Model):
    id = models.AutoField(primary_key=True)
    service_no = models.IntegerField(unique=True, verbose_name='서비스 이름')
    sort = models.IntegerField(verbose_name='정렬을 위한 no')
    category = models.CharField(max_length=50, blank=True, null=True, verbose_name='분류')
    name_detail = models.CharField(max_length=50, blank=True, null=True, verbose_name='서비스 상세')
    priority = models.CharField(max_length=3, blank=True, null=True, verbose_name='서비스 우선순위')
    group = models.CharField(max_length=20, blank=True, null=True, verbose_name='M매뉴얼')
    release_yn = models.CharField(max_length=5, blank=True, null=True, verbose_name='출시여부')
    d_type = models.CharField(max_length=10, blank=True, null=True)
    standard_mm = models.FloatField(verbose_name='기준리소스')
    standard_mm_dpl = models.FloatField(verbose_name='배포기준고려')
    note_service = models.CharField(max_length=200, blank=True, null=True)
    part = models.CharField(max_length=10, blank=True, null=True)
    team_member = models.CharField(max_length=30, blank=True, null=True)
    dpl_cycle = models.CharField(max_length=10, blank=True, null=True)
    create_dt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.service_no)
    

class Resource(models.Model):
    id = models.AutoField(primary_key=True)
    service_no = models.ForeignKey(ServiceInfo, to_field='service_no', on_delete=models.CASCADE)
    mm = models.FloatField()
    month = models.IntegerField(null=False)
    year = models.IntegerField()
    category = models.CharField(max_length=50, blank=True, null=True, verbose_name='서비스명')
    name_detail = models.CharField(max_length=50, blank=True, null=True, verbose_name='서비스명 상세')
    group = models.CharField(max_length=10, blank=True, null=True, verbose_name='M매뉴얼 자동화 공공')
    md = models.BigIntegerField()
    translation = models.FloatField(verbose_name='추이')
    note_resource = models.CharField(max_length=200, blank=True, null=True)
    part = models.CharField(max_length=10, blank=True, null=True)
    team_member = models.CharField(max_length=10, blank=True, null=True)
    create_dt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.service_no)
    

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=100, null=False, blank=False, verbose_name='카테고리 이름')

    def __str__(self):
        return self.category

class Service(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, verbose_name="카테고리", on_delete=models.CASCADE)
    service = models.CharField(max_length=100, null=False, blank=False, verbose_name='서비스 이름')
    priority = models.CharField(max_length=10, null=False, blank=False, verbose_name='우선순위')
    man_month = models.FloatField(verbose_name='Man Month')
    description = models.TextField(null=True, blank=True, verbose_name='비고')
    ordering = models.IntegerField(verbose_name='정렬 순서')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.service

    class Meta:
        ordering = ['ordering']

class Member(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=10, null=False, blank=False, verbose_name='이름')
    team = models.CharField(max_length=50, null=False, blank=False, verbose_name='부서명')
    email = models.EmailField(max_length=254, null=False, blank=False, verbose_name='이메일')
    title = models.CharField(max_length=10, null=False, blank=False, verbose_name='직함')
    position = models.CharField(max_length=10, null=False, blank=False, verbose_name='직책')
    services = models.ManyToManyField(Service, blank=True,
     related_name='services', verbose_name='담당 서비스')
    description = models.TextField(null=True, blank=True, verbose_name='비고')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class WorkHistory(models.Model):

    WORK_TYPE_CHOICES = (
        ('alpha','Alpha Test'),
        ('beta','Beta Test'),
        ('real','Real Test'),
        ('auto','자동화 유지보수'),
        ('meeting', '회의'),
    )

    TEST_TYPE_CHOICES = (
        ('normal', '정기배포'),
        ('normal2', '2주차배포'),
        ('hotfix', 'Hot fix'), 
    )
    
    id = models.AutoField(primary_key=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    start_date = models.DateField(verbose_name='시작 날짜')
    end_datet = models.DateField(verbose_name='종료 날짜')
    work_type = models.CharField(max_length=20, null=False, blank=False,
         choices=WORK_TYPE_CHOICES, verbose_name='업무 종류')
    test_type = models.CharField(max_length=20, null=False, blank=False,
         choices=TEST_TYPE_CHOICES, verbose_name='업무 종류')
    man_days = models.FloatField(verbose_name='투입 공수(Man Day)')
    description = models.TextField(verbose_name='비고')

    def __str__(self):
        return '{}_{}'.format(self.service, self.work_type)
