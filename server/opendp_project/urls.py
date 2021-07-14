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
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include
from django.views.generic import TemplateView, RedirectView
from rest_framework import routers, serializers

from opendp_apps.dataset.views import DepositorSetupViewSet, DataSetInfoViewSet
from opendp_apps.dataverses.urls import router as dataverse_router
from opendp_apps.dataverses.views.dataverse_file_view import DataverseFileView
from opendp_apps.dataverses.views.dataverse_handoff_view import DataverseHandoffView
from opendp_apps.dataverses.views.dataverse_user_view import DataverseUserView
from opendp_apps.terms_of_access.views import TermsOfAccessViewSet, TermsOfAccessAgreementViewSet
from opendp_apps.user.models import OpenDPUser
from opendp_apps.user.views import GoogleLogin, OpenDPRegister
from opendp_apps.user.views import UserViewSet

admin.site.site_header = 'OpenDP App Admin Panel'
admin.site.site_title = 'OpenDP App Admin Panel'


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OpenDPUser
        fields = ['url', 'username', 'email', 'is_staff']


router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'terms-of-access', TermsOfAccessViewSet)
router.register(r'terms-of-access-agreement', TermsOfAccessAgreementViewSet)
router.register(r'dataset-info', DataSetInfoViewSet)
router.register(r'test', TermsOfAccessAgreementViewSet)
router.register(r'dv-user', DataverseUserView, basename='dv-user')
router.register(r'deposit', DepositorSetupViewSet, basename='deposit')
router.register(r'dv-handoff', DataverseHandoffView, basename='dv-handoff')
router.register(r'dv-file', DataverseFileView, basename='dv-file')
router.registry.extend(dataverse_router.registry)

urlpatterns = [
    path('async_messages/', include('opendp_apps.async_messages.urls')),

    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include(router.urls)),
    # For testing
    path('dv-mock-api/', include('opendp_apps.dataverses.mock_urls')),

    url(r'^user-details/$',
      TemplateView.as_view(template_name="user_details.html"),
      name='user-details'),
    url(r'^rest-auth/', include('dj_rest_auth.urls')),
    url(r'^rest-auth/registration/', OpenDPRegister.as_view(), name='opendp-register'),
    url(r'^rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    url(r'^account/', include('allauth.urls')),
    url(r'^accounts/profile/$', RedirectView.as_view(url='/', permanent=True), name='profile-redirect'),
    url(r'^rest-auth/google/$', GoogleLogin.as_view(), name='google-login'),
    # Putting all vue-related views under "ui/" for now to separate from the api.
    url(r'^.*$', TemplateView.as_view(template_name="index.html"), name='vue-home'),
    ]

if settings.USE_DEV_STATIC_SERVER:
    #print('Adding static url!!')
    print(f'Serving directory "{settings.STATIC_ROOT}" from url "{settings.STATIC_URL}"')
    urlpatterns += staticfiles_urlpatterns()
    #urlpatterns += static(settings.STATIC_URL,
    #                      document_root=settings.STATIC_ROOT,
    #                      kwargs={'show_indexes': True})
