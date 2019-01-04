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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth import views as auth_views
from rest_framework import routers, serializers, viewsets
from .views import *
from user.views import UserCreateView, activate

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
    url(r'^$', main,name='main'),
    url(r'^examples/$', examples,name='examples'),
    url(r'^examples/dataset/$', examples_dataset,name='examples_dataset'),
    url(r'^features/$', feature_list,name='features'),
    url(r'^model/', include(('model.urls','model'),namespace='model')),
    url(r'^dataset/', include(('dataset.urls','dataset'),namespace='dataset')),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^signup/', UserCreateView.as_view(),name='user_create'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', activate, name='activate'),
    # url(r'^', include(router.urls)),
    url(r'^api-auth/', include(('rest_framework.urls','rest_framework'), namespace='rest_framework')),
# ]
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
