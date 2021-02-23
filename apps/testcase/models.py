from django.db import models

class Service(models.Model):
    service_id = models.CharField(max_length=30, blank=False, null=False)
    service_name = models.CharField(max_length=100, blank=False, null=False)
    service_order = models.IntegerField(null=True)
    
    def __str__(self):
        return self.service_name
    
    class Meta:
        db_table = 'testcase_service'
        managed = True
        verbose_name = 'Service'

class Module(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    module_id = models.CharField(max_length=30, blank=False, null=False)
    module_name = models.CharField(max_length=100, blank=False, null=False)
    module_order = models.IntegerField(null=True)
    
    def __str__(self):
        return self.module_name

    class Meta:
        db_table = 'testcase_module'
        managed = True
        verbose_name = 'Module'

class Function(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    function_id = models.CharField(max_length=30, blank=False, null=False)
    function_name = models.CharField(max_length=100, blank=False, null=False)
    function_order = models.IntegerField(null=True)

    def __str__(self):
        return self.function_name

    class Meta:
        db_table = 'testcase_fuction'
        managed = True
        verbose_name = 'Function'

class Region(models.Model):
    region = models.CharField(max_length=50)
    
    def __str__(self):
        return self.region

    class Meta:
        db_table = 'testcase_region'
        managed = True
        verbose_name = 'Region'

class Testcase(models.Model):

    PRIORITY_CHOICES = [
        ('p1','P1'),
        ('p2','P2'),
        ('p3','P3'),
        ('p4','P4'),
        ('p5','P5'),
    ]

    def save(self, *args, **kwargs): # save method override for testcase_id
        self.testcase_id = self.get_testcase_id()
        self.version = self.get_version()
        super(Testcase, self).save(*args, **kwargs)

    function = models.ForeignKey(Function, on_delete=models.CASCADE)
    testcase_id = models.CharField(
        max_length=100, blank=True, null=True, unique=True)
    summary = models.CharField(max_length=255, blank=False, null=False)
    precondition = models.TextField(blank=True, null=True)
    priority = models.CharField(
        max_length=5, blank=False, null=False, choices=PRIORITY_CHOICES)
    is_auto = models.BooleanField(default=False)
    is_regression = models.BooleanField(default=False)
    author = models.CharField(max_length=50, blank=False, null=False)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    visible = models.BooleanField(default=True)
    requirements = models.CharField(max_length=255, blank=True, null=True)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)
    version = models.IntegerField()

    def get_testcase_id(self):
        # service_id, function_id를 조합해 Testcase_id 자동 생성
        function_id = self.function.function_id
        module_id = self.function.module.module_id
        service_id = self.function.module.service.service_id
        try: # 현재 function에 Testcase가 있는 경우
            testcase_id = self.function.testcase_set.last().testcase_id
            serial_no = int((testcase_id.split('_')[-1][1:4]))
        except: # 처음 Testcase를 생성하는 경우
            serial_no = 0
        finally:
            # service_id_function_id_001
            print(serial_no+1)
            return '{}_{}_{}{}'.format(
                service_id, module_id, function_id, str(serial_no+1).zfill(3)
            )

    def get_version(self):
        if self.version:
            return self.version + 1
        else:
            return 1

    def __str__(self):
        return self.testcase_id

    class Meta:
        db_table = 'testcase_testcase'
        managed = True
        verbose_name = 'Testcase'

class Procedure(models.Model):

    def save(self, *args, **kwargs): # save method override for procedure_id
        self.procedure_id = self.get_procedure_id()
        super(Procedure, self).save(*args, **kwargs)

    testcase = models.ForeignKey(
        Testcase, to_field='testcase_id', on_delete=models.CASCADE)
    procedure_id = models.IntegerField(blank=True, null=True)
    procedure = models.TextField()
    expect_result = models.TextField()

    def get_procedure_id(self):
        try:
            last_procedure_id = self.testcase.procedure_set.last().procedure_id
            return last_procedure_id + 1
        except AttributeError:
            return 1

    def __str__(self):
        return self.testcase.testcase_id + '_' + str(self.procedure_id)

    class Meta:
        db_table = 'testcase_procedure'
        managed = True
        verbose_name = 'Procedure'

class Testcase_history(models.Model):
    function = models.ForeignKey(Function, on_delete=models.CASCADE)
    testcase_id = models.CharField(
        max_length=100, blank=False, null=False, unique=True)
    summary = models.CharField(max_length=255, blank=False, null=False)
    precondition = models.TextField()
    priority = models.CharField(max_length=5, blank=False, null=False)
    is_auto = models.BooleanField(default=False)
    is_regression = models.BooleanField(default=False)
    autor = models.CharField(max_length=50, blank=False, null=False)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)
    version = models.IntegerField()

    def __str__(self):
        return self.testcase_id

    class Meta:
        db_table = 'testcase_testcase_history'
        managed = True
        verbose_name = 'Testcase History'

class Procedure_history(models.Model):
    testcase = models.ForeignKey(
        Testcase_history, to_field='testcase_id', on_delete=models.CASCADE)
    procedure_id = models.IntegerField()
    procedure = models.TextField()
    expect_result = models.TextField()

    def __str__(self):
        return self.testcase.testcase_id + '_' + str(self.procedure_id)

    class Meta:
        db_table = 'testcase_procedure_history'
        managed = True
        verbose_name = 'Procedure History'
