from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<dataset_id>[0-9]+)/$', views.dataset_detail, name='dataset_detail'),
]
