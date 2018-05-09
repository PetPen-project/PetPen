from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_natme = 'model'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<project_id>[0-9]+)/$', views.project_detail, name='project_detail'),
    url(r'^(?P<project_id>[0-9]+)/history/$', login_required(views.HistoryView.as_view()), name='project_history'),
    url(r'^(?P<project_id>[0-9]+)/(?P<history_path>[\d]+_[\d]+)/predict/$', views.predict, name='predict'),
    url(r'^api/parse/$',views.api, name='api'),
    url(r'^api/plot/$',views.plot_api, name='plot_api'),
    url(r'^editor/$',views.manage_nodered, name='manage_editor'),
    url(r'^api/backend/$', views.backend_api, name='backend_api'),
    url(r'^images/',views.img_api,name='images'),
    url(r'^images/(?P<pid>)',views.img_api,name='images'),
] + \
    format_suffix_patterns([
        url(r'^api/$', views.project_list),
        url(r'^api/(?P<pk>[0-9]+)/$', views.NN_modelDetail.as_view()),
        ])

# urlpatterns = format_suffix_patterns(urlpatterns)
