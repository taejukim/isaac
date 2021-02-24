from django.shortcuts import render
from apps.dooray.tasks import CollectDooray
from accounts.views import get_session
from apps.dooray.models import TargetProject, Tags
from django.http.response import JsonResponse, HttpResponse
import pandas as pd

from datetime import datetime, timedelta
from dateutil import parser

class CollectGRM(CollectDooray):

    def __init__(self, email):
        super().__init__()
        retv = self.get_member(email=email)
        self.user_id = retv.get('id')

    def search_tasks(self):
        tasks = list()
        target_projects = TargetProject.objects.all()
        for project in target_projects:
            url = f'project/v1/projects/{project.project_id}/posts'
            params = {
                'page':0,
                'szie':100,
                project.member_key:self.user_id,
                'order':'-createAt' 
            }
            retv = self.get_json(url, params=params)
            print(project.project_name, project.member_key, project.target_time, len(retv))
            for task in retv['result']:
                tags = [self.get_tag(tag['id'], project).tag_name\
                     for tag in task['tags']]
                if not self.is_target(task[project.target_time]):
                    # print(task[project.target_time], self.is_target(task[project.target_time]))
                    continue
                tasks.append({
                    'project':project.project_name,
                    'target_time':task[project.target_time],
                    'workflow':task['workflow']['name'],
                    'tags':tags,
                    'task':task['subject']
                    })
        return tasks

    def is_target(self, target_time):
        return (parser.isoparse(target_time)+timedelta(hours=9)).month\
             == datetime.today().month

    def get_tag(self, tag_id, project):
        try:
            return Tags.objects.get(tag_id=tag_id)
        except:
            tag_url = f'project/v1/projects/{project.project_id}/tags/{tag_id}'
            retv = self.get_json(tag_url)
            tag_name=retv['result']['name'].split(':')[-1].strip().replace('.','')
            tag, _flag = Tags.objects.get_or_create(
                project=project,
                tag_name=tag_name,
                tag_id=tag_id
                )
            return tag

def grm(request):
    session = get_session(request)
    grm = CollectGRM(session['email'])
    tasks = grm.search_tasks()
    result = {
        'result' : tasks
    }
    tags_esm = Tags.objects.filter(esm_code__isnull=False)
    grm_result = []
    for tag in tags_esm:
        complets = 0
        working = 0
        for task in tasks:
            if tag.tag_name in task['tags']:
                if task['workflow'] == '완료':
                    complets += 1
                else:
                    working += 1
        grm_result.append({
            'esm_code':tag.esm_code,
            'esm_name':tag.esm_name,
            'tag_name':tag.tag_name,
            'project':tag.project.project_name,
            'complets':complets,
            'working':working
        })
    grm_result = pd.DataFrame(grm_result).to_html()
    tasks = pd.DataFrame(tasks).to_html()
    return HttpResponse(grm_result + tasks)
