import requests
from bs4 import BeautifulSoup as bs

def check_sso(emp_no, pw):
    '''
    emp_no : Employee number
    '''

    url = 'https://sso.nhnent.com/siteminderagent/forms/login.fcc'
    data = {
    'target': '-SM-http://whatsup.nhnent.com/settings/im/selfservice/myInfo_connect',
    'smauthreason': '0',
    'smagentname': 'whatsup.nhnent.com',
    'USER': emp_no,
    'PASSWORD': pw
    }

    resp = requests.post(url, data)
    soup = bs(resp.text, 'html.parser')
    
    form_tag = soup.find('form', {'id':'myInfoForm'})
    if not form_tag:
        return False

    kr_name = form_tag.find('input', {'id':'empNm'}).attrs.get('value')
    email = form_tag.find('dd', {'class':'mail'}).text
    department = form_tag.find('dd').text
    title, position = form_tag.find_all('dd')[1].text.split(' / ')
    dept_code = form_tag.find('input', {'id':'empNm'}).attrs.get ('value')
    img_src = form_tag.find('img').attrs.get('src')

    return {
        'kr_name':kr_name,
        'email':email,
        'department':department,
        'title':title,
        'position':position,
        'dept_code':dept_code,
        'img_src':img_src
    }
