from __future__ import absolute_import, unicode_literals
import json
import requests
import pandas as pd
# import pytz
from datetime import datetime, timedelta, timezone
from dateutil import parser as date_parser
from apps.dooray.models import UserList
from django.core.mail import send_mail
from django.template import loader
from django.http import HttpResponse

from celery import shared_task


class CollectDooray(requests.Session):
    '''
    Dooray API를 사용해 업무를 수집하고,
    수집된 업무 담당자 별로 메일링하는 Class
    '''

    HOST = 'https://api.dooray.com/'
    FROM_USER = 'isaac@toast.com'
    POSTS = []
    USERS = []

    def set_header(self, token):
        '''인증 토큰 헤더에 저장'''
        key = 'Authorization'
        self.headers.update({key:token})

    def get_json(self, url, params=None):
        '''JSON 응답을 사전 객체로 반환'''
        r = self.get(self.HOST+url, params=params)
        return json.loads(r.text)

    def get_project_info(self, project_id):
        '''대상 프로젝트의 이름을 가져옴'''
        url = f'project/v1/projects/{project_id}'
        r = self.get_json(url)
        self.project_name = r['result']['code']

    def get_member(self, name, member_id=None):
        '''이름과 member_id를 사용해 Email을 가져옴'''
        # common/v1/members?name=
        url = 'common/v1/members'
        params={'name':name}
        member_info = self.get_json(url, params=params)
        member_list = member_info.get('result')
        if len(member_list) == 1:
            return member_list[0]
        else:
            for member in member_list:
                if member.get('id') == member_id:
                    return member
            return False

    def get_posts(self, project_id, size=100, days_range=100):
        '''대상 프로젝트를 API를 사용해 가져오는 메소드'''
        # project/v1/projects/{project_id}/posts
        self.get_project_info(project_id)
        url = f'project/v1/projects/{project_id}/posts'
        page = 0
        past_dates = datetime.utcnow()-timedelta(days=days_range)
        past_dates = past_dates.replace(tzinfo=timezone.utc)
        while True:
            # st = datetime.now()
            _params = {
                'size':size,
                'page':page,
                'order':'-createdAt',
                }
            r = self.get_json(url, params=_params)
            _posts = r.get('result')
            if date_parser.parse(_posts[-1]['createdAt']) < past_dates:
                break
            self.POSTS+=_posts
            # print(page, len(posts), datetime.now()-st)
            page+=1

    def get_to_user(self, to_user):
        ''' 조회된 모든 프로젝트의 담당자의 정보(이메일)을 받아옴'''
        to_users=[]
        for to in to_user:
            _member = to.get('member')
            member_id = _member.get('organizationMemberId')
            user_name = _member.get('name')
            try:
                _user_info = UserList.objects.get(member_id=member_id)
                email = _user_info.email
            except Exception:
                _user_info = self.get_member(name=user_name, member_id=member_id)
                email = _user_info['externalEmailAddress']
                new_member = UserList(
                    name=user_name,
                    member_id=member_id,
                    email=email
                )
                new_member.save()
            to_users.append({
                'member_id':member_id,
                'user_name':user_name,
                'email':email
            })
            self.USERS.append([
                user_name, 
                email
                ])
        return to_users

    def get_users_dataframe(self):
        '''조회된 모든 User의 중복 제거'''
        self.USERS = pd.DataFrame(self.USERS).drop_duplicates()
        self.USERS.columns = ['name', 'email']

    def make_dataframe(self):
        '''메일링할 Task를 filtering 하여 Dataframe으로 변환'''
        _posts = []
        for post in self.POSTS:
            subject = post.get('subject')
            post_id = post['id']
            project_Id = '{}-{}'.format(self.project_name, post.get('number'))
            url = f'https://nhnent.dooray.com/project/posts/{post_id}'
            created = date_parser.parse(post.get('createdAt'))
            status = post.get('workflowClass')
            if status == 'closed':
                continue
            duedate = post.get('dueDate')
            overdays = 0
            if duedate:
                # 지연 여부 판단
                duedate = date_parser.parse(duedate)
                if duedate < datetime.now().replace(tzinfo=timezone.utc):
                    diff = datetime.now().replace(tzinfo=timezone.utc) - duedate
                    overdays= int(diff.total_seconds()/86400) # 1day = 86400 seconds
                    overdue = True
                    # print(subject)
                else:
                    overdue = False
            else:
                overdue = False
            # print(status, subject)
            try:
                to_users = self.get_to_user(post['users']['to'])
            except Exception:
                continue
            for to_user in to_users:
                _posts.append({
                    'to_user':to_user.get('email'),
                    'url':url,
                    'subject':subject,
                    'project_id':project_Id,
                    'status':status,
                    'created':created,
                    'duedate':duedate,
                    'overdue':overdue,
                    'overdays':overdays,
                })
        self.POSTS = pd.DataFrame(_posts)

    def send_mail(self, http=True):
        '''각 target user 별 메일 전송'''
        # To-do User table에서 동적으로 가져오기
        target_user = ['신선주','이연주','김태주','장선향','정연주','권혜조','김동원',
                   '정정아','최영준','정승원','김인선','김주영','이재희', '김명지', '염요섭']
        # target_user = ['김태주']
        self.USERS=self.USERS[self.USERS.name.isin(target_user)]
        for _, user in self.USERS.iterrows():
            posts_df = self.POSTS[self.POSTS['to_user']==user.email]
            # overdue_df = posts_df[posts_df.status == 'overdue']
            posts_df = posts_df.sort_values(by=['overdue'], ascending=False)
            user_name = user['name']
            title = f'[알림]{self.project_name} 미 완료 업무 List - {user_name}'
            template = loader.get_template('mail_template.html')
            context = {
                'total_count':len(posts_df),
                'posts':posts_df,
                'user_name':user_name,
            }
            html =template.render(context)
            # print(user.email)
            send_mail(title, '', self.FROM_USER, [user.email], html_message=html)
            # send_mail(title, '', self.FROM_USER, ['taeju.kim@nhntoast.com'], html_message=html)
        if http:
            return HttpResponse('Send Mail OK')
        return 'Send Mail OK'
    
    def clear_data(self):
        '''이전 정보 삭제'''
        self.POSTS = []
        self.USERS = []


def _main(request):
    token = 'dooray-api 4CIgg_y2QTmlnHjBc-6Ifw'
    project_id = '1573143134167076010' # toastcloud-qa
    c = CollectDooray()
    c.clear_data()
    c.set_header(token)
    c.get_posts(project_id=project_id, size=50, days_range=100)
    c.make_dataframe()
    c.get_users_dataframe()
    return c.send_mail()


@shared_task
def collect_dooray_task():
    # for shell
    token = 'dooray-api 4CIgg_y2QTmlnHjBc-6Ifw'
    project_id = '1573143134167076010' # toastcloud-qa
    c = CollectDooray()
    c.clear_data()
    c.set_header(token)
    c.get_posts(project_id=project_id, size=50, days_range=100)
    c.make_dataframe()
    c.get_users_dataframe()
    result = c.send_mail(http=False)
    now = datetime.now().isoformat()
    print(f'[{now}]{result}')
    return True
