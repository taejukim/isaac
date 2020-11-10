FROM python:3.8-slim-buster
LABEL maintainer="taeju.kim@nhntoast.com"
RUN pip install pipenv

RUN mkdir /isaac
WORKDIR /isaac

COPY Pipfile /isaac/Pipfile
COPY Pipfile.lock /isaac/Pipfile.lock

RUN pipenv install --system

ADD . /isaac/
