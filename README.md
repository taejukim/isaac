# ISAAC
### ISAAC; Integrated Software Assessment And Collaboration

**ISAAC**는 Test Project 단위로 Test를 수행/관리하고 수행되는 Test case의 관리를 도와주는 서비스 입니다.

## Deploy
------

1) `docker`와 `docker-compose`를 설치 합니다.
2) 해당 Repository를 Clone 합니다.
3) `docker-compose`를 사용하여 docker image를 Build 합니다.
    ```shell
    root/path/to/isaac $ docker-compose up --build
    ```

## 개발환경 세팅
-----

 * Python 설치
    * Anaconda 설치 권장(`환경변수 path 등록 필요`)
    * Anaconda : https://repo.anaconda.com/archive/Anaconda3-2020.07-Windows-x86_64.exe
 * pipenv 설치
    ```bash
    pip install pipenv
    ```
 * Repository clone
    ```bash
    git clone https://github.com/taejukim/isaac.git
    ```
 * pipenv shell & package install
    ```bash
    $ cd isaac

    isaac$ pipenv --python 3.8

    isaac$ pipenv shell

    (isaac)isaac$ pipenv install

    ```


## File Tree
-----

```bash
.
├── Dockerfile # Docker file
├── docker-compose.yml # docker-compose 파일
├── Pipfile # python 패키지 의존성 파일
├── Pipfile.lock # python 패키지 의존성 파일 lock
├── README.md # README
├── accounts  # SSO 로그인 및 세션 관련 App
│   ├── admin.py
│   ├── apps.py
│   ├── login_session.py
│   ├── migrations
│   ├── models.py
│   ├── sso.py
│   ├── tests.py
│   └── views.py
├── apps
│   ├── problem # 문제점 관리 App
│   │   ├── admin.py # django Admin page 정의
│   │   ├── apps.py
│   │   ├── models.py # django model 정의 (DB Scheme)
│   │   ├── templates # Temlpates 폴더 (html)
│   │   ├── tests.py 
│   │   ├── urls.py # App url 정의
│   │   └── views.py # View 정의
│   ├── project # Project 관리 App
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── templates
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── testcase # Testcase 관리 App
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── templates
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   └── testing # Test 수행 App
│       ├── admin.py
│       ├── apps.py
│       ├── models.py
│       ├── templates
│       ├── tests.py
│       ├── urls.py
│       └── views.py
├── config 
│   └── nginx # Nginx 설정 파일
├── docu # 문서
│   └── prototype
├── isaac_project # 프로젝트 설정 및 Main URL
│   ├── admin.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   └── wsgi.py
├── manage.py # Django 실행 파일
├── static # 정적 파일 폴더
│   ├── admin
│   ├── favicon.ico
│   ├── files
│   └── img
└── templates # 메인 Templates
    ├── base.html
    └── login.html
```


Specification
-----
- python 3.9
- django 3.1.3
- gunicorn 20.0.4
- nginx
- bootstrap4
