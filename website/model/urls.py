from django.conf.urls import url

from . import views

app_natme = 'model'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<project_id>[0-9]+)/$', views.project_detail, name='project_detail'),
    url(r'^history_detail/$', views.history_detail, name='history_detail'),
    url(r'^(?P<project_id>[0-9]+)/history/$', views.HistoryView.as_view(), name='project_history'),
    url(r'^api/parse/$',views.api, name='api'),
    url(r'^api/plot/$',views.plot_api, name='plot_api'),
    url(r'^editor/$',views.manage_nodered, name='manage_editor'),
    url(r'^api/backend/$', views.backend_api, name='backend_api')
]
