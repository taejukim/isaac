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
        return self.service_no
    

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
        return self.sevice_no
    