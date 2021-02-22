from django.shortcuts import render
from apps.dooray.tasks import CollectDooray


# 사용자 입력 (Email, 이름)
# 
# 정해진 Project의
class CollectGRM(CollectDooray):

    def tags(self):
        pass


