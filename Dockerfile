#FROM tensorflow/tensorflow:latest-gpu-py3

#RUN pip install keras 

FROM python:3.7.1
ENV PYTHONUNBUFFERED 1
#RUN pip install django bokeh docker
#RUN pip install djangorestframework redis
#RUN pip install django-background-tasks
#RUN pip install django-bower python-nvd3
#RUN pip install django-nvd3 pandas
#RUN pip install libsass django-compressor django-sass-processor

RUN mkdir -p /source
WORKDIR /source
COPY requirements.txt /source/
RUN pip install -r requirements.txt
COPY . /source/
RUN mkdir -p storage

#WORKDIR /source/website
#ENTRYPOINT ["python", "manage.py", "runserver"]

EXPOSE 8000
