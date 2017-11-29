from django.conf.urls import url

from . import views

app_name = 'dataset'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<dataset_id>[0-9]+)/$', views.dataset_detail, name='dataset_detail'),
]
