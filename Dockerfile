FROM tensorflow/tensorflow:latest-gpu

RUN pip install keras django bokeh
RUN pip install djangorestframework
RUN pip install django-background-tasks

RUN mkdir -p /source
ADD . /source/

RUN apt-get update && apt-get install -y nodejs npm

WORKDIR /source/website
ENTRYPOINT ["python", "manage.py", "runserver"]
