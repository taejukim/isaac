FROM python:3.9-slim-buster

# update and install libs
RUN apt-get update && \
apt-get install python3-dev default-libmysqlclient-dev build-essential -y
    
# make directory and copy files
RUN mkdir /isaac
WORKDIR /isaac

# pip upgrade and install pipenv
RUN pip install --upgrade pip
RUN pip install pipenv

# install packages via pipenv
COPY Pipfile /isaac/Pipfile
COPY Pipfile.lock /isaac/Pipfile.lock
RUN pipenv install --system

# Add Files
ADD . /isaac/

# execute docker-entrypoint.sh
CMD [ "sh", "docker-entrypoint.sh" ]
