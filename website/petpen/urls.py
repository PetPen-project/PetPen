"""petpen URL Configuration

    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth import views as auth_views
from rest_framework import routers, serializers, viewsets

from user import views as user_views

# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('password', 'username', 'email', 'is_staff',)

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
# router.register(r'users', UserViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^$', auth_views.LoginView.as_view(),name='main'),
    url(r'^model/', include('model.urls')),
    url(r'dataset/', include('dataset.urls')),
    url(r'^login/', auth_views.LoginView.as_view(),name='login'),
    url(r'^logout/', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^admin/', admin.site.urls),
    # url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
