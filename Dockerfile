FROM python:3.9-slim-buster

# update and install libs
RUN apt-get update && \
apt-get install python3-dev default-libmysqlclient-dev \
 build-essential libbz2-dev liblzma-dev -y

# make directory and copy files
RUN mkdir /isaac
WORKDIR /isaac

# pip upgrade and install poetry
RUN pip install --upgrade pip
RUN pip install poetry

# install packages via poetry
COPY poetry.lock /isaac/poetry.lock
COPY pyproject.toml /isaac/pyproject.toml
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction

# Add Files
ADD . /isaac/

# execute docker-entrypoint.sh
CMD [ "sh", "docker-entrypoint.sh" ]
