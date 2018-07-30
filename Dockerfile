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
ENV INSTALL_PATH /home/ubuntu/webhook_handler
#ENV FLASK_APP webhook_handler.py
#ENTRYPOINT ["python", "-m", "flask", "run", "--host=0.0.0.0"]
RUN mkdir -p $INSTALL_PATH
WORKDIR $INSTALL_PATH
EXPOSE 9990
COPY requirements.txt requirements.txt
#RUN pip uninstall psycopg2
#RUN pip install --no-binary :all: psycopg2
RUN pip install -r requirements.txt

COPY . .

VOLUME ["docker_static"]
CMD  uwsgi --http 0.0.0.0:9990 --ini uwsgi.ini
