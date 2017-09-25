from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^results/$', views.results, name='results'),
    url(r'^api/parse/$',views.api, name='api'),
    url(r'^api/plot/$',views.plot_api, name='plot_api'),
    # url(r'^configure/', views.configure, name='configure')
]
