import pytest
from django.urls import reverse, resolve
from django.test import TestCase, client


def test_logout_view(client):
    resp = client.get(
        reverse('logout')
    )
    assert resolve(resp.url).view_name == 'login'

def test_login_view(client):
    resp = client.get(
        reverse('login')
    )
    assert 'login' in 'resp.content'

# @pytest.mark.django_db
# def test_testcase_view(client):
#     resp = client.get(
#         reverse('testcase_main')
#     )
#     assert resolve(resp.url).view_name == 'testcase_main'
    