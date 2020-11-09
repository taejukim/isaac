FROM python:3.8.5

RUN mkdir /isaac
WORKDIR /isaac

ADD req.txt /isaac/

RUN pip install --upgrade pip
RUN pip install -r req.txt

ADD . /isaac/

RUN python manage.py makemigrations
RUN python manage.py migrate
