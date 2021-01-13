FROM python:3.9-slim-buster
LABEL maintainer="taeju.kim@nhntoast.com"

RUN apt-get update && \
    apt-get install python3-dev default-libmysqlclient-dev build-essential cron -y

RUN pip install --upgrade pip
RUN pip install pipenv

RUN mkdir /isaac
WORKDIR /isaac

COPY Pipfile /isaac/Pipfile
COPY Pipfile.lock /isaac/Pipfile.lock

RUN pipenv install --system

RUN crontab <<< "# new crontab"
RUN python manage.py crontab add
RUN python manage.py crontab show

ADD . /isaac/

CMD [ "sh", "docker-entrypoint.sh" ]
