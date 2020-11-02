from django.shortcuts import render
from django.http import HttpResponse

from accounts.login_session import login_required

@login_required
def main(requests):
    return HttpResponse('project main')