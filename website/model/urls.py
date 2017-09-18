from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # ex: /polls/5/
    url(r'^(?P<dataset_id>[0-9]+)/$', views.dataset_detail, name='dataset_detail'),
    url(r'^results/$', views.results, name='results'),
    url(r'^api/parse/$',views.api, name='api'),
    url(r'^api/plot/$',views.plot_api, name='plot_api'),
    url(r'build/', views.build_model, name='build'),
    url(r'^configure/', views.configure, name='configure')
]
