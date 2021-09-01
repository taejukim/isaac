from accounts.views import get_session
from apps.dooray.tasks import *
from apps.dooray.models import Issues, TargetProject, Tags, UpdateHistory
from django.http.response import JsonResponse, HttpResponse
import pandas as pd

from datetime import datetime, timedelta, timezone
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

def get_issues(request):
    if request.GET.get('update')=='true':
        print('start_update')
        collect_issue_task(http=False)
    _issues = []
    issues = Issues.objects.all()
    for issue in issues:
        post_id = issue.post_id
        project_name = issue.project_name
        task_id = project_name+"/"+str(issue.post_number)
        subject = issue.subject
        url = issue.url
        milestone = issue.milestone
        created_at = issue.created
        service=grade=environment=defect_cause=\
             defect_cause_detail=non_detect_reason=non_detect_reason_detail=''
        # tag_type : 대분류
        # tag_class  : 중분류
        # tag_name : 소분류
        for tag in issue.tags.all():
            if tag.tag_type == 'service':
                service=tag.tag_name
            if tag.tag_type == 'grade':
                grade=tag.tag_name
            if tag.tag_type == 'environment':
                environment=tag.tag_name
            if tag.tag_type == '결함 원인':
                defect_cause = tag.tag_class
                defect_cause_detail = tag.tag_name
            if tag.tag_type == '미검출 사유':
                non_detect_reason = tag.tag_class
                non_detect_reason_detail = tag.tag_name
        _issues.append(
            {
                'post_id':post_id,
                'proect_name':project_name,
                'task_id':task_id,
                'subject':subject,
                'service':service,
                'url':url,
                'milestone':milestone,
                'grade':grade,
                'environment':environment,
                'defect_cause':defect_cause,
                'defect_cause_detail':defect_cause_detail,
                'non_detect_reason':non_detect_reason,
                'non_detect_reason_detail':non_detect_reason_detail,
                'created_at':created_at.isoformat()
            }
        )
    if request.GET.get('export') == 'excel':
        file_name = str(datetime.strftime(datetime.now(),'real_defect_%y%m%d%H%M%S.xlsx'))
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(file_name)
        df = pd.DataFrame(_issues)
        writer = pd.ExcelWriter(response, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='issues')  # send df to writer
        worksheet = writer.sheets['issues']  # pull worksheet object
        for idx, col in enumerate(df):  # loop through all columns
            series = df[col]
            max_len = max((
                series.astype(str).map(len).max(),  # len of largest item
                len(str(series.name))  # len of column name/header
                )) + 1  # adding a little extra space
            max_len = 50 if max_len > 50 else max_len
            worksheet.set_column(idx+1, idx+1, max_len)  # set column width
        writer.save()
        # df.to_excel(response)
        return response
    update_date = UpdateHistory.objects.all().last()
    update_date_kst=update_date.updated + timedelta(hours=9)
    return JsonResponse({
        "last_update_datetime":update_date_kst.strftime('%Y-%m-%d %H:%M:%S'),
        "data":_issues,
        })