from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'dataset'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    # url(r'^(?P<dataset_id>[0-9]+)/$', views.dataset_detail, name='dataset_detail'),
    url(r'^(?P<dataset_id>[0-9]+)/$', login_required(views.DatasetDetailView.as_view()), name='dataset_detail'),
    url(r'^(?P<dataset_id>[0-9]+)/edit/$', login_required(views.DatasetUpdateView.as_view()), name='dataset_update'),
]
