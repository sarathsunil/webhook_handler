FROM python:2.7-slim
MAINTAINER Sarath Sunil <sarathsunil@yahoo.com>
RUN echo "deb http://archive.ubuntu.com/ubuntu/ bionic main universe" > /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -f -y --allow-unauthenticated gnupg2
RUN apt-get install -f -y --allow-unauthenticated apt-file
RUN apt-file update
RUN apt-get install -f -y --allow-unauthenticated software-properties-common
RUN apt-get install -f -qq -y --allow-unauthenticated build-essential libpq-dev --fix-missing --no-install-recommends
RUN apt-get install -f -qq -y --allow-unauthenticated python python-dev python-distribute python-pip --fix-missing --no-install-recommends
ENV INSTALL_PATH /dockerdemo
RUN mkdir -p $INSTALL_PATH

WORKDIR $INSTALL_PATH

COPY requirements.txt requirements.txt
RUN pip uninstall psycopg2
RUN pip install --no-binary :all: psycopg2
RUN pip install -r requirements.txt

COPY . .

#VOLUME ["static"]
CMD uwsgi --socket 127.0.0.1:8000 --module webhook_handler --callab application
