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

class CollectDooray(requests.Session):

    HOST = 'https://api.dooray.com/'
    FROM_USER = 'qa_task@nhnsoft.com'
    POSTS = []
    USERS = []

    def set_header(self, token):
        key = 'Authorization'
        self.headers.update({key:token})

    def get_json(self, url, params=None):
        r = self.get(self.HOST+url, params=params)
        return json.loads(r.text)

    def get_project_info(self, project_id):
        url = f'project/v1/projects/{project_id}'
        r = self.get_json(url)
        self.project_name = r['result']['code']

    def get_member(self, name, member_id=None):
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
        self.USERS = pd.DataFrame(self.USERS).drop_duplicates()
        self.USERS.columns = ['name', 'email']

    def make_dataframe(self):
        _posts = []
        for post in self.POSTS:
            subject = post.get('subject')
            print(subject)
            post_id = post['id']
            project_Id = '{}-{}'.format(self.project_name, post.get('number'))
            url = f'https://nhnent.dooray.com/project/posts/{post_id}'
            created = date_parser.parse(post.get('createdAt'))
            status = post.get('workflowClass')
            if status == 'closed':
                continue
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
                    'created':created
                })
        self.POSTS = pd.DataFrame(_posts)

    def send_mail(self):
        test_user = ['신선주', '이연주', '김태주']
        # test_user = ['김태주','김명지']
        self.USERS=self.USERS[self.USERS.name.isin(test_user)]
        for _, user in self.USERS.iterrows():
            posts_df = self.POSTS[self.POSTS['to_user']==user.email]
            user_name = user['name']
            title = f'[알림]{self.project_name} 미 완료 업무 List - {user_name}'
            template = loader.get_template('mail_template.html')
            context = {
                'posts':posts_df,
                'user_name':user_name,
            }
            html =template.render(context)
            send_mail(title, '', self.FROM_USER, [user.email], html_message=html)
            # send_mail(title, '', self.FROM_USER, ['taeju.kim@nhntoast.com'], html_message=html)
        return HttpResponse('Send Mail OK')
        

def main(request):
    token = 'dooray-api 4CIgg_y2QTmlnHjBc-6Ifw'
    project_id = '1573143134167076010' # toastcloud-qa
    c = CollectDooray()
    c.set_header(token)
    c.get_posts(project_id=project_id, size=50, days_range=100)
    c.make_dataframe()
    c.get_users_dataframe()
    return c.send_mail()

        
if __name__ == "__main__":
        
    token = 'dooray-api 4CIgg_y2QTmlnHjBc-6Ifw'
    project_id = '1573143134167076010' # toastcloud-qa

    c = CollectDooray()
    c.set_header(token)
    c.get_posts(project_id=project_id, size=50, days_range=10)
    c.make_dataframe()
    c.get_users_dataframe()
    c.send_mail()
    
    # c.get_posts
    # st = datetime.now()
    # print('total ', datetime.now()-st)
    # print(posts[-1])
    # # https://nhnent.dooray.com/project/posts/2895869329518870288
    # url = f'https://nhnent.dooray.com/project/posts/{post_id}'
    # subject = post.get('subject')
    # created = date_parser.parse(post.get('createdAt'))
    # _to_users = post.get('to')
    # to_users = []
    # for to in _to_users:
    #     _member = to.get('member')
    #     member_id = _member.get('organizationMemberId')
    #     user_name = _member.get('name')
    #     _user_info = c.get_member(name=user_name, member_id=member_id)
    #     to_users.append({
    #         'member_id':member_id,
    #         'user_name':user_name,
    #         'email':_user_info['result']['externalEmailAddress']
    #     })