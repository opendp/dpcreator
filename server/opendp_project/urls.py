"""opendp_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework import routers, serializers

from opendp_apps.user.models import DataverseUser
from opendp_apps.user.views import UserViewSet, SessionViewSet
from opendp_project import settings
from opendp_project.views import home_view


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DataverseUser
        fields = ['url', 'username', 'email', 'is_staff']


router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'sessions', SessionViewSet)

urlpatterns = [
    url(r'^$', home_view),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),    
    path('api/', include(router.urls)),

    # Putting all vue-related views under "ui/" for now to separate from the api.
    path('ui/', TemplateView.as_view(template_name='index.html'), name='index'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT, kwargs={'show_indexes': True})
