from __future__ import absolute_import, unicode_literals
import json
from django.http.response import JsonResponse
import requests
import pandas as pd
# import pytz
from datetime import datetime, timedelta, timezone
from dateutil import parser as date_parser
from apps.dooray.models import TargetProject, UserList
from django.core.mail import send_mail
from django.template import loader
from django.http import HttpResponse
from isaac_project import env
from celery import shared_task
from apps.dooray.models import Tags


class CollectDooray:
    '''
    Dooray API를 사용해 업무를 수집하고,
    수집된 업무 담당자 별로 메일링하는 Class
    '''

    HOST = 'https://api.dooray.com/'
    FROM_USER = 'isaac@toast.com'
    POSTS = []
    USERS = []
    
    def __init__(self, project_id):
        '''init class'''
        self.session = requests.Session()
        key = 'Authorization'
        self.session.headers.update({key:env.dooray_token})
        self.prj = self.get_project(project_id)

    def get_project(self, project_id):
        '''대상 프로젝트의 객체를 가져옴'''
        url = f'project/v1/projects/{project_id}'
        return TargetProject.objects.get_or_create(
            project_id = project_id,
            project_name = self.get_json(url)['result']['code'],
            target_time = 'createdAt',
            member_key = 'toMemberIds'
        )[0]

    def get_json(self, url, params=None):
        '''JSON 응답을 사전 객체로 반환'''
        r = self.session.get(self.HOST+url, params=params)
        return json.loads(r.text)

    def get_member(self, name=None, email=None, member_id=None):
        '''이름과 member_id를 사용해 Email을 가져옴'''
        # common/v1/members?name=
        url = 'common/v1/members'
        if name:
            params={'name':name}
        elif email:
            params = {'externalEmailAddresses':email}
        else:
            return False
        member_info = self.get_json(url, params=params)
        member_list = member_info.get('result')
        if len(member_list) == 1:
            return member_list[0]
        else:
            for member in member_list:
                if member.get('id') == member_id:
                    return member
            return False

    def get_posts(self, size=100, days_range=200):
        '''대상 프로젝트를 API를 사용해 가져오는 메소드'''
        # project/v1/projects/{project_id}/posts
        url = f'project/v1/projects/{self.prj.project_id}/posts'
        page = 0
        past_dates = datetime.utcnow()-timedelta(days=days_range)
        past_dates = past_dates.replace(tzinfo=timezone.utc)
        while True:
            # st = datetime.now()
            params = {
                'size':size,
                'page':page,
                'order':'-createdAt',
                }
            r = self.get_json(url, params=params)
            posts = r.get('result')
            if posts:
                if date_parser.parse(posts[-1]['createdAt']) < past_dates:
                    break
            else:
                break
            self.POSTS+=posts
            # print(page, len(posts), datetime.now()-st)
            page+=1

    def get_to_user(self, to_user):
        ''' 조회된 모든 프로젝트의 담당자의 정보(이메일)을 받아옴'''
        to_users=[]
        for to in to_user:
            member = to.get('member')
            member_id = member.get('organizationMemberId')
            user_name = member.get('name')
            try:
                user_info = UserList.objects.get(member_id=member_id)
                email = user_info.email
            except Exception:
                user_info = self.get_member(name=user_name, member_id=member_id)
                email = user_info['externalEmailAddress']
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

    def get_tag(self, tag_id):
        try:
            return Tags.objects.get(tag_id=tag_id)
        except:
            tag_url = f'project/v1/projects/{self.prj.project_id}/tags/{tag_id}'
            retv = self.get_json(tag_url)
            tag_name=retv['result']['name'].split(':')[-1].strip().replace('.','')
            tag, _flag = Tags.objects.get_or_create(
                project=self.prj,
                tag_name=tag_name,
                tag_id=tag_id
                )
            return tag

    def update_tag(self, tag_id):
        try:
            tag = Tags.objects.get(tag_id=tag_id)
        except:
            print('no tag_id in data')
            return False
        tag_url = f'project/v1/projects/{self.prj.project_id}/tags/{tag_id}'
        retv = self.get_json(tag_url)
        tag_name=retv['result']['name'].split(':')[-1].strip().replace('.','')
        if tag_name != tag.tag_name:
            tag.tag_name = tag_name
            tag.save()
            return True
        return False


    def make_dataframe_for_issue(self):
        posts = []
        for post in self.POSTS:
            subject = post.get('subject')
            post_id = post['id']
            
            post_number = post.get('number')
            url = f'https://nhnent.dooray.com/project/posts/{post_id}'
            created = date_parser.parse(post.get('createdAt'))
            tags = ','.join([self.get_tag(tag['id']).tag_name\
                     for tag in post['tags']])
            posts.append(
                {
                    'project_id':self.prj.project_id,
                    'project_name':self.prj.project_name,
                    'post_id':post_id,
                    'subject':subject,
                    'post_number':post_number,
                    'url':url,
                    'tags':tags,
                    'created':created.isoformat(),
                }
            )
        print(len(posts))
        return HttpResponse(json.dumps(posts))
            
    def make_dataframe(self):
        '''메일링할 Task를 filtering 하여 Dataframe으로 변환'''
        _posts = []
        for post in self.POSTS:
            subject = post.get('subject')
            post_id = post['id']
            project_Id = '{}-{}'.format(self.prj.project_name, post.get('number'))
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
                   '정정아','최영준','정승원','김인선','김주영','이재희', '김명지', 
                    '염요섭', '안민형', '고준영', '김혜정']
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
    token = env.dooray_token
    project_id = '1573143134167076010' # toastcloud-qa
    c = CollectDooray(project_id)
    c.clear_data()
    c.get_posts(size=50, days_range=100)
    c.make_dataframe()
    c.get_users_dataframe()
    return c.send_mail()

@shared_task
def collect_dooray_task():
    # for shell
    token = env.dooray_token
    project_id = '1573143134167076010' # toastcloud-qa
    c = CollectDooray(project_id)
    c.clear_data()
    c.get_posts(size=50, days_range=100)
    c.make_dataframe()
    c.get_users_dataframe()
    result = c.send_mail(http=False)
    now = datetime.now().isoformat()
    print(f'[{now}]{result}')
    return True

def _issue(request):
    token = env.dooray_token
    project_id = '3000973564283604325' # tc-qa-defect-analysis
    c = CollectDooray(project_id)
    c.clear_data()
    c.get_posts(size=50)
    return c.make_dataframe_for_issue()
    
def _tag_update(request):
    token = env.dooray_token
    project_id = '3000973564283604325' # tc-qa-defect-analysis
    c = CollectDooray(project_id)
    tags = Tags.objects.all()
    for tag in tags:
        print(c.update_tag(tag.tag_id))
    return HttpResponse("OK")