FROM tensorflow/tensorflow:latest-gpu

RUN pip install keras django bokeh
RUN pip install djangorestframework
RUN pip install django-background-tasks

RUN mkdir -p /source
ADD . /source/

WORKDIR /source/website
ENTRYPOINT ["python", "manage.py", "runserver"]
