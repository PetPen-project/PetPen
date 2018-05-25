from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

app_natme = 'model'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<project_id>[0-9]+)/$', views.project_detail, name='project_detail'),
    url(r'^history_detail/$', views.history_detail, name='history_detail'),
    url(r'^(?P<project_id>[0-9]+)/history/$', login_required(views.HistoryView.as_view()), name='project_history'),
    url(r'^(?P<project_id>[0-9]+)/prediction/$', login_required(views.PredictView.as_view()), name='prediction'),
    url(r'^api/parse/$',views.api, name='api'),
    url(r'^api/plot/$',views.plot_api, name='plot_api'),
    url(r'^editor/$',views.manage_nodered, name='manage_editor'),
    url(r'^api/backend/$', views.backend_api, name='backend_api'),
    url(r'^images/',views.img_api,name='images'),
    url(r'^images/(?P<pid>)',views.img_api,name='images'),
] + \
    format_suffix_patterns([
        # url(r'^api/$', views.project_list),
        url(r'^api/$', views.NN_model_list.as_view()),
        url(r'^api/(?P<pk>[0-9]+)/$', views.NN_model_detail.as_view()),
        ])

# urlpatterns = format_suffix_patterns(urlpatterns)
