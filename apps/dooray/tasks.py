from __future__ import absolute_import, unicode_literals
import json
from json.decoder import JSONDecodeError
import string
from django.http.response import JsonResponse
from numpy import delete
import requests
import pandas as pd
# import pytz
from datetime import datetime, timedelta, timezone
from dateutil import parser as date_parser
from apps.dooray.models import Issues, TargetProject, UserList, UpdateHistory, QAMember
from django.core.mail import send_mail
from django.template import loader
from django.http import HttpResponse
from isaac_project import env
from celery import shared_task
from apps.dooray.models import Tags
from django.core import serializers
from django.db.models.query import QuerySet


class CollectDooray:
    '''
    Dooray API를 사용해 업무를 수집하고,
    수집된 업무 담당자 별로 메일링하는 Classfr
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
        try: 
            response = json.loads(r.text)
        except JSONDecodeError as e:
            print(e)
            return False
        return response

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
        '''대상 프로젝트 Post를 API를 사용해 가져오는 메소드'''
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
        target_user = list(QAMember.objects.values_list('name', flat=True))
        # target_user = ['김태주']
        self.USERS=self.USERS[self.USERS.name.isin(target_user)]
        for _, user in self.USERS.iterrows():
            posts_df = self.POSTS[self.POSTS['to_user']==user.email]
            # overdue_df = posts_df[posts_df.status == 'overdue']
            posts_df = posts_df.sort_values(by=['overdue'], ascending=False)
            user_name = user['name']
            title = f'[알림]{self.prj.project_name} 미 완료 업무 List - {user_name}'
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
        '''이전 정보 초기화'''
        self.POSTS = []
        self.USERS = []

class CollectIssue(CollectDooray):

    def update_tag(self):
        updated_tags = list()

        # get all tag from project and isaac
        tags_from_dooray: pd.DataFrame = self.get_all_tags_in_project()
        tags_from_issac: QuerySet = Tags.objects.filter(project__project_id=self.prj.project_id)\
                                .values('tag_id', 'tag_name')

        # Standardization
        tags_from_issac = pd.DataFrame(tags_from_issac)
        try:
            tags_from_issac.columns = ['id', 'name']
        except:
            tags_from_issac = pd.DataFrame(columns=['id', 'name'])

        tags_from_issac: pd.DataFrame = tags_from_issac.set_index('id')

        # merge
        merged = pd.merge(tags_from_dooray, tags_from_issac, 
            how='outer', left_index=True, right_index=True, indicator=True)

        # get need to update
        need_to_update = merged[((merged['name_x']==merged['name_y'])==False)\
                                 & (merged['_merge']=='both')]
        if not need_to_update.empty:
            updated_tags += self.get_update_history(need_to_update, 'update')
            # bulk update
            update_target = Tags.objects.filter(tag_id__in=need_to_update.index.to_list())
            update_tag_list = self.get_standardized_tags(need_to_update.name_x)
            for tag in update_target:
                tag.tag_name = update_tag_list[update_tag_list.tag_id==tag.tag_id].tag_name.values.item()
            Tags.objects.bulk_update(update_tag_list, ['tag_name'])
        
        # get need to add
        need_to_add = merged[merged['_merge']=='left_only']
        if not need_to_add.empty:
            updated_tags += self.get_update_history(need_to_add, 'add')
            # bulk add
            add_tag_list = self.get_standardized_tags(need_to_add.name_x)
            Tags.objects.bulk_create([Tags(**add_tag.to_dict()) for _, add_tag in add_tag_list.iterrows()])

        # get need to delete
        need_to_delete = merged[merged['_merge']=='right_only']
        if not need_to_delete.empty:
            updated_tags += self.get_update_history(need_to_delete, 'delete')
            # delete
            delete_tag_list = self.get_standardized_tags(need_to_delete.name_y)
            Tags.objects.filter(tag_id__in=delete_tag_list.tag_id.to_list()).delete()
        
        if updated_tags:
            self.send_history_mail(updated_tags)

    def get_standardized_tags(self, target) -> pd.DataFrame:
        tag_list = pd.DataFrame(target)
        tag_list = tag_list.reset_index()
        tag_list.columns = ['tag_id', 'tag_name']
        tag_list['project'] = TargetProject.objects.get(project_id=self.prj.project_id)
        return tag_list

    def get_update_history(self, target_list:pd.DataFrame, update_type:str) -> list:
        target = target_list.name_x
        if update_type == 'delete':
            target = target_list.name_y
        target_df = self.get_standardized_tags(target)
        target_df['update_type'] = update_type
        return target_df.to_dict('records')

    def send_history_mail(self, history:list):
        html_template = '''
        <html>
            <body>
                <h3>Updated tag list</h3>
                <h4>{}</h4>
                {}
            </body>
        </html>
        '''
        recipient_list = [
            'taeju.kim@nhnsoft.com',
            # 'yeonju.lee@nhnsoft.com',
            # 'seonju.shin@nhnsoft.com',
            # 'hyejo.kwon@nhnsoft.com',
            # 'minjae.jin@nhnsoft.com',
        ]
        history_df = pd.DataFrame(history)
        history_table =  history_df.to_html()
        html = html_template.format(datetime.now().isoformat(), history_table)
        send_mail('Dooray Tag update history',
         '', self.FROM_USER, recipient_list, html_message=html)

    def get_all_tags_in_project(self) -> pd.DataFrame:
        tag_url = f'project/v1/projects/{self.prj.project_id}/tags?size=10000'
        response = self.get_json(tag_url)
        tag_list = pd.DataFrame(response.get('result'))[['id', 'name']]
        tag_list = tag_list.set_index('id')
        return tag_list
        
    def make_dataframe(self, http=True):
        posts = []
        for post in self.POSTS:
            subject = post.get('subject')
            post_id = post['id']
            post_number = post.get('number')
            try:
                milestone = post.get('milestone')['name']
            except:
                milestone = ''
            url = f'https://nhnent.dooray.com/project/posts/{post_id}'
            created = date_parser.parse(post.get('createdAt'))
            exist_issue = Issues.objects.get(project_id=self.prj.project_id, post_id=post_id)
            if exist_issue:
                exist_issue.project_id = self.prj.project_id
                exist_issue.project_name = self.prj.project_name
                exist_issue.post_id = post_id
                exist_issue.subject = subject
                exist_issue.post_number = post_number
                exist_issue.url = url
                exist_issue.milestone = milestone
                exist_issue.created = created
                exist_issue.tags.set([Tags.objects.get(tag_id=tag['id']) for tag in post['tags']])
                exist_issue.save()
                print(post_id, 'is exists')
                continue
            new_issue = Issues(
                project_id = self.prj.project_id,
                project_name = self.prj.project_name,
                post_id = post_id,
                subject = subject,
                post_number = post_number,
                url = url,
                milestone = milestone,
                created = created
                )
            new_issue.save()
            new_issue.tags.add(*[Tags.objects.get(tag_id=tag['id']) for tag in post['tags']])
            posts.append(new_issue.id)
        
        if http:
            return HttpResponse('OK')
        return 'Collect issue OK'

# toastcloud-qa project task 관리
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


# 리얼 결함 이슈 분석
@shared_task
def collect_issue():
    collect_issue_task(http=False)

def collect_issue_manual(request):
   collect_issue_task(http=True)

def collect_issue_task(http=True, project_name='all'):
    if project_name == 'all':
        target_project = ['3000973564283604325', '2570957930434228737']      
    else:
        target_project = [TargetProject.objects.get(project_name=project_name).project_id]
    # project_id = '3000973564283604325' # tc-qa-defect-analysis
    # project_id = '2570957930434228737' # tc-qa-iaas-bugs
    for project_id in target_project:
        c = CollectIssue(project_id)
        c.update_tag()
        c.clear_data()
        c.get_posts(size=50)
        history = UpdateHistory(
            remarks="update"
        )
        history.save()
        c.make_dataframe(http=http)
    if http:
        return HttpResponse('OK')
    
def _tag_update(request):
    token = env.dooray_token
    project_id = '3000973564283604325' # tc-qa-defect-analysis
    c = CollectIssue(project_id)
    c.update_tag()
    return HttpResponse("OK")
